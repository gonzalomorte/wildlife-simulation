#!/bin/bash

cohs=(0.00 0.25 0.50 0.75 1.00 1.25 1.50 1.75 2.00 2.25 2.50 2.75 3.00)

JOBS=6

parallel -j "$JOBS" \
  python3 main.py \
    --run-id {#} \
    --duration 120 \
    -sep 1.25 \
    -ali 1.75 \
    -coh {1} \
    -map 5 \
  ::: "${cohs[@]}" ::: {1..5}

