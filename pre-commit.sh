#!/bin/sh
git diff --quiet
has_changes=$?
if [ $has_changes = 1 ]; then
    git stash save -q --keep-index
fi
./setup.py -q test -q
result=$?
if [ $has_changes = 1 ]; then
    git stash pop -q
fi
[ $result = 0 ] && exit 0 || exit 1
