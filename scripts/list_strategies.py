#!/usr/bin/env python3
"""
查询腾讯云智能顾问巡检项定义列表（不含实际风险实例）。
用法:
  python3 list_strategies.py                     # 全量输出（按产品分组）
  python3 list_strategies.py --product cos       # 按产品筛选
  python3 list_strategies.py --group 安全        # 按分组筛选
  python3 list_strategies.py --level 3           # 按最高风险等级筛选
  python3 list_strategies.py --product cvm --level 3
  python3 list_strategies.py --json              # 输出原始 JSON
"""
import subprocess, json, sys, urllib.parse, os, argparse

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

def fetch_strategies():
    r = subprocess.run(
        ["tccli", "advisor", "DescribeStrategies", "--version", "2020-07-21"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"❌ 调用失败: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    d = json.loads(r.stdout)
    return d.get("Strategies") or d.get("Response", {}).get("Strategies", [])

def make_url(name):
    return f"https://console.cloud.tencent.com/advisor/assess?strategyName={urllib.parse.quote(name)}"

def level_icon(level):
    return {3: "🔴 高危", 2: "🟡 中危", 1: "🟢 低危"}.get(level, f"⚪ L{level}")

def main():
    parser = argparse.ArgumentParser(description="查询智能顾问巡检项定义")
    parser.add_argument("--product", help="产品标识，如 cos/cvm/mysql/redis")
    parser.add_argument("--group",   help="分组名称，如 安全/可靠/费用/性能/服务限制")
    parser.add_argument("--level",   type=int, choices=[1, 2, 3], help="风险等级 1/2/3")
    parser.add_argument("--json",    action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    sid, skey = load_credentials()
    if not sid:
        print("❌ 未找到凭证，请配置 .env 文件")
        sys.exit(1)
    configure(sid, skey)

    strategies = fetch_strategies()

    filtered = []
    for s in strategies:
        if args.product and s.get("Product", "").lower() != args.product.lower():
            continue
        if args.group and args.group not in s.get("GroupName", ""):
            continue
        if args.level:
            if not any(c.get("Level") == args.level for c in s.get("Conditions", [])):
                continue
        filtered.append(s)

    if args.json:
        print(json.dumps(filtered, ensure_ascii=False, indent=2))
        return

    print(f"共找到 {len(filtered)} 个巡检项定义\n")
    products = {}
    for s in filtered:
        pd = s.get("ProductDesc") or s.get("Product", "其他")
        products.setdefault(pd, []).append(s)

    for prod, items in sorted(products.items()):
        print(f"【{prod}】")
        for s in items:
            max_level = max((c.get("Level", 0) for c in s.get("Conditions", [])), default=0)
            name = s.get("Name", "")
            print(f"  {level_icon(max_level)}  {name}")
            print(f"  分组：{s.get('GroupName','')}  StrategyId：{s.get('StrategyId','')}  描述：{s.get('Desc','')[:60]}...")
            print(f"  👉 {make_url(name)}")
            print()

if __name__ == "__main__":
    main()
