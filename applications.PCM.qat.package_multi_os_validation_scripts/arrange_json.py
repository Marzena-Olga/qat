import json
with open(r'./config/VM_OS_list.json') as json_file:
    data = json.load(json_file)
    for p in data:
        print(p)
with open(r'./config/VM_OS_list.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)
