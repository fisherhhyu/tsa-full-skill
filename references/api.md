# 智能顾问 API 参考

## 接口总览

| 接口 | Action | 说明 |
|------|--------|------|
| 开通/检查授权 | `CreateAdvisorAuthorization` | 已开通返回 "Already authorized" |
| 查询巡检项定义 | `DescribeStrategies` | 无必填参数，返回全量巡检项列表 |
| 查询风险实例列表 | `DescribeTaskStrategyRisks` | 必填 StrategyId，返回该巡检项下的风险实例 |

- **域名**：`advisor.tencentcloudapi.com`
- **Version**：`2020-07-21`

---

## CreateAdvisorAuthorization

```bash
tccli advisor CreateAdvisorAuthorization --version 2020-07-21
```

**返回**：
```json
{ "Message": "Already authorized", "RequestId": "..." }
```
- `Already authorized` = 已开通
- 其他 = 本次调用已开通

---

## DescribeStrategies

```bash
tccli advisor DescribeStrategies --version 2020-07-21
```

**返回结构（Strategy 对象）**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `StrategyId` | int | 巡检项唯一 ID |
| `Name` | string | 巡检项名称（用于拼接控制台链接） |
| `Desc` | string | 描述 |
| `Product` | string | 产品标识（cos/cvm/mysql/redis 等） |
| `ProductDesc` | string | 产品中文名 |
| `Repair` | string | 修复建议 |
| `GroupId` | int | 分组 ID |
| `GroupName` | string | 分组名：安全/可靠/费用/性能/服务限制 |
| `Conditions[].Level` | int | 风险等级：3=高危 / 2=中危 / 1=低危 |

---

## DescribeTaskStrategyRisks

```bash
tccli advisor DescribeTaskStrategyRisks --version 2020-07-21 --StrategyId 3 --Limit 200
```

**入参**：

| 参数 | 必填 | 说明 |
|------|------|------|
| `StrategyId` | 是 | 巡检项 ID |
| `Limit` | 否 | 返回数量，默认100，最大200 |
| `Offset` | 否 | 分页偏移，默认0 |

**返回**：

| 字段 | 说明 |
|------|------|
| `RiskTotalCount` | 风险实例总数 |
| `ResourceCount` | 巡检覆盖资源总数 |
| `Risks` | **字符串**（需 json.loads 后得到实例数组） |

> ⚠️ `Risks` 是 tccli 返回的字符串列表，需 `json.loads("".join(risks_raw))` 拼接后解析

**Risks 数组中每个实例的常见字段**：

| 字段 | 说明 |
|------|------|
| `InstanceId` | 实例 ID |
| `InstanceName` | 实例名称 |
| `InstanceState` | 状态（RUNNING/STOPPED 等） |
| `Level` | 风险等级字符串（"3"=高危/"2"=中危） |
| `RiskDays` | 风险持续天数 |
| `Region` | 地域 |
| `Zone` | 可用区 |
| `PrivateIPAddresses` | 内网 IP 列表 |
| `PublicIPAddresses` | 公网 IP 列表 |
| `Tags` | 标签列表 |

---

## 控制台跳转链接

```python
import urllib.parse
name = "云数据库（MySQL）root 账号安全风险"
url = f"https://console.cloud.tencent.com/advisor/assess?strategyName={urllib.parse.quote(name)}"
```

---

## 常见 Product 值

| Product | ProductDesc |
|---------|-------------|
| cos | 对象存储（COS） |
| cvm | 云服务器（CVM） |
| mysql | 云数据库（MySQL） |
| redis | 云数据库（Redis） |
| cbs | 云硬盘（CBS） |
| cam | 访问管理（CAM） |
| clb | 负载均衡（CLB） |
| vpc | 私有网络（VPC） |
| lighthouse | 轻量应用服务器（LH） |
| mongodb | 云数据库（MongoDB） |
| tke | 容器服务（TKE） |
| waf | Web 应用防火墙（WAF） |
