#!/bin/sh

num="0 1 2"
num="0 1 2 3 4 5 6 7 8 9"

for t in 1 2 3 4 5
do
    echo "==== $t ===================================="
    for i in $num
    do
        for j in $num
        do
            for k in $num
            do
                for l in $num
                do
                    echo "$i$j$k$l $t ------------------------------------"
                    python docs/architecture/component_termination.py $t >/dev/null 
                done
            done
        done
    done
done

