#parse yaml file
from yaml import load, dump
import docker
import time

client = docker.from_env()


def create(yaml, stream, graph):
    #base = os.path.dirname(os.path.realpath(__file__))
    global log
    log = stream
    nodes = dict()
    edges = dict()
    #with open(base + "/example.yml", 'r') as file:
    try:
    #   config = (load(file))
        config = load(yaml)
        print(config)
        nodes = config["nodes"]
        edges = config["edges"]
        if "image" in config:
            image = config["image"]
        else:
            image = "ofenstichloch/nemu"
    except Exception as e:
        log.write("Error reading config file" + e.message + "</br>")
    startperf = time.perf_counter()
    log.write("Starting at "+str(startperf)+"</br>")
    t1 = time.perf_counter()
    networks = genSwitches(nodes)
    t2 = time.perf_counter()
    log.write("Perf: Switches "+str(t2-t1) + "</br>")
    log.write("############## Finished creating network bridges (switches) ##############" + "</br>")
    t1 = time.perf_counter()
    genNodes(nodes,image)
    t2 = time.perf_counter()
    log.write("Perf: Nodes "+str(t2-t1) + "</br>")
    log.write("############## Finished creating nodes ##############" + "</br>")
    t1 = time.perf_counter()
    setupLinks(nodes, networks, edges)
    t2 = time.perf_counter()
    log.write("Perf: Links " + str(t2-t1) + "</br>")
    t1 = time.perf_counter()
    startNodes(nodes, networks, edges)
    t2 = time.perf_counter()
    log.write("Perf: Start " + str(t2-t1) + "</br>")
    endperf = time.perf_counter()
    log.write(str(nodes) + "</br></br>")
    log.write(str(edges) + "</br></br>")
    log.write(str(networks) + "</br></br>")
    log.write("############## Finished creating Docker components #############</br>")
    log.write("Time taken: "+str(endperf-startperf)+"</br>")
    log.write("<a href='/main'>Continue</a>")
    graph.append(nodes)
    graph.append(edges)
    with open('/tmp/nemu.graph', 'w') as outfile:
        dump(graph, outfile, default_flow_style=False)


#Determine docker vswitches aka bridges
#v1: Every router serves its own network -> Every router needs a switch
def genSwitches(nodes):
    networks = dict()
    for name, node in nodes.items():
        if node["type"] == "switch":
            ###Setup network configurations###
            client.networks.create(name, enable_ipv6=True)
            networks["name"] = True
            log.write("Created network "+name+"</br>")
    return networks


#Build Docker properties per node
def genNodes(nodes, image):
    for name, node in nodes.items():
        if node["type"] == "switch":
            continue
        ###Setup loading mode (router/client)###
        param = ""
        if "entrypoint" in node:
            param = node["entrypoint"]
        if node["type"] == "router":
            entry = "/usr/bin/loop client " + param
        else:
            entry = "/usr/bin/loop client " + param

        volumes = {'/tmp/'+name: {'bind': '/var/log', 'mode': 'rw'}}
        if "volumes" in node:
            volumes = node["volumes"]

        client.containers.create(image,
                                 name=name, hostname=name, entrypoint=entry, privileged=True, volumes=volumes)
        net = client.networks.get("bridge")
        net.disconnect(name)
        log.write("Created node " + name + "</br>")


def setupLinks(nodes, networks, edges):
        ###Setup network links###
        for edge in edges:
            if edge[0] in networks:
                #This is a switch
                client.networks.get(edge[0]).connect(edge[1])
                log.write("Connected node " + edge[1] + " to " + edge[0] + "</br>")

            elif edge[1] in networks:
                # This is not a switch
                client.networks.get(edge[1]).connect(edge[0])
            else:
                raise Exception("A link must connect a node to a switch")


def startNodes(nodes, networks, edges):
    for name, node in nodes.items():
        if node["type"] == "switch":
            continue
        nodestart=time.perf_counter()
        container = client.containers.get(name)
        container.start()
        log.write("Started "+name + "</br>")
        #Remove old default route via host
        container.exec_run("route del default", privileged=True)
        log.write("Removed default route on "+name + "</br>")
        #Add new default route to first router on this network

        log.write("Added new default route on " + name + " via " + gw + "</br>")
        #Add netem configuration
        # for edge in edges:
        #     #If there are additional netem options
        #     if len(edge) == 4:
        #         #is it this node?
        #         if edge[0] == name or edge[1] == name:
        #             options = edge[2]
        #             print(options)
        #             cmd = "/usr/bin/setupNemu "+edge[3]+" \""
        #             args = '#'.join(options)
        #             args = args.replace("#", "\" \"")
        #             cmd = cmd + args + "\""
        #             container.exec_run(cmd, privileged=True)
        #             log.write("Added netem command to node "+name+": "+cmd+"</br>")
        log.write("Perf: Singlestart "+str(time.perf_counter()-nodestart) + "</br>")
