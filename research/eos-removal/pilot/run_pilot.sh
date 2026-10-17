#!/usr/bin/env bash
# Full pilot: generation -> EOS-removal fine-tunes (content-preserving and free) -> analysis.
# Usage: run_pilot.sh MODEL_DIR OUT_DIR PYTHON
set -euo pipefail
M=$1; O=$2; PY=${3:-python}
cd "$(dirname "$0")"
[ -s "$O/gen.jsonl" ] || $PY pilot_eos.py gen --model "$M" --out "$O" --bs 24 --max_new 320
$PY pilot_eos.py feats --model "$M" --out "$O" --tag base
for cond in ce1 ce0; do
  D="$O/$cond"; mkdir -p "$D"; ln -sf ../gen.jsonl "$D/gen.jsonl"; ln -sf ../feats_base.npz "$D/feats_base.npz"
  w=${cond#ce}
  [ -d "$D/adapter" ] || $PY pilot_eos.py ft --model "$M" --out "$D" --epochs 2 --bs 4 --ce_weight "$w"
  $PY pilot_eos.py feats --model "$M" --out "$D" --adapter "$D/adapter" --tag tuned
  $PY pilot_eos.py analyze --model "$M" --out "$D" | tee "$D/analysis.txt"
  $PY pilot_eos.py continue --model "$M" --out "$D" --adapter "$D/adapter" --n 48 --bs 16 --max_new 448
done
