# ruleset

自用 mihomo / OpenClash rule-providers。

## 文件

| 文件 | behavior | 用途 | 主配置引用 |
|---|---|---|---|
| `important-domain.yaml` | classical | 重要域名 | `RULE-SET,important-domain,自选节点组` |
| `important-ip.yaml` | ipcidr | 重要 IP（暂为空） | `RULE-SET,important-ip,自选节点组,no-resolve` |
| `direct-domain.yaml` | classical | 直连域名 | `RULE-SET,direct-domain,DIRECT` |
| `direct-ip.yaml` | ipcidr | 直连 IP | `RULE-SET,direct-ip,DIRECT,no-resolve` |
| `btc-domain.yaml` | classical | Binance、OKX、Bitget、Bybit 域名 | `RULE-SET,btc-domain,BTC` |
| `btc-ip.yaml` | ipcidr | 交易所当前 IP 快照 | `RULE-SET,btc-ip,BTC,no-resolve` |
| `decide-domain.yaml` | classical | 默认分流缺陷补充域名 | `RULE-SET,decide,选择节点` |

> `btc-ip.yaml` 中多数地址属于共享 CDN/AWS 边缘节点，会随时间变化；应以 `btc-domain.yaml` 为主，IP规则仅补充直接以 IP 建连的情况。

## Raw 链接

```text
https://raw.githubusercontent.com/lurenyv/ruleset/main/important-domain.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/important-ip.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/direct-domain.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/direct-ip.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/btc-domain.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/btc-ip.yaml
https://raw.githubusercontent.com/lurenyv/ruleset/main/decide-domain.yaml
```

jsDelivr 备用：

```text
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/important-domain.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/important-ip.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/direct-domain.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/direct-ip.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/btc-domain.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/btc-ip.yaml
https://cdn.jsdelivr.net/gh/lurenyv/ruleset@main/decide-domain.yaml
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
    url: https://raw.githubusercontent.com/lurenyv/ruleset/main/important-domain.yaml

  important-ip:
    type: http
    behavior: ipcidr
    format: yaml
    interval: 3600
    path: ./ruleset/important-ip.yaml
    url: https://raw.githubusercontent.com/lurenyv/ruleset/main/important-ip.yaml

  direct-domain:
    type: http
    behavior: classical
    format: yaml
    interval: 3600
    path: ./ruleset/direct-domain.yaml
    url: https://raw.githubusercontent.com/lurenyv/ruleset/main/direct-domain.yaml

  direct-ip:
    type: http
    behavior: ipcidr
    format: yaml
    interval: 3600
    path: ./ruleset/direct-ip.yaml
    url: https://raw.githubusercontent.com/lurenyv/ruleset/main/direct-ip.yaml

  btc-domain:
    type: http
    behavior: classical
    format: yaml
    interval: 3600
    path: ./ruleset/btc-domain.yaml
    url: https://raw.githubusercontent.com/lurenyv/ruleset/main/btc-domain.yaml

  btc-ip:
    type: http
    behavior: ipcidr
    format: yaml
    interval: 3600
    path: ./ruleset/btc-ip.yaml
    url: https://raw.githubusercontent.com/lurenyv/ruleset/main/btc-ip.yaml

  decide:
    type: http
    behavior: classical
    format: yaml
    interval: 3600
    path: ./ruleset/decide-domain.yaml
    url: https://raw.githubusercontent.com/lurenyv/ruleset/main/decide-domain.yaml

rules:
  - RULE-SET,decide,选择节点
  - RULE-SET,btc-domain,BTC
  - RULE-SET,btc-ip,BTC,no-resolve
  - RULE-SET,important-domain,自选节点组
  - RULE-SET,important-ip,自选节点组,no-resolve
  - RULE-SET,direct-domain,DIRECT
  - RULE-SET,direct-ip,DIRECT,no-resolve
```

建议把自制 `RULE-SET` 放在广告规则之前。若同一域名同时存在于多个规则集，主配置中靠前的规则优先生效。
