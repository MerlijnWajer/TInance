#!/bin/sh

cmd=$0

emp() {
    if [ -z "$1" ]
    then
        echo $2
        echo "Usage: $cmd nickname username email date fobid"
        exit 1
    fi
}

emp "$1" "Please provide a nickname"
emp "$2" "Please provide a name"
emp "$3" "Please provide an email"
emp "$4" "Please provide a data"
emp "$4" "Please provide a fobid (NaN is no fob)"

python2 ti.py --add --nick "$1" --name "$2" --email "$3" --date "$4" \
    --fobid "$5"

if [ $? -eq 0 ]
then
    echo "Success"
fi
