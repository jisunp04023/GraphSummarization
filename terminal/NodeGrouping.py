import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import math
import csv

with open('Edge.csv', newline = '') as f:
    reader = csv.reader(f)
    wg = list(reader)
wg = wg[1:]

df = pd.DataFrame(wg)
df = df.astype({2: 'float'})

weight = df[2].max()
weight = str(weight)

supernode = []
def IsSupernode(n):
    for i in range(0, len(supernode)):
        for j in range(0, len(supernode[i])):
            if n == supernode[i][j]:
                return i
    return -1

superedge = []
idx = 0

for i in range(0, len(wg)):
    if wg[i][2] == weight:
        if IsSupernode(wg[i][0]) >= 0: # source node가 supernode에 존재한다면
            row = IsSupernode(wg[i][0])
            supernode[row].append(wg[i][1])
        else:
            supernode.append([])
            supernode[len(supernode)-1].append(wg[i][0])
            supernode[len(supernode)-1].append(wg[i][1])
    else:
        superedge.append([])
        superedge[idx].append(wg[i][0])
        superedge[idx].append(wg[i][1])
        superedge[idx].append(wg[i][2])
        idx += 1

for i in range(0, len(superedge)):
    for j in range(0, 2):
        if IsSupernode(superedge[i][j]) >= 0:
            row = IsSupernode(superedge[i][j])
            superedge[i][j] = supernode[row][0]

output = []

def IsSuperedge(s, t):
    for i in range(0, len(output)):
        if (s == output[i][0]) and (t == output[i][1]):
            return i
    return -1

idx2 = 0

for i in range(0, len(superedge)):
    s = superedge[i][0]
    t = superedge[i][1]
    w = superedge[i][2]
    if IsSuperedge(s, t) >= 0:
        # 있을 경우
        row = IsSuperedge(s, t)
        output[row][2] = float(output[row][2]) + float(w)
        output[row][3] += 1
    else:
        output.append([])
        output[idx2].append(s)
        output[idx2].append(t)
        output[idx2].append(w)
        output[idx2].append(1)
        idx2 += 1

for i in range(0, len(output)):
    if output[i][3] > 1:
        output[i][2] /= output[i][3]
        output[i][2] = round(output[i][2], 1) # 반올림

output = pd.DataFrame(output)

output.columns = ['Source', 'Target', 'Weight', 'Count']

output = output.drop(['Count'], axis = 1)

output.to_csv("Edge.csv", index = False)