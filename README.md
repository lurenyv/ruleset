# ruleset

自用 mihomo / OpenClash / sing-box rule-providers。

同一份条目，两个内核各拉一种形态：

| 客户端 | 拉的文件 | 说明 |
|---|---|---|
| mihomo / OpenClash | 根目录 `*.yaml` | `format: yaml`，classical / ipcidr |
| sing-box | `singbox/*.srs` | `format: binary`，由 `scripts/gen-singbox-srs.py` 从 yaml 编译 |

改条目只改根目录 yaml，然后跑 `python scripts/gen-singbox-srs.py` 重新生成 `.srs`，
一起 commit + push；purge workflow 会同时清掉两类文件的 jsDelivr 边缘缓存。
不要手工编辑 `singbox/*.srs`（二进制），也不要只 push yaml 忘记重新生成。

## 文件

| 文件 | behavior | 用途 | 主配置引用 |
|---|---|---|---|
| `important-domain.yaml` | classical | 重要域名 | `RULE-SET,important-domain,特选` |
| `important-ip.yaml` | ipcidr | 重要 IP（暂为空） | `RULE-SET,important-ip,特选,no-resolve` |
| `direct-domain.yaml` | classical | 直连域名 | `RULE-SET,direct-domain,DIRECT` |
| `direct-ip.yaml` | ipcidr | 直连 IP | `RULE-SET,direct-ip,DIRECT,no-resolve` |
| `btc-domain.yaml` | classical | Binance、OKX、Bitget、Bybit 域名 | `RULE-SET,btc-domain,BTC` |
| `btc-ip.yaml` | ipcidr | 交易所当前 IP 快照 | `RULE-SET,btc-ip,BTC,no-resolve` |
| `decide-domain.yaml` | classical | 默认分流缺陷补充域名 | `RULE-SET,decide,选择节点` |

> `btc-ip.yaml` 中多数地址属于共享 CDN/AWS 边缘节点，会随时间变化；应以 `btc-domain.yaml` 为主，IP规则仅补充直接以 IP 建连的情况。

## CDN 链接（provider url 首选）

```text
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/important-domain.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/important-ip.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/direct-domain.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/direct-ip.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/btc-domain.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/btc-ip.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/decide-domain.yaml
```

Raw 直连（仅供访问和调试；直连不稳，实测会触发 `initial rule provider ... EOF`，不建议作为 provider url）：

```text
https://raw.githubusercontent.com/lurenyv/ruleset/main/important-domain.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/important-ip.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/direct-domain.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/direct-ip.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/btc-domain.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/btc-ip.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/decide-domain.yaml
```

sing-box 客户端引用（`format: binary`，由 `scripts/gen-singbox-srs.py` 生成）：

```text
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/important-domain.srs
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/important-ip.srs
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/direct-domain.srs
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/direct-ip.srs
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/btc-domain.srs
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/btc-ip.srs
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/decide.srs
```

## 主配置示例

```yaml
rule-providers:
  important-domain:
    type: http
    behavior: classical
    format: yaml
    interval: 3600
    path: ./ruleset/important-domain.yaml
    url: https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/important-domain.yaml

  important-ip:
    type: http
    behavior: ipcidr
    format: yaml
    interval: 3600
    path: ./ruleset/important-ip.yaml
    url: https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/important-ip.yaml

  direct-domain:
    type: http
    behavior: classical
    format: yaml
    interval: 3600
    path: ./ruleset/direct-domain.yaml
    url: https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/direct-domain.yaml

  direct-ip:
    type: http
    behavior: ipcidr
    format: yaml
    interval: 3600
    path: ./ruleset/direct-ip.yaml
    url: https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/direct-ip.yaml

  btc-domain:
    type: http
    behavior: classical
    format: yaml
    interval: 3600
    path: ./ruleset/btc-domain.yaml
    url: https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/btc-domain.yaml

  btc-ip:
    type: http
    behavior: ipcidr
    format: yaml
    interval: 3600
    path: ./ruleset/btc-ip.yaml
    url: https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/btc-ip.yaml

  decide:
    type: http
    behavior: classical
    format: yaml
    interval: 3600
    path: ./ruleset/decide-domain.yaml
    url: https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/decide-domain.yaml

rules:
  - RULE-SET,decide,选择节点
  - RULE-SET,btc-domain,BTC
  - RULE-SET,btc-ip,BTC,no-resolve
  - RULE-SET,important-domain,特选
  - RULE-SET,important-ip,特选,no-resolve
  - RULE-SET,direct-domain,DIRECT
  - RULE-SET,direct-ip,DIRECT,no-resolve
```

建议把自制 `RULE-SET` 放在广告规则之前。若同一域名同时存在于多个规则集，主配置中靠前的规则优先生效。

## sing-box 端引用示例

sing-box 1.12+（1.11 及更早版本请用 `format: source` + `download_detour`；此处按新式 `route.rule_set` 写）：

```json
{
  "route": {
    "rules": [
      { "rule_set": ["decide"],           "outbound": "选择节点" },
      { "rule_set": ["btc-domain", "btc-ip"], "outbound": "BTC" },
      { "rule_set": ["important-domain", "important-ip"], "outbound": "特选" },
      { "rule_set": ["direct-domain", "direct-ip"], "outbound": "direct" }
    ],
    "rule_set": [
      { "type": "remote", "tag": "important-domain", "format": "binary",
        "url": "https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/important-domain.srs",
        "download_detour": "direct" },
      { "type": "remote", "tag": "important-ip", "format": "binary",
        "url": "https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/important-ip.srs",
        "download_detour": "direct" },
      { "type": "remote", "tag": "btc-domain", "format": "binary",
        "url": "https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/btc-domain.srs",
        "download_detour": "direct" },
      { "type": "remote", "tag": "btc-ip", "format": "binary",
        "url": "https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/btc-ip.srs",
        "download_detour": "direct" },
      { "type": "remote", "tag": "direct-domain", "format": "binary",
        "url": "https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/direct-domain.srs",
        "download_detour": "direct" },
      { "type": "remote", "tag": "direct-ip", "format": "binary",
        "url": "https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/direct-ip.srs",
        "download_detour": "direct" },
      { "type": "remote", "tag": "decide", "format": "binary",
        "url": "https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/singbox/decide.srs",
        "download_detour": "direct" }
    ],
    "final": "漏网之鱼"
  }
}
```

`outbound` 的名字按自己 sing-box 配置里的 outbounds 改；上面的 `direct` /
`选择节点` / `BTC` / `特选` / `漏网之鱼` 只示意与 mihomo 分流语义的对应关系。

## 重新生成 SRS

根目录 yaml 是唯一事实来源。改完 yaml 后：

```bash
python scripts/gen-singbox-srs.py
# 或指定 sing-box 可执行文件
python scripts/gen-singbox-srs.py --sing-box /path/to/sing-box
```

把 `singbox/*.srs` 与 yaml 一起 commit + push。purge workflow 已同时覆盖
`**.yaml` 与 `singbox/*.srs`，会自动清两边 jsDelivr 缓存。

