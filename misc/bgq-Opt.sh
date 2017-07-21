#!/bin/bash

queue=default
acct=PSFMat
time=60


nodes=128
nthreads=32
mode=c1


bin=qmcpack
bindir=/soft/applications/qmcpack/current/build_XL_real/bin

intemplate=Opt.xml
title=bgq.Opt-QP-HF-${mode}_p${nodes}x${nthreads}.`date +"%m-%d-%y_%H%M"`

qmcin=$intemplate
qmcout=${title}

qsub -A $acct -q $queue -n $nodes -t $time -O ${qmcout} --mode $mode --env BG_SHAREDMEMSIZE=32:OMP_NUM_THREADS=${nthreads} $bindir/$bin $qmcin
