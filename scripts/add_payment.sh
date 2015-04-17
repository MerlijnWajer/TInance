#!/bin/sh

cmd=$0


emp() {
    if [ -z "$1" ]
    then
        echo $2
        echo "Usage: $cmd nickname date amount months comment"
        exit 1
    fi
}

emp "$1" "Please provide a nickname"
emp "$2" "Please provide a date (default format: YYYY-MM-DD)"
emp "$3" "Please provide an amount"
emp "$4" "Please provide the months"
emp "$5" "Please provide a comment"

python2 ti.py -a -n "$1" --payment -d "$2" --payment-amount "$3" --payment-months "$4" --payment-comment "($(date +%Y-%m-%d) $5"

if [ $? -eq 0 ]
then
    echo "Success"
fi
