from json import loads
from statistics import mean 
import sys
from pprint import pprint
import matplotlib.pyplot as plt

lines = {}

for result_file in sys.argv[1:]:
    print(result_file)

    with open(result_file) as json_file:
        print("= " * 20)
        data = loads(json_file.read())

        # pprint(data["settings"])
        
        # name for each line in plot
        label = data["settings"]["replicas"] + "pod-" + data["settings"]["resources.limits.cpu"] + "-" + data["settings"]["resources.limits.memory"]
        
        if label in lines:
            lines[label]["x"].append(int(data["settings"]["users"]))
            # lines[label]["x"].append(float(data["locust"]["Requests/s"]))
        else:
            lines[label] = {"x":[], "y":[]}
            lines[label]["x"].append(int(data["settings"]["users"]))
            # lines[label]["x"].append(float(data["locust"]["Requests/s"]))

        
        # lines[label]["y"].append(int(data["locust"]["Average response time"]))
        # lines[label]["y"].append(int(float(data["settings"]["users"])))


        # pprint(data["locust"])

        for container in data["cpu"]["data"]["result"]:
            print("cpu -", container["metric"]["container"], ":", mean([float(x[1]) for x in container["values"]]))
            if container["metric"]["container"] == "prometheus-node-exporter":
                lines[label]["y"].append(int(mean([float(x[1]) for x in container["values"]])*1000))
        
        for container in data["memory"]["data"]["result"]:
            print("memory -", container["metric"]["container"], ":", mean([float(x[1]) for x in container["values"]]))  
            # if container["metric"]["container"] == "node":
            #     lines[label]["y"].append(int(mean([float(x[1]) for x in container["values"]])/1000))

# print(lines)

for line in lines:
    #print("* " * 30)
    #print(lines[line])
    plt.plot(lines[line]["x"], lines[line]["y"], label = line)

plt.xlabel('RPS') 
# naming the y axis 
plt.ylabel('Users')

plt.title('Number of users generate request')
plt.legend(loc='upper left')

fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = 20
fig_size[1] = 13
plt.rcParams["figure.figsize"] = fig_size

plt.show()