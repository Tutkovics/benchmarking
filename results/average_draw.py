#!/usr/bin/env python3

# Usage: average_draw.py [cpu|memory] [resultfile1 [... resultfile2]]

import matplotlib.pyplot as plt 
import json
import sys
import os
import statistics

#all_collections = {}
datas = {}

def plot_from_file(json_files):
    # function to add new line for graph

    for json_file in json_files:

        with open(json_file) as json_result:
            raw_data = json.load(json_result)
            select_by_pod_number(raw_data, raw_data["number_of_pod"])


def select_by_pod_number(raw_data, pod_number):
    
    tmp = []
    last_qps = -1

    for measurement in raw_data["measurements"]:
     
        if last_qps < measurement["actualQPS"]:
            tmp.append([measurement["requested_qps"], measurement["actualQPS"], measurement["cpu_used"]/ int(raw_data["benchmark_time"]), measurement["memory_used"]/ int(raw_data["benchmark_time"])])
            last_qps = measurement["actualQPS"]

    if str(pod_number) in datas:
        datas[str(pod_number)].append(tmp)
    else:
        datas[str(pod_number)] = []


def data_process_and_visualize():

    for key in datas:
        colletcion = {}

        for measurement in datas[key]:
            for i in range(len(measurement)):
                if str(measurement[i][0]) in colletcion:
                    # already key presented in dictionary
                    colletcion[str(measurement[i][0])]["actual"].append(measurement[i][1])
                    colletcion[str(measurement[i][0])]["cpu"].append(measurement[i][2])
                    colletcion[str(measurement[i][0])]["memory"].append(measurement[i][3])

                else:
                    colletcion[str(measurement[i][0])] = {
                        "actual" : [measurement[i][1]],
                        "cpu" : [measurement[i][2]],
                        "memory" : [measurement[i][3]]
                    }

        x = []
        y = []

        for point in colletcion:
            x.append(statistics.mean(colletcion[point]["actual"]))
            if str(sys.argv[1]) == "cpu":
                y.append(statistics.mean(colletcion[point]["cpu"]))
            elif str(sys.argv[1]) == "memory":
                y.append(statistics.mean(colletcion[point]["memory"]))
        #print(x)
        #print(y)

        plt.plot(x, y, label=key+"# pods")

    if(str(sys.argv[1]) == "cpu"):
        plt.ylabel("SUM CPU / sec")
        plt.title('CPU usage in different qps') 
    elif(str(sys.argv[1]) == "memory"):
        plt.ylabel("SUM memory / sec") #
        plt.title('Memory usage in different qps') 

    # visualize
    plt.xlabel("QPS")
    plt.legend(loc='lower right')

    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 3 :
        # not enough parameter was given
        print("Please choose memory or cpu usage and give results json file")
        sys.exit(-1)
    else:
        # call function to calculate average and add datapoints
        plot_from_file(sys.argv[2:]) 
        data_process_and_visualize()
        #print_data()