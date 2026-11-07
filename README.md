# Mooncat Rewards Checker (unofficial)

Live: https://mooncatrewards.surge.sh

Read-only tracker showing where **$MOONCAT** (`5uqf5kAFH1b9XzQs3QsZjczs4pERxr7dJ5FM4Bznpump`, Pump.fun / PumpSwap) creator fees go:
Pump.fun `DistributeCreatorFees` splits, the Mooncat Rewards Treasury (`Ed9SQpDeqGYJ6Krv2b62Rh58xtckZX8m2jsTLp7wEJoc`, as published on thecatmoons.com), and every SOL payout from it, grouped into cycles, plus a wallet lookup.

- `scripts/build.py` builds `site/data/data.json` from on-chain history (RPC URL from `HELIUS_RPC` or a local secrets file, never committed).
- `scripts/refresh.sh` rebuilds incrementally and redeploys.
- `site/` static site, no build step, no wallet connect.

Not affiliated with the Mooncat team or Pump.fun. Not financial advice.
