#!/bin/sh

grep 'hash' $1 | egrep -o '[0-9|a-f]{64}'
