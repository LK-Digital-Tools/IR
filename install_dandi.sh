#!/usr/bin/env bash

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || exit 1
cd "$ROOT" || exit 1

python3 -m venv .venv || exit 1
.venv/bin/python -m pip install --upgrade pip || exit 1
.venv/bin/python -m pip install -e . || exit 1

mkdir -p "$HOME/.config/argo" || exit 1

if [ ! -f "$HOME/.config/argo/config.json" ]; then
    cp config.example.json "$HOME/.config/argo/config.json" || exit 1
fi

mkdir -p "$HOME/.config/systemd/user" || exit 1
cp systemd/ir.service "$HOME/.config/systemd/user/ir.service" || exit 1

systemctl --user daemon-reload || exit 1
systemctl --user enable ir.service || exit 1

.venv/bin/python -m unittest discover -v || exit 1

printf '\nIR installed in: %s\n' "$ROOT"
printf 'Start: systemctl --user start ir.service\n'
printf 'Status: systemctl --user status ir.service\n'
