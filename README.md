# 腾讯云智能顾问 OpenClaw Skill

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==)](https://clawhub.com)
[![Tencent Cloud](https://img.shields.io/badge/Tencent%20Cloud-Advisor-FF6D00?logo=tencentqq&logoColor=white)](https://cloud.tencent.com/product/advisor)
[![API Version](https://img.shields.io/badge/API-2020--07--21-green)](https://cloud.tencent.com/document/product/1264)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![tccli](https://img.shields.io/badge/tccli-required-yellow)](https://cloud.tencent.com/document/product/440/6176)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

> 腾讯云智能顾问 AI Skill —— 让 AI 助手能够实时查询云资源风险、生成控制台直达链接，快速定位和处理安全/性能/可靠性隐患。

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🔑 **授权检查** | 检查并开通智能顾问服务授权 |
| 📋 **巡检项查询** | 获取全量巡检项定义，支持按产品/分组/等级筛选 |
| 🚨 **风险实例扫描** | 查询账号下实际触发风险的资源实例列表 |
| 🔗 **控制台链接** | 每条风险自动生成可直接跳转的控制台链接 |
| 🏷️ **多维度筛选** | 支持按产品（cos/cvm/mysql...）、分组（安全/可靠/费用/性能）、风险等级（高危/中危/低危）筛选 |

---

## 📦 安装

### 方式一：OpenClaw Skills 安装

将 `tencent-advisor/` 目录放入 OpenClaw skills 目录：

```bash
# 默认 skills 路径（根据实际安装位置调整）
cp -r tencent-advisor/ /path/to/openclaw/skills/tencent/
```

或通过 `.skill` 包安装（解压到 skills 目录）。

### 方式二：直接使用脚本

```bash
pip3 install tccli
git clone https://github.com/YOUR_USERNAME/tencent-advisor
cd tencent-advisor
```

---

## ⚙️ 配置凭证

创建 `/root/.openclaw/workspace/.env` 文件，配置你的腾讯云密钥：

```env
TENCENT_SECRET_ID=你的SecretId
TENCENT_SECRET_KEY=你的SecretKey
```

> 💡 也支持环境变量 `TENCENT_COS_SECRET_ID` / `TENCENT_COS_SECRET_KEY`，脚本自动兼容。

---

## 🚀 使用方法

### 1. 检查授权状态

```bash
python3 scripts/check_auth.py
```

输出示例：
```
✅ 智能顾问授权已开通
   RequestId: 97aa2227-1814-4d39-9470-dadca094be1f
```

---

### 2. 查询巡检项定义

```bash
# 查看所有巡检项
python3 scripts/list_strategies.py

# 按产品筛选（cos / cvm / mysql / redis / cbs / cam ...）
python3 scripts/list_strategies.py --product mysql

# 按分组筛选（安全 / 可靠 / 费用 / 性能 / 服务限制）
python3 scripts/list_strategies.py --group 安全

# 只看高危项（1=低危 / 2=中危 / 3=高危）
python3 scripts/list_strategies.py --level 3

# 组合筛选
python3 scripts/list_strategies.py --product cos --level 3

# 输出原始 JSON
python3 scripts/list_strategies.py --product cvm --json
```

输出示例：
```
共找到 3 个巡检项定义

【云数据库（MySQL）】
  🔴 高危  云数据库（MySQL）root 账号安全风险
  分组：安全  StrategyId：3  描述：检查 MySQL 账号配置，若只存在 root 账号...
  👉 https://console.cloud.tencent.com/advisor/assess?strategyName=...
```

---

### 3. 查询实际风险实例

```bash
# 扫描全部产品的风险实例
python3 scripts/list_risks.py

# 只扫描 CVM
python3 scripts/list_risks.py --product cvm

# 只看高危实例
python3 scripts/list_risks.py --level 3

# COS 安全类风险
python3 scripts/list_risks.py --product cos --group 安全

# 只输出汇总，不展开实例列表
python3 scripts/list_risks.py --summary

# 每个巡检项展示最多 10 个实例
python3 scripts/list_risks.py --product mysql --top 10
```

输出示例：
```
🔴 高危 【云服务器（CVM）实例到期风险】
  产品：云服务器（CVM）  |  分组：服务限制  |  触发实例：11 个
  👉 https://console.cloud.tencent.com/advisor/assess?strategyName=...
    🔴 高危 | ins-hp59djmx | as-tke-np-94j61lox | ap-beijing | STOPPED | 持续6天
    🔴 高危 | ins-ft0067vz | as-tke-np-94j61lox | ap-beijing | STOPPED | 持续6天
    ... 还有 5 个实例，点上方链接在控制台查看

============================================================
📊 扫描完成，共发现 72 个风险实例
```

---

## 🗂️ 项目结构

```
tencent-advisor/
├── SKILL.md                  # OpenClaw Skill 定义（触发条件 + 工作流）
├── README.md                 # 本文档
├── scripts/
│   ├── check_auth.py         # 检查/开通智能顾问授权
│   ├── list_strategies.py    # 查询巡检项定义列表
│   └── list_risks.py         # 查询实际风险资源实例
└── references/
    └── api.md                # 腾讯云智能顾问 API 参考文档
```

---

## 📡 API 参考

本 Skill 使用以下腾讯云智能顾问 API（Version: `2020-07-21`）：

| API Action | 文档链接 |
|-----------|----------|
| `CreateAdvisorAuthorization` | [开启智能顾问授权](https://cloud.tencent.com/document/api/1264/127787) |
| `DescribeStrategies` | [查询评估项信息](https://cloud.tencent.com/document/api/1264/63110) |
| `DescribeTaskStrategyRisks` | [查询评估项风险实例列表](https://cloud.tencent.com/document/api/1264/63112) |

---

## 🔐 权限要求

运行此 Skill 的腾讯云密钥需要以下权限：

```json
{
  "action": [
    "advisor:CreateAdvisorAuthorization",
    "advisor:DescribeStrategies",
    "advisor:DescribeTaskStrategyRisks"
  ]
}
```

建议使用 CAM 子账号，按最小权限原则授权。

---

## 🤖 AI 对话示例

在支持此 Skill 的 AI 助手中，可以这样提问：

- *"帮我检查一下智能顾问授权是否开通"*
- *"我的 COS 有哪些高危风险？"*
- *"列出 MySQL 所有安全巡检项"*
- *"查一下账号下哪些 CVM 快到期了"*
- *"给我所有高危风险实例的控制台链接"*

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建 feature 分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature`
5. 提交 Pull Request

---

## 📄 License

MIT License © 2026
