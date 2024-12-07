# Project (Data Modeling for Intelligent Networks and Security)

**Authors:** Dalia Lablack, Mathieu Stenzel

## Setup

This setup has been tested the following environment:

- Ubuntu 22.04.3 LTS
- Docker version 27.2.1

1. Clone the repository to your computer and enter the directory:  
   `git clone <GitHub-URL> && cd <repository-name>`
2. Execute the script to build the Docker images and run the containers:  
   `src/run_containers.sh`
3. Execute the script to run the Python application:  
   `src/run_application.sh`

## Example walkthrough of the application

**Important:** The there are two different names per host and switch. This is due to use of Mininet and OpenDaylight, which have different naming conventions. The mapping is as follows:

- `h1`, `h2`, ... (in Mininet) correspond to `host:00:00:00:00:00:01`, `host:00:00:00:00:00:02`, ... (in OpenDaylight).
- `s1`, `s2`, ... (in Mininet) correspond to `openflow:1`, `openflow:2`, ... (in OpenDaylight).

This is an example to show the functionality of the application:

1. Chose the topology "Ring" by entering "1" in the terminal
2. Chose the option "Measure latency" by entering "2" in the terminal
3. By performing step 2 a few times you can see that the latency between `h2` and `h3` is higher than the average latency between the other hosts. This is due to the fact that OpenDaylight uses the Spanning Tree Protocol (STP) to prevent loops in the network. The loop of the Ring topology is broken by blocking the link between `s2` and `s3`. This causes the traffic between `h2` and `h3` to take a longer path.
4. To optimize the routing between `h2` and `h3`, we can use the "Optimize path between two hosts" functionality. To do this, enter "3" in the terminal.
5. Enter the names of the two hosts you want to optimize the path between. In this case, enter the option `2` and then `3`. The output will show the shortest path between the two hosts, which passes via `s2` and `s3`.
6. To apply the optimized path, enter "y" or "Y" in the terminal. This will add the flow rules to the switches to forward the traffic between `h2` and `h3` (in both directions) via the shortest path.
7. If you measure the latency between the hosts again, you will see that the latency between `h2` and `h3` is now close to the average latency between the other hosts.

To visualize the current topology run the Jupyter Notebook `src/visualization/visualize_traffic.ipynb`. (The easiest way to run the notebook is to use the Jupyter extension in Visual Studio Code.)

**Note:** Before choosing a new topology you should reset the network. This can be done easily be reexecuting the script `src/run_containers.sh`. You can then restart the script `src/run_application.sh` and use a different topology.
