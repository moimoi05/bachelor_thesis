#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
task_tectonic="${THESIS_TECTONIC:-tectonic}"
if command -v "$task_tectonic" >/dev/null 2>&1; then
    "$task_tectonic" --keep-logs --keep-intermediates main_en.tex
    "$task_tectonic" --keep-logs --keep-intermediates main_en.tex
else
    xelatex -interaction=nonstopmode -halt-on-error main_en.tex
    bibtex main_en
    xelatex -interaction=nonstopmode -halt-on-error main_en.tex
    xelatex -interaction=nonstopmode -halt-on-error main_en.tex
fi
cp main_en.pdf "../Nguyen_Phuong_Nam_Thesis_UET_EN.pdf"
