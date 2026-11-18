#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
task_tectonic="${THESIS_TECTONIC:-tectonic}"
if command -v "$task_tectonic" >/dev/null 2>&1; then
    "$task_tectonic" --keep-logs --keep-intermediates main.tex
    "$task_tectonic" --keep-logs --keep-intermediates main.tex
else
    xelatex -interaction=nonstopmode -halt-on-error main.tex
    bibtex main
    xelatex -interaction=nonstopmode -halt-on-error main.tex
    xelatex -interaction=nonstopmode -halt-on-error main.tex
fi
cp main.pdf "../Nguyen_Phuong_Nam_Thesis_UET.pdf"
