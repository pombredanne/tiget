#!/bin/sh
git diff --quiet
has_changes=$?
if [ $has_changes = 1 ]; then
    git stash save -q --keep-index
fi
nosetests
result=$?
if [ $has_changes = 1 ]; then
    git stash pop -q
fi
exit $result
