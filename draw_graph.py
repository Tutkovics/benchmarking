#!/usr/bin/env python3

# Usage: draw_graph.py [cpu|memory] [resultfile1 [... resultfile2]]

import matplotlib.pyplot as plt 
import json
import sys
import os

def plot_from_file(json_file):
    # function to add new line for graph
    with open( json_file ) as json_result:
        data = json.load(json_result)

        x = []
        y = []  

        last_qps = -1 #because show 0 qps

        for measurement in data["measurements"]:
            if(measurement["actualQPS"] > last_qps):
                # append all data point from measurement
                x.append(measurement["actualQPS"])
                # get memory or cpu  usage depends on command line variable
                resource_usage = measurement[str(sys.argv[1]) + "_used"] / int(data["benchmark_time"])
                y.append(resource_usage)

                last_qps = measurement["actualQPS"]

        print("# pods: " + data["number_of_pod"])
        if str(data["number_of_pod"]) == str(1):
            print("Call function predict")
            #our_function(data["number_of_pod"], data, 3)
            
            

        plt.plot(x, y, label=data["number_of_pod"] + "# pods")

def our_function(original_pod_number, original_measurements, new_pod_number):
    x = []
    y = []

    for measurement in original_measurements["measurements"]:
        x.append(measurement["actualQPS"])
        y.append(measurement[str(sys.argv[1]) + "_used"] / int(original_measurements["benchmark_time"]) / int(original_pod_number) * new_pod_number)

    plt.plot(x, y, label="Predicted value to: " + str(new_pod_number))
    



if __name__ == "__main__":
    if len(sys.argv) < 3 :
        # not enough parameter was given
        print("Please choose memory or cpu usage and give results json file")
        sys.exit(-1)
    else:
        for json_file in sys.argv[2:]:
            # call function to add new plot (each file will give new line)
            plot_from_file(json_file) 

        # setup label for x-, y-axis and graph title
        if(str(sys.argv[1]) == "cpu"):
            plt.ylabel("SUM mCPU / sec")
            plt.title('CPU usage in different qps') 
        elif(str(sys.argv[1]) == "memory"):
            plt.ylabel("SUM memory / sec") #
            plt.title('Memory usage in different qps') 

        # visualize
        plt.xlabel("QPS")
        plt.legend(loc='lower right')

        plt.show()