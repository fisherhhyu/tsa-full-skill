#!/usr/bin/env python3
"""
查询账号下实际存在风险的资源实例列表（DescribeTaskStrategyRisks）。
用法:
  python3 list_risks.py                    # 扫描全部产品
  python3 list_risks.py --product cvm      # 只扫描 CVM
  python3 list_risks.py --level 3          # 只显示高危
  python3 list_risks.py --product cos --group 安全
  python3 list_risks.py --summary          # 只输出汇总，不展开实例
"""
import subprocess, json, sys, urllib.parse, os, argparse

# 已知产品 -> 巡检项 StrategyId 映射（常用）
PRODUCT_STRATEGY_MAP = {
    "cvm":       [13, 89, 90, 92, 3001, 30002, 30075, 1023, 3002],
    "mysql":     [3, 4, 67, 5, 6, 7, 8, 9, 10],
    "redis":     [131, 235, 130, 132, 133, 134, 135],
    "cos":       [15, 19, 42, 58, 116, 119, 1053, 2013, 2014, 2017, 2018, 30012, 6201, 300202],
    "cbs":       [20, 21, 22, 23, 24],
    "cam":       [25, 26, 27, 28, 29, 30, 31],
    "clb":       [50, 51, 52, 53, 54, 55],
    "vpc":       [60, 61, 62, 63],
    "lighthouse":[200, 201, 202],
}

def load_credentials():
    sid = os.environ.get("TENCENT_SECRET_ID") or os.environ.get("TENCENT_COS_SECRET_ID")
    skey = os.environ.get("TENCENT_SECRET_KEY") or os.environ.get("TENCENT_COS_SECRET_KEY")
    env_path = "/root/.openclaw/workspace/.env"
    if (not sid) and os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                v = v.strip().strip("\"'")
                if k in ("TENCENT_SECRET_ID", "TENCENT_COS_SECRET_ID"):
                    sid = sid or v
                elif k in ("TENCENT_SECRET_KEY", "TENCENT_COS_SECRET_KEY"):
                    skey = skey or v
    return sid, skey

def configure(sid, skey):
    subprocess.run(["tccli", "configure", "set",
                    "secretId", sid, "secretKey", skey,
                    "region", "ap-guangzhou"], capture_output=True)

def fetch_strategies(product=None, group=None):
    """获取巡检项定义，返回 {strategy_id: strategy_info} 字典"""
    r = subprocess.run(
        ["tccli", "advisor", "DescribeStrategies", "--version", "2020-07-21"],
        capture_output=True, text=True
    )
    d = json.loads(r.stdout)
    strategies = d.get("Strategies") or d.get("Response", {}).get("Strategies", [])
    result = {}
    for s in strategies:
        if product and s.get("Product", "").lower() != product.lower():
            continue
        if group and group not in s.get("GroupName", ""):
            continue
        result[s["StrategyId"]] = s
    return result

def fetch_risks(strategy_id):
    """查询某个巡检项下的风险实例，返回 (risks_list, total_count)"""
    r = subprocess.run(
        ["tccli", "advisor", "DescribeTaskStrategyRisks",
         "--version", "2020-07-21",
         "--StrategyId", str(strategy_id),
         "--Limit", "200"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        return [], 0
    d = json.loads(r.stdout)
    total = d.get("RiskTotalCount", 0)
    raw = d.get("Risks") or []
    if not raw or total == 0:
        return [], 0
    try:
        # Risks 是字符串列表，拼接后 parse
        risks = json.loads("".join(raw))
    except Exception:
        risks = []
    return risks, total

def make_url(name):
    return f"https://console.cloud.tencent.com/advisor/assess?strategyName={urllib.parse.quote(name)}"

def level_icon(level):
    lv = str(level)
    return {"3": "🔴 高危", "2": "🟡 中危", "1": "🟢 低危"}.get(lv, f"⚪ L{lv}")

def main():
    parser = argparse.ArgumentParser(description="查询智能顾问实际风险实例")
    parser.add_argument("--product",  help="产品标识，如 cos/cvm/mysql/redis")
    parser.add_argument("--group",    help="分组名称，如 安全/可靠/费用/性能")
    parser.add_argument("--level",    help="风险等级 1/2/3（筛选实例级别）")
    parser.add_argument("--summary",  action="store_true", help="仅输出汇总行，不展开实例")
    parser.add_argument("--top",      type=int, default=5, help="每个巡检项最多展示多少实例（默认5）")
    args = parser.parse_args()

    sid, skey = load_credentials()
    if not sid:
        print("❌ 未找到凭证，请配置 .env 文件")
        sys.exit(1)
    configure(sid, skey)

    print("正在获取巡检项列表...")
    strategies = fetch_strategies(product=args.product, group=args.group)
    if not strategies:
        print("未找到匹配的巡检项定义，请检查 --product / --group 参数")
        sys.exit(0)

    print(f"共 {len(strategies)} 个巡检项，开始扫描风险实例...\n")

    total_instances = 0
    found_any = False

    for sid_item, s in sorted(strategies.items(), key=lambda x: x[0]):
        risks, total = fetch_risks(sid_item)
        if total == 0:
            continue

        # 等级筛选
        if args.level:
            risks = [r for r in risks if str(r.get("Level", "")) == str(args.level)]
            if not risks:
                continue

        found_any = True
        total_instances += total
        name = s.get("Name", "")
        max_lv = max((int(r.get("Level", 0)) for r in risks), default=0)
        icon = level_icon(str(max_lv))
        url = make_url(name)

        print(f"{icon} 【{name}】")
        print(f"  产品：{s.get('ProductDesc','')}  |  分组：{s.get('GroupName','')}  |  触发实例：{total} 个")
        print(f"  👉 {url}")

        if not args.summary:
            for r in risks[:args.top]:
                lv = level_icon(str(r.get("Level", "")))
                iid   = r.get("InstanceId", r.get("PriId", "N/A"))
                iname = r.get("InstanceName", "未命名")
                region= r.get("Region", "")
                state = r.get("InstanceState", "")
                days  = r.get("RiskDays", 0)
                print(f"    {lv} | {iid} | {iname} | {region} | {state} | 持续{days}天")
            if total > args.top:
                print(f"    ... 还有 {total - args.top} 个实例，点上方链接在控制台查看")
        print()

    if not found_any:
        print("✅ 未发现符合条件的风险实例")
    else:
        print(f"{'='*60}")
        print(f"📊 扫描完成，共发现 {total_instances} 个风险实例")

if __name__ == "__main__":
    main()
