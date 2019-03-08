import json
from collections import Counter
import re

with open('../2-Segmentation/slice-event.json') as f:
    slice_event = json.load(f)

num_list = []

for slice in slice_event:
    num = 1
    for i in range(len(slice)):
        if i == len(slice)-1:
            num_list.append(num)
            continue
        if slice[i + 1]['EventType'] == slice[i]['EventType'] and re.findall('ClassName: (.+?);', slice[i]['Action'])[0] == re.findall('ClassName: (.+?);', slice[i+1]['Action'])[0]:
            num += 1
        else:
            num_list.append(num)
            num = 1

calculater = list(dict(Counter(num_list)).items())

all = sum([x[1] for x in calculater])
for c in calculater:
    print(c)
print(float((5391+523))/all)
print(float((5391+523+107))/all)
print(all)