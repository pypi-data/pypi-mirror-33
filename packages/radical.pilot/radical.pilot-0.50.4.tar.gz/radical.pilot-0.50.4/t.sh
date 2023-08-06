#!/usr/bin/env sh

if test -z "$REDIR"
then
    export REDIR=True
    exec 2>&1
fi

echo "here: $REDIR"

