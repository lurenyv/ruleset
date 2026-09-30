#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把仓库里 mihomo classical/ipcidr 的 rule-provider yaml 编译成 sing-box SRS。

背景：仓库 7 份规则集是唯一事实来源（SSOT），mihomo 客户端直接用 yaml 的
`format: yaml` 拉，sing-box 客户端用这里的 `.srs` 二进制拉。两份内容要保持一致，
所以 SRS 不从 yaml 直接复制条目，而是由本脚本读同一份 yaml 生成。

用法::

    python scripts/gen-singbox-srs.py            # 编译全部 7 份到 singbox/
    python scripts/gen-singbox-srs.py --check    # 只校验，不写文件（CI 用）
    python scripts/gen-singbox-srs.py --sing-box /path/to/sing-box

产物在 ``singbox/<file>.srs``。``singbox/`` 目录加进 git，push 后 jsDelivr 才会
提供 ``https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/<file>.srs``。

为什么不是 GitHub Actions 跑：sing-box 官方没有直接可复用的 compile action，
且产物小（每份几 KB~几百 KB），本地编一次 push 就行。
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    import yaml
except ImportError:
    sys.exit("需要 pyyaml: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "singbox")

# 与 README / JS override / 独立 yaml 保持一致。key = 输出文件名（不含扩展名），
# value = (源 yaml, 该集预计的条目类别)。仅用于在找不到某类条目时给出更清楚的信息。
FILES = {
    "important-domain": ("important-domain.yaml", "domain"),
    "important-ip":     ("important-ip.yaml",     "ip"),
    "btc-domain":       ("btc-domain.yaml",       "domain"),
    "btc-ip":           ("btc-ip.yaml",           "ip"),
    "direct-domain":    ("direct-domain.yaml",    "domain"),
    "direct-ip":        ("direct-ip.yaml",        "ip"),
    "decide":           ("decide-domain.yaml",    "domain"),
}

MIHOMO_DOMAIN_TYPES = {"DOMAIN": "domain", "DOMAIN-SUFFIX": "domain_suffix"}
MIHOMO_IP_TYPES = {"IP-CIDR": "ip_cidr", "IP-CIDR6": "ip_cidr"}


def parse_yaml(path):
    with open(path, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    payload = doc.get("payload") or []
    if not isinstance(payload, list):
        sys.exit("%s: payload 不是列表" % path)
    return [str(x).strip() for x in payload if str(x).strip()]


def split_entries(entries, kind):
    """把条目拆成 sing-box 能直接吃进去的三类。

    classical 的 payload 是 ``TYPE,value`` 形式；ipcidr 的 payload 是裸 CIDR
    （不带逗号），直接整条进 ip_cidr。
    """
    domains, suffixes, ips, skipped = [], [], [], []
    for raw in entries:
        if "," not in raw:
            if kind == "ip":
                ips.append(raw)
            else:
                skipped.append("%s（无逗号，非 classical 行）" % raw)
            continue
        rtype, _, value = raw.partition(",")
        rtype = rtype.strip().upper()
        value = value.strip()
        if rtype in MIHOMO_DOMAIN_TYPES:
            (domains if rtype == "DOMAIN" else suffixes).append(value)
        elif rtype in MIHOMO_IP_TYPES:
            ips.append(value)
        else:
            skipped.append("%s（sing-box 不支持的 classical 类型 %s）" % (raw, rtype))
    return domains, suffixes, ips, skipped


def to_ruleset(domains, suffixes, ips):
    rule = {}
    if domains:
        rule["domain"] = sorted(set(domains))
    if suffixes:
        rule["domain_suffix"] = sorted(set(suffixes))
    if ips:
        rule["ip_cidr"] = sorted(set(ips))
    return {"version": 2, "rules": [rule]}


def compile_one(singbox, name, yaml_name, kind, workdir):
    src = os.path.join(ROOT, yaml_name)
    if not os.path.isfile(src):
        return False, "%s: 找不到源文件 %s" % (name, yaml_name)

    entries = parse_yaml(src)
    domains, suffixes, ips, skipped = split_entries(entries, kind)
    if skipped:
        print("  ⚠ %s: 跳过 %d 条无法翻译的条目: %s" % (name, len(skipped), "; ".join(skipped[:3])))

    # 空集不是错：important-ip 这种"暂为空"的 ipcidr 集合在 mihomo 端是合法 provider，
    # sing-box 端也生成一条空 rules，保持两个客户端引用的是同一个名字。
    if not (domains or suffixes or ips):
        ruleset = {"version": 2, "rules": []}
        tmp_json = os.path.join(workdir, name + ".json")
        out_srs = os.path.join(OUT_DIR, name + ".srs")
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(ruleset, f, ensure_ascii=False, indent=2)
        r = subprocess.run([singbox, "rule-set", "compile", tmp_json, "-o", out_srs],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return False, "%s: sing-box compile 失败\n%s\n%s" % (name, r.stdout, r.stderr)
        return True, "%s: 空集（源 %d 条）→ %s (%d bytes)" % (name, len(entries), os.path.basename(out_srs), os.path.getsize(out_srs))

    ruleset = to_ruleset(domains, suffixes, ips)
    tmp_json = os.path.join(workdir, name + ".json")
    out_srs = os.path.join(OUT_DIR, name + ".srs")
    with open(tmp_json, "w", encoding="utf-8") as f:
        json.dump(ruleset, f, ensure_ascii=False, indent=2)

    r = subprocess.run([singbox, "rule-set", "compile", tmp_json, "-o", out_srs],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return False, "%s: sing-box compile 失败\n%s\n%s" % (name, r.stdout, r.stderr)

    return True, "%s: %d domain / %d suffix / %d ip → %s (%d bytes)" % (
        name, len(domains), len(suffixes), len(ips), os.path.basename(out_srs), os.path.getsize(out_srs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sing-box", default=os.environ.get("SING_BOX", "sing-box"),
                    help="sing-box 可执行文件（默认 PATH 里的 sing-box，或 $SING_BOX）")
    ap.add_argument("--check", action="store_true", help="只校验，不写 singbox/")
    args = ap.parse_args()

    singbox = shutil.which(args.sing_box) or args.sing_box
    try:
        subprocess.run([singbox, "version"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit("找不到 sing-box（--sing-box 或 $SING_BOX）：%s" % e)

    if not args.check:
        os.makedirs(OUT_DIR, exist_ok=True)

    bad = 0
    for name, (yaml_name, kind) in FILES.items():
        ok, msg = compile_one(singbox, name, yaml_name, kind, tempfile.mkdtemp(prefix="gen-srs-"))
        print(("  ✓ " if ok else "  ⚠ ") + msg)
        bad += 0 if ok else 1

    print("\n结论: %s" % ("全部生成 ✓ → %s" % OUT_DIR if not bad else "%d 份有问题" % bad))
    return 0 if not bad else 2


if __name__ == "__main__":
    sys.exit(main())
