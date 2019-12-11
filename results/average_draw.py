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
            name = json_file.split("/")[1].split("-")[0]
            select_by_pod_number(raw_data, name)


def select_by_pod_number(raw_data, name):
    pod_number = raw_data["number_of_pod"]
    cpu_limit = raw_data["cpu_limit"]
    memory_limit = raw_data["memory_limit"]

    unique = name + ": " + str(pod_number) + "pod-" + cpu_limit + "Cpu-" + memory_limit

    tmp = []
    last_qps = -1

    for measurement in raw_data["measurements"]:
     
        if last_qps < measurement["actualQPS"]:
            tmp.append([measurement["requested_qps"], measurement["actualQPS"], measurement["cpu_used"]/ int(raw_data["benchmark_time"]), measurement["memory_used"]/ int(raw_data["benchmark_time"])])
            last_qps = measurement["actualQPS"]

    if unique in datas:
        datas[unique].append(tmp)
    else:
        datas[unique] = [tmp] # first occurrence was miss


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

        last_qps = -1

        for point in colletcion:
            if last_qps < statistics.mean(colletcion[point]["actual"]):
                x.append(statistics.mean(colletcion[point]["actual"]))
                if str(sys.argv[1]) == "cpu":
                    y.append(statistics.mean(colletcion[point]["cpu"]))
                elif str(sys.argv[1]) == "memory":
                    y.append(statistics.mean(colletcion[point]["memory"]))
                
                last_qps = statistics.mean(colletcion[point]["actual"])

        predicted = 2

        if "-1pod" in key:
            #continue
            predict_own_usage(colletcion,1, predicted, 50, "Predict from 1 pod version")
        elif "-2pod" in key:
            #continue
            predict_own_usage(colletcion,2, predicted, 50, "Predict from 2 pod version")
        elif "-3pod" in key:
            
            predict_own_usage(colletcion,3, predicted, 50, "Predict from 3 pod version")
        elif "-4pod" in key:
            predict_own_usage(colletcion,4, predicted, 50, "Predict from 4 pod version")

        #if str(predicted)+"pod" in key:
        if True: 
            plt.plot(x, y, label=key)

    if(str(sys.argv[1]) == "cpu"):
        plt.ylabel("SUM CPU / sec")
        #plt.title('CPU usage in different qps') 
    elif(str(sys.argv[1]) == "memory"):
        plt.ylabel("SUM memory / sec") #
        #plt.title('Memory usage in different qps') 

    # visualize
    plt.title(str(sys.argv[-1]))
    plt.xlabel("QPS")
    plt.legend(loc='lower right')

    plt.show()

def answer_y(x1, y1, x2, y2, ask_x):
    # answer y number (cpu/memory usage) beetween two point in a given x value
    # use line's normal method Ax + By = Ax1 + By1
    # normalvector values (A,B):
    A = y1 - y2
    B = x2 - x1

    y = ( (A*x1) + (B*y1) - (A*ask_x) ) / B
    #print("Calculate: (" + str(x1) + ', ' + str(y1) + ") ("+ str(x2) +", "+ str(y2)+") " + str(ask_x)+" --> " + str(y))
    return y

def predict_own_usage(raw_data, old_pod_number, new_pod_number, granularity, plot_label):
    # get end of qps (Q):
    last_key = ""
    for key in raw_data:
        last_key = key
    Q = (new_pod_number / old_pod_number) * (statistics.mean(raw_data[last_key]["actual"]))

    # x and y arrays for points
    x = []
    y = []

    # get data points to show
    for ask_qps in range(1, int(Q), granularity):
        last_point = [0,0]

        # only if qps numbers in increment order
        for key in raw_data:
            find_qps = ask_qps * (old_pod_number / new_pod_number)

            tmp_usage = 0
            if(str(sys.argv[1]) == "cpu"):
                tmp_usage = statistics.mean(raw_data[key]["cpu"])
            elif(str(sys.argv[1]) == "memory"):
                tmp_usage = statistics.mean(raw_data[key]["memory"])

            if (find_qps <= statistics.mean(raw_data[key]["actual"])) and (find_qps >= last_point[0]):
                if find_qps == statistics.mean(raw_data[key]["actual"]):
                    x.append(ask_qps)
                    y.append(tmp_usage)
                else:
                    x.append(ask_qps)
                    new_y = answer_y(last_point[0], last_point[1], statistics.mean(raw_data[key]["actual"]), tmp_usage, find_qps )
                    
                    y.append(new_y*(new_pod_number / old_pod_number))
                
            last_point = [statistics.mean(raw_data[key]["actual"]), tmp_usage]

    plt.plot(x,y,label=plot_label)

    



if __name__ == "__main__":
    if len(sys.argv) < 3 :
        # not enough parameter was given
        print("Please choose memory or cpu usage and give results json file")
        sys.exit(-1)
    else:
        # call function to calculate average and add datapoints
        plot_from_file(sys.argv[2:-1]) 
        data_process_and_visualize()
        #for key in datas:
        #    print(key)
        #print(datas["nodejs: 1pod-200mCPU-64Mi"])
        #print_data()