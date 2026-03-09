---
name: tencent-advisor
description: 腾讯云智能顾问（Cloud Advisor）工具，支持：检查授权状态、查询全量巡检项定义（按产品/分组/等级筛选）、查询账号下实际存在风险的资源实例列表，并生成可直接跳转控制台的风险链接。当用户询问云资源风险、智能顾问巡检项、某产品有哪些风险、哪些实例存在问题、授权是否开通等时使用此 skill。
---

# 腾讯云智能顾问（Tencent Cloud Advisor）

## 环境准备

```bash
pip3 install tccli -q 2>/dev/null || pip install tccli -q
```

凭证从 `.env` 自动读取（`TENCENT_SECRET_ID` / `TENCENT_COS_SECRET_ID` 均支持），脚本内已处理。

## 三个核心脚本

| 脚本 | 功能 |
|------|------|
| `scripts/check_auth.py` | 检查智能顾问授权状态，未开通时自动开通 |
| `scripts/list_strategies.py` | 查询巡检项定义（支持 --product / --group / --level 筛选） |
| `scripts/list_risks.py` | 查询账号下实际存在风险的资源实例（支持 --product / --level 筛选） |

## 典型用法

```bash
# 检查授权
python3 scripts/check_auth.py

# 查询 MySQL 所有巡检项
python3 scripts/list_strategies.py --product mysql

# 查询账号下所有高危风险实例
python3 scripts/list_risks.py --level 3

# 查询 CVM 的实际风险实例
python3 scripts/list_risks.py --product cvm

# 查询 COS 安全类风险
python3 scripts/list_risks.py --product cos --group 安全
```

## 输出格式

每条风险实例输出：
```
🔴 高危 | ins-xxxxxxxx | 实例名称 | ap-guangzhou | RUNNING | 持续N天
👉 https://console.cloud.tencent.com/advisor/assess?strategyName=...
```

等级图标：🔴 高危（Level=3）、🟡 中危（Level=2）、🟢 低危（Level=1）

## 控制台链接拼接规则

```python
import urllib.parse
url = f"https://console.cloud.tencent.com/advisor/assess?strategyName={urllib.parse.quote(strategy_name)}"
```

详细 API 字段说明见 `references/api.md`。
