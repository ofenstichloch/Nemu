#NEMU: Network emulation in Docker

The program takes a yml graph (as example in example.yml) and creates the corresponding network with Docker containers and bridges.

A Switch is a Docker networking bridge
A Router is a container connected to two or more networks, every router runs the BIRD Internet Routing Daemon with OSPF
A Client is simple Docker container connected to one network, using his router as default gateway. 

Docker provides the infrastructure, BIRD does the routing, netem (iproute2) does the network emulation.

A Link must always be between a switch and a container.
A Switch always has to be connected to at least one router.

## Configuration
A link might have addition info such as:
  delay: The delay on this link. This applies only to packets SENT on this link from the container
    Possible values are as in "tc qdisc change dev eth0 root netem delay 100ms 10ms 25%", where 100ms is the base delay, 10ms the jitter and 25% the correlation between consecutive packets.
      That command in NEMU would be "- [ router,switch, [delay=100ms 10s 25%]]"
  loss: The procentual loss of packets. Also only SENT packages from the container will be dropped. Warning: If dropped on the actual sending machine (Container, not router) the loss is beeing reported to the above layers, thus likely to be resent.
    Possible values as in "tc qdisc change dev eth0 root netem loss 0.3% 25%"
      "- [ router,switch, [loss=0.3% 25%]]"
     
## Running
The program is a Python Flask app. The main App is located in nemu_cli.py and can be started with:
 ./run.sh
This runscript creates a virutalenv with all required pip packages.
Make sure the Docker daemon is running!
You can then access the webinterface at http://127.0.0.1:5000 (yes, still on the dev server)

## Requirements
Host: Docker, virtualenv
App: It requires the following pip packages: tornado, docker, PyYAML, Flask, requests, wtforms (handled by virtualenv)
