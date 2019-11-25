#!/usr/bin/env python3

import matplotlib.pyplot as plt 
import json


with open( "./results/nginx-8-50m-200Mi-20191125132111.json" ) as json_result:
    data = json.load(json_result)
    
    x = []
    y = []

    for measurement in data["measurements"]:
        x.append(measurement["actualQPS"])
        y.append(measurement["cpu_used"]/6)

plt.plot(x, y) 
plt.xlabel("QPS")
plt.ylabel("mCPU")
plt.title('My first graph!') 
plt.show()