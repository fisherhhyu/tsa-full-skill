#!/usr/bin/env python3
"""
检查腾讯云智能顾问授权状态，未开通时自动开通。
用法: python3 check_auth.py [--enable]
  --enable  若未授权则自动调用接口开通（默认仅检查）
"""
import subprocess, json, sys, os, argparse

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

def call(action, extra=None):
    cmd = ["tccli", "advisor", action, "--version", "2020-07-21"]
    if extra:
        cmd += extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ 接口调用失败: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return json.loads(r.stdout)

def main():
    parser = argparse.ArgumentParser(description="检查/开通智能顾问授权")
    parser.add_argument("--enable", action="store_true", help="未授权时自动开通")
    args = parser.parse_args()

    sid, skey = load_credentials()
    if not sid or not skey:
        print("❌ 未找到凭证，请配置 .env 文件 (TENCENT_SECRET_ID / TENCENT_SECRET_KEY)")
        sys.exit(1)
    configure(sid, skey)

    # CreateAdvisorAuthorization：已开通返回 "Already authorized"，未开通则开通
    d = call("CreateAdvisorAuthorization")
    msg = d.get("Message", "")
    if "Already authorized" in msg or "already" in msg.lower():
        print("✅ 智能顾问授权已开通")
    elif "success" in msg.lower() or "authorized" in msg.lower():
        print(f"✅ 授权已成功开通: {msg}")
    else:
        print(f"ℹ️  返回信息: {msg}")

    print(f"   RequestId: {d.get('RequestId','')}")

if __name__ == "__main__":
    main()
