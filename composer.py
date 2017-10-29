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
        log.write("Error reading config file\n" + e.message + "</br>")
    startperf = time.perf_counter()
    startcpu = time.process_time()
    log.write("Starting at "+str(startperf)+" with process time of "+str(startcpu)+"</br>")
    networks = genSwitches(nodes)
    log.write("############## Finished creating network bridges (switches) ##############" + "</br>")
    genNodes(nodes,image)
    log.write("############## Finished creating nodes ##############" + "</br>")
    setupLinks(nodes, networks, edges)
    startNodes(nodes, networks, edges)
    endperf = time.perf_counter()
    endcpu = time.process_time()
    log.write(str(nodes) + "</br></br>")
    log.write(str(edges) + "</br></br>")
    log.write(str(networks) + "</br></br>")
    log.write("############## Finished creating Docker components #############</br>")
    log.write("Time taken: "+str(endperf-startperf)+"   CPU time taken: "+str(endcpu-startcpu)+"</br>")
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
            #Determine subnet
            networks[name] = dict()
            numNetworks = len(networks)
            if numNetworks > 254:
                raise Exception("Too many subnetworks")
            networks[name]["net"] = "10.100."+str(numNetworks)+".0/24"
            networks[name]["prefix"] = "10.100."+str(numNetworks)+"."
            networks[name]["nextIP"] = 2
            networks[name]["router"] = ""
            dhcp = "10.100."+str(numNetworks)+".0/24"
            ipam_pool = docker.types.IPAMPool(
                subnet=networks[name]["net"],
                iprange=dhcp
            )
            ipam_config = docker.types.IPAMConfig(
                pool_configs=[ipam_pool])
            client.networks.create(name, ipam=ipam_config)
            log.write("Created network "+name+" with IP range "+networks[name]["net"] + "</br>")
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
            entry = "/usr/bin/loop router " + param
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
                ip = networks[edge[0]]["prefix"]+str(networks[edge[0]]["nextIP"])
                networks[edge[0]]["nextIP"] += 1
                client.networks.get(edge[0]).connect(edge[1], ip)

                nodes[edge[1]]["ip"] = ip
                nodes[edge[1]]["network"] = edge[0]
                edge.append(ip)
                log.write("Connected node " + edge[1] + " to " + edge[0] + " with IP " + ip + "</br>")
                if nodes[edge[1]]["type"] == "router" and networks[edge[1]]["router"] == "":
                    networks[edge[1]]["router"] = ip

            elif edge[1] in networks:
                # This is not a switch
                ip = networks[edge[1]]["prefix"] + str(networks[edge[1]]["nextIP"])
                networks[edge[1]]["nextIP"] += 1
                client.networks.get(edge[1]).connect(edge[0], ip)
                nodes[edge[0]]["ip"] = ip
                nodes[edge[0]]["network"] = edge[1]
                edge.append(ip)
                log.write("Connected node "+edge[0]+" to "+edge[1]+" with IP "+ip + "</br>")
                if nodes[edge[0]]["type"] == "router" and networks[edge[1]]["router"] == "":
                    networks[edge[1]]["router"] = ip
            else:
                raise Exception("A link must connect a node to a switch")


def startNodes(nodes, networks, edges):
    for name, node in nodes.items():
        if node["type"] == "switch":
            continue
        container = client.containers.get(name)
        container.start()
        log.write("Started "+name + "</br>")
        #Remove old default route via host
        container.exec_run("route del default", privileged=True)
        log.write("Removed default route on "+name + "</br>")
        #Add new default route to first router on this network
        gw = networks[node["network"]]["router"]
        container.exec_run("route add default gw " + gw, privileged=True)
        log.write("Added new default route on " + name + " via " + gw + "</br>")
        #Add netem configuration
        for edge in edges:
            #If there are additional netem options
            if len(edge) == 4:
                #is it this node?
                if edge[0] == name or edge[1] == name:
                    options = edge[2]
                    print(options)
                    cmd = "/usr/bin/setupNemu "+edge[3]+" \""
                    args = '#'.join(options)
                    args = args.replace("#", "\" \"")
                    cmd = cmd + args + "\""
                    container.exec_run(cmd, privileged=True)
                    log.write("Added netem command to node "+name+": "+cmd+"</br>")
