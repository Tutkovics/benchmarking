import json
import sys

def print_datas(json_file):
    with open( json_file ) as json_result:
        data = json.load(json_result)
        last_qps = -1 #because show 0 qps

        for measurement in data["measurements"]:
            print(str(measurement["requested_qps"]) + "," + str(measurement["actualQPS"]) + "," + str(measurement["cpu_used"]/ int(data["benchmark_time"])) + "," + str(measurement["memory_used"]/ int(data["benchmark_time"])) )
            #last_qps = measurement["actualQPS"]

if __name__ == "__main__":
    if len(sys.argv) < 2 :
        # not enough parameter was given
        print("Please give results json file")
        sys.exit(-1)
    else:
        for json_file in sys.argv[1:]:
            # call function to add new plot (each file will give new line)
            print_datas(json_file) 