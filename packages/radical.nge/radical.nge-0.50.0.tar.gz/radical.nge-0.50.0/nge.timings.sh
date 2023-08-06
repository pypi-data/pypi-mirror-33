#!/bin/sh

. ve/bin/activate
radical-stack

for n in 1 2 4 8 16 32 64 128 256 512 1024
do
  echo "##################################### $n ##############################"
# ./examples/00_nge.py $n
  ./examples/00_rp.py $n
done

