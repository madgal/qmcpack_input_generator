#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import matplotlib.pyplot as plt

os.system("OptProgress.pl *scalar.dat | sort -k 2 > opt_energy.dat")

filein = open("opt_energy.dat","r")


x=[]
y=[]
sd=[]
for row in filein:
        row = row.split("  ")
        x.append(int(row[0]))
        y.append(float(row[1]))
        sd.append(float(row[2]))
filein.close()

fig = plt.figure(figsize = (10,9))
ax = plt.subplot(111)

plt.plot(x,y,'b*')

plt.errorbar(x,y   , yerr=sd,fmt="o")

plt.savefig("OptProg.png")
plt.show()
