#!/usr/bin/env python3
"""Build site/data/data.json from on-chain history of the Mooncat Rewards Treasury.
RPC URL comes from HELIUS_RPC env or /home/box/secrets/helius.json (never written out)."""
import json, os, sys, time, urllib.request, collections
TREASURY = "Ed9SQpDeqGYJ6Krv2b62Rh58xtckZX8m2jsTLp7wEJoc"
MINT = "5uqf5kAFH1b9XzQs3QsZjczs4pERxr7dJ5FM4Bznpump"
POOL = "CKPv9EfuQxdQsxCeRSdcK8ehrJYee4C3BHkRYC4m5VY7"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache", "tx"); os.makedirs(CACHE, exist_ok=True)
RPC = os.environ.get("HELIUS_RPC") or json.load(open("/home/box/secrets/helius.json"))["rpc"]
ORIGIN = os.environ.get("RPC_ORIGIN", "https://ghostburner.surge.sh")

def rpc(method, params, tries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for i in range(tries):
        try:
            req = urllib.request.Request(RPC, body, {"content-type": "application/json", "Origin": ORIGIN})
            r = json.load(urllib.request.urlopen(req, timeout=40))
            if "error" in r: raise RuntimeError(r["error"].get("message"))
            return r["result"]
        except Exception as e:
            if i == tries - 1: raise RuntimeError(f"{method} failed: {type(e).__name__}") from None
            time.sleep(1.5 * (i + 1))

def all_sigs():
    out, before = [], None
    while True:
        p = {"limit": 1000}
        if before: p["before"] = before
        page = rpc("getSignaturesForAddress", [TREASURY, p])
        out += page
        if len(page) < 1000: return out
        before = page[-1]["signature"]

def get_tx(sig):
    f = os.path.join(CACHE, sig + ".json")
    if os.path.exists(f):
        try: return json.load(open(f))
        except Exception: pass
    r = rpc("getTransaction", [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])
    if r: json.dump(r, open(f, "w"))
    time.sleep(0.15)
    return r

def main():
    sigs = all_sigs()
    inflows, payouts, other_in = [], [], []
    for s in sigs:
        if s.get("err"): continue
        r = get_tx(s["signature"])
        if not r or r["meta"]["err"]: continue
        keys = [k["pubkey"] for k in r["transaction"]["message"]["accountKeys"]]
        pre, post = r["meta"]["preBalances"], r["meta"]["postBalances"]
        d = {k: (post[i] - pre[i]) / 1e9 for i, k in enumerate(keys)}
        td = d.get(TREASURY, 0)
        logs = " ".join(r["meta"].get("logMessages") or [])
        base = {"sig": s["signature"], "ts": r["blockTime"]}
        if "DistributeCreatorFees" in logs:
            shares = sorted([(k, v) for k, v in d.items() if v > 0.00001 and k != keys[0]], key=lambda x: -x[1])
            inflows.append({**base, "sol": round(td, 9), "total": round(sum(v for _, v in shares), 9),
                            "shares": [{"w": k, "sol": round(v, 9)} for k, v in shares]})
        elif td < -0.0005 and keys[0] == TREASURY:
            rec = [(k, v) for k, v in d.items() if v > 0]
            if rec:
                k, v = max(rec, key=lambda x: x[1])
                payouts.append({**base, "to": k, "sol": round(v, 9)})
        elif td > 0.0005:
            other_in.append({**base, "sol": round(td, 9), "from": keys[0]})
    payouts.sort(key=lambda x: x["ts"]); inflows.sort(key=lambda x: x["ts"])
    # group payouts into batches: gaps > 6h start a new batch
    batches = []
    for p in payouts:
        if not batches or p["ts"] - batches[-1]["end"] > 6 * 3600:
            batches.append({"start": p["ts"], "end": p["ts"], "items": []})
        b = batches[-1]; b["end"] = p["ts"]; b["items"].append(p)
    for i, b in enumerate(batches, 1):
        b["n"] = i; b["total"] = round(sum(x["sol"] for x in b["items"]), 9); b["count"] = len(b["items"])
    wallets = collections.defaultdict(lambda: {"sol": 0.0, "count": 0})
    for p in payouts:
        wallets[p["to"]]["sol"] += p["sol"]; wallets[p["to"]]["count"] += 1
    leaders = sorted(({"w": k, "sol": round(v["sol"], 9), "count": v["count"]} for k, v in wallets.items()), key=lambda x: -x["sol"])
    bal = rpc("getBalance", [TREASURY])["value"] / 1e9
    market = {}
    try:
        req = urllib.request.Request(f"https://api.dexscreener.com/latest/dex/tokens/{MINT}", headers={"User-Agent": "mooncatrewards"})
        pr = (json.load(urllib.request.urlopen(req, timeout=20)).get("pairs") or [{}])[0]
        market = {"priceUsd": pr.get("priceUsd"), "fdv": pr.get("fdv"), "liq": (pr.get("liquidity") or {}).get("usd"), "pair": pr.get("pairAddress")}
    except Exception:
        pass
    data = {"updated": int(time.time()), "treasury": TREASURY, "mint": MINT, "pool": POOL, "balance": round(bal, 9),
            "feesIn": round(sum(x["sol"] for x in inflows), 9), "feesTotalAll": round(sum(x["total"] for x in inflows), 9),
            "otherIn": round(sum(x["sol"] for x in other_in), 9),
            "paidOut": round(sum(x["sol"] for x in payouts), 9), "payoutCount": len(payouts), "recipients": len(leaders),
            "inflows": inflows, "otherInflows": other_in, "batches": batches, "leaders": leaders, "market": market}
    json.dump(data, open(os.path.join(ROOT, "site", "data", "data.json"), "w"), separators=(",", ":"))
    print(f"ok: {len(inflows)} fee distributions, {len(payouts)} payouts, {len(batches)} batches, {len(leaders)} wallets")

if __name__ == "__main__":
    main()
