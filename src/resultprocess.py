from json import loads
from statistics import mean 
import sys
from pprint import pprint

for result_file in sys.argv[1:]:
    print(result_file)

    with open(result_file) as json_file:
        print("= " * 20)
        data = loads(json_file.read())

        pprint(data["settings"])
        pprint(data["locust"])

        for container in data["cpu"]["data"]["result"]:
            print("cpu -", container["metric"]["container"], ":", mean([float(x[1]) for x in container["values"]]))
        
        for container in data["memory"]["data"]["result"]:
            print("memory -", container["metric"]["container"], ":", mean([float(x[1]) for x in container["values"]]))  

        