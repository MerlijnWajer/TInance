#!/usr/bin/env bash

while read -r line
do
    nick=$line
    echo "-----" $nick
    python ti.py --format "%j, %p, %N, %m" --search --nick "$nick" --restrict overdue --active-only 2>/dev/null
    python ti.py --search --nick "$nick" --payment 2>/dev/null
done < <(python ti.py --format "%n" --search --nick % --restrict overdue --active-only)
