import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import math

"""
Node.csv: 노드 정보
Edge.csv: 엣지 정보

SampledNode.csv: 가중치 계산 시 사용되는 노드 정보
DataAnalysis.xlsx: 노드 세부 정보
"""

data = pd.read_json("./cve_list.txt")

node = pd.DataFrame({"Label": data[0]})

entities = []
for d in data[1]:
    d['entities'] = dict(d['entities'])
    entities.append(d['entities'])
entities = pd.DataFrame(entities)

NodeTable = pd.concat([node, entities], axis = 1)
NodeTable['Id'] = NodeTable.index
NodeTable.to_csv("Node.csv", index = False)

# feature들의 NaN 값 frequency
NaN_COUNT = pd.DataFrame({"NaN" : entities.isnull().sum()})

# Label 칼럼 값들의 frequency
CVE_ID = pd.DataFrame(node.value_counts())

# feature들의 label을 index list에 저장
index = entities.keys()

# .xlsx 파일 생성
with pd.ExcelWriter('DataAnalysis.xlsx') as writer:
    NodeTable.to_excel(writer, sheet_name = 'NodeTable')
    NaN_COUNT.to_excel(writer, sheet_name = 'NaN_COUNT')
    CVE_ID.to_excel(writer, sheet_name = 'CVE_ID')
    for i in index:
        pd.DataFrame(entities[i].value_counts()).to_excel(writer, sheet_name = i)

Sample = NodeTable.loc[:, ['Label', 'V2_CVSS', 'VULNERABILITY', 'STRUCT', 'CWE', 'IMPACT', 'VENDER', 'SOFTWARE']]

def ProcessCVSS(x):
    if 0 <= x and x < 2.5:
        return 0
    elif 2.5 <= x and x < 5:
        return 2.5
    elif 5 <= x and x < 7.5:
        return 5
    else:
        return 7.5
    
for i in range(0, len(Sample)):
    Sample.loc[i, 'V2_CVSS'] = ProcessCVSS(Sample.loc[i, 'V2_CVSS'])

Sample.to_csv("SampledNode.csv", index = False)

software = []
idx = 0

for i in Sample.loc[:, 'SOFTWARE']:
    if type(i) == type('str'):
        l = i.split(" ")
        for j in l:
            software.append([])
            software[idx].append(j)
    else:
        software.append([])
        software[idx].append(math.nan)
    idx += 1

software = software[: idx]

def JaccardSimilarity(list1, list2):
    NaN = [math.nan]
    if list1 == NaN or list2 == NaN:
        return 0
    else:
        union = set(list1).union(set(list2))
        intersection = set(list1).intersection(set(list2))
        return len(intersection)/len(union)

def Similarity(list1, list2):
    count = 0
    for i in range(1,7):
        if type(list1[i]) == type(list2[i]):
            if type(list1[i]) == type('str'):
                if list1[i] == list2[i]:
                    count += 1
            else:
                if not(math.isnan(list1[i]) or math.isnan(list2[i])):
                    if list1[i] == list2[i]:
                        count += 1
    return count

weight = []
idx2 = 0

for i in range(len(Sample)):
    for j in range(i+1, len(Sample)):
        s = Similarity(Sample.loc[i, :].tolist(), Sample.loc[j, :].tolist())
        s += JaccardSimilarity(software[i], software[j])
        s /= 7
        s = round(s, 1)
        if(s != 0):
            weight.append([])
            weight[idx2].append(i)
            weight[idx2].append(j)
            weight[idx2].append(s)
            idx2 += 1
            
weight = pd.DataFrame(weight)
weight.columns = ['Source', 'Target', 'Weight']

weight.to_csv("Edge.csv", index = False)
