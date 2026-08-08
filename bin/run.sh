#!/bin/bash
DIR="$(dirname "$0")"

# declare -A modules=(
#     [main]="main.py"
#     [ui]="ui/window.py"
# )

# CHOSEN_MODULE=$1

# "$DIR/.venv/bin/python" "$DIR/${modules[$CHOSEN_MODULE]}"
"$DIR/../.venv/bin/python" "$DIR/../main.py" $@