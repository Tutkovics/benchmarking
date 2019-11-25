#!/usr/bin/env python3

# Usage: draw_graph.py [cpu|memory] [resultfile1 [... resultfile2]]

import matplotlib.pyplot as plt 
import json
import sys

def plot_from_file(json_file):
    # function to add new line for graph
    with open( json_file ) as json_result:
        data = json.load(json_result)

        x = []
        y = []  

        for measurement in data["measurements"]:
            # append all data point from measurement
            x.append(measurement["actualQPS"])
            # get memory or cpu  usage depends on command line variable
            y.append(measurement[str(sys.argv[1]) + "_used"] / int(data["benchmark_time"]))

        plt.plot(x, y, label=data["number_of_pod"] + "# pods")


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
            plt.ylabel("mCPU")
            plt.title('CPU usage in different qps') 
        elif(str(sys.argv[1]) == "memory"):
            plt.ylabel("memory")
            plt.title('Memory usage in different qps') 

        # visualize
        plt.legend(loc='upper left')
        plt.show()