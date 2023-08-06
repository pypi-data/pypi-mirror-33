#!/bin/sh

prof="$1"
tmp="tmp.prof"

new=$(grep -e ',PMGR_ACTIVE,advance,$' $prof)
if test -z "$new"
then
    echo 'no pilot entered PMGR_ACTIVE state'
    exit 1
fi

n_pilots=$(echo "$new" | wc -l)
if ! test "$n_pilots" = "1"
then
    echo 'can only handle one pilot'
    exit 2
fi

stub=$(echo $new | cut -f 2- -d , | sed -e 's/PMGR_ACTIVE/CANCELED/')
final=$(grep -e ',\(DONE\|FAILED\|CANCELED\),advance,$' $prof)
if test -z "$final"
then
    t_final=$(grep -e 'pmgr.0000,,stopped,' $prof | cut -f 1 -d ',')
    if test -z "$t_final"
    then
        echo "can't determine pmgr termination time"
        exit 3
    fi
    echo "$prof: fixing"
    cp   "$prof"             "$tmp"
    echo "$t_final,$stub" >> "$tmp"
    mv   "$tmp"              "$prof"
else
    echo "$prof: ok"
fi

