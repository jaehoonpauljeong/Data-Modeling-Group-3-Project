import requests
import json
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
import pandas as pd
import my_networkx_module as my_nx

ODL_IP = "http://localhost:8181"
USERNAME = "admin"
PASSWORD = "admin"

def get_restconf_data(url):
    response = requests.get(url, auth=(USERNAME, PASSWORD), headers={"Content-Type": "application/yang-data+json"})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

def get_current_topology():
    url = f"{ODL_IP}/restconf/operational/network-topology:network-topology"
    return get_restconf_data(url)

def get_flow_statistics():
    url = f"{ODL_IP}/restconf/operational/opendaylight-inventory:nodes"
    return get_restconf_data(url)

def analyze_packet_routing(flow_stats):
    """
    Analyze packet routing from flow statistics.
    """
    routes = []
    for node in flow_stats.get("nodes", {}).get("node", []):
        for connected_node in node.get("node-connector", []):
            for port in connected_node.get("id", [])[-1]:
                if port != "L":
                    host_mac = None
                    if "address-tracker:addresses" in connected_node:
                        host_mac = connected_node.get("address-tracker:addresses", [])[0].get("mac", [])
                    packets = connected_node.get("opendaylight-port-statistics:flow-capable-node-connector-statistics", {}).get("packets", {})
                    transmit_packets = packets.get("transmitted", 0)
                    recieve_packets = packets.get("received", 0)
                    routes.append({
                        "node": node.get("id", "N/A"),
                        "port": port,
                        "host": "host:" + host_mac if host_mac else "N/A",
                        "transmitted_packets": transmit_packets,
                        "received_packets": recieve_packets,
                    })
    return routes

def visualize_topology_with_traffic(nodes, links, routes):
    G = nx.MultiDiGraph()  # Use MultiDiGraph to handle multiple edges between nodes

    # Add nodes
    for node in nodes:
        G.add_node(node["node-id"])

    # Add edges from links
    edge_port_map = {}  # Map for source-to-destination ports
    for link in links:
        link_src_node = link["source"]["source-node"]
        link_dst_node = link["destination"]["dest-node"]
        link_src_port = link["source"]["source-tp"].split(":")[-1]  # Extract port number
        G.add_edge(link_src_node, link_dst_node)
        edge_port_map[(link_src_node, link_dst_node)] = link_src_port

    # Map traffic intensity to graph edges
    traffic_intensity = {edge: 0 for edge in G.edges(keys=True)}  # Initialize traffic for all edges
    for route in routes:
        switch = route["node"]
        port = route["port"]
        for (link_src_node, link_dst_node), link_src_port in edge_port_map.items():
            if link_src_node == switch and link_src_port == port:  # Match source and port
                for key in G[link_src_node][link_dst_node]:
                    traffic_intensity[(link_src_node, link_dst_node, key)] += route["transmitted_packets"]
        if "host:" in route["host"]:
            host = route["host"]
            for (link_src_node, link_dst_node), link_src_port in edge_port_map.items():
                if link_src_node == host and link_dst_node == switch:  # Match host and switch
                    for key in G[link_src_node][link_dst_node]:
                        traffic_intensity[(link_src_node, link_dst_node, key)] += route["received_packets"]

    # Calculate edge widths
    edge_widths = {edge: traffic_intensity.get(edge, 0) for edge in G.edges(keys=True)}
    max_width = max(edge_widths.values(), default=1)  # Avoid division by zero
    normalized_widths = {edge: max(1, (width / max_width) * 5) for edge, width in edge_widths.items()}  # Scale widths

    # Create edge labels for traffic intensity
    edge_labels = {edge: f"{traffic_intensity[edge]}" for edge in G.edges(keys=True)}

    visualize_topology(nodes, links, normalized_widths, edge_labels)

def visualize_topology(nodes, links, normalized_widths=None, edge_labels=None):
    G = nx.MultiDiGraph()

    for node in nodes:
        G.add_node(node["node-id"])

    if edge_labels:
        for link in links:
            source = link["source"]["source-node"]
            destination = link["destination"]["dest-node"]
            label = edge_labels[(source, destination, 0)]
            G.add_edge(source, destination, w=label)
    else:
        G.add_edges_from([(link["source"]["source-node"], link["destination"]["dest-node"]) for link in links])
    
    # Generate the Graph
    plt.figure(figsize=(12, 6))
    pos = nx.spring_layout(G, seed=7, k=0.3)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_shape="s", node_color="none")

    # Draw node labels
    labels = {node["node-id"]: node["node-id"] for node in nodes}
    nx.draw_networkx_labels(G, pos, labels, bbox=dict(facecolor="skyblue", edgecolor='black', boxstyle='round,pad=0.2'))

    # Draw curved edges with varying thickness if traffic intensity provided
    if normalized_widths:
        rad = 0.25
        for (u, v, key) in G.edges(keys=True):
            width = normalized_widths.get((u, v, key), 2)  # Default width to 2 if not found
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=width, edge_color="gray", connectionstyle=f'arc3,rad={rad}')
        edge_weights = nx.get_edge_attributes(G, "w")
        my_nx.my_draw_networkx_edge_labels(G, pos, edge_labels=edge_weights, rotate=False, rad=rad)
    else:
        nx.draw_networkx_edges(G, pos, edge_color="gray", arrows=False)

    # Add title and display
    title = "Network Topology"
    if normalized_widths:
        title += " (with Traffic Intensity)"
    plt.title(title)
    plt.show()
