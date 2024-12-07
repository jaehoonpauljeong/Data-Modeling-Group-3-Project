import requests
import networkx as nx

class TopologyODL:
	def __init__(self):
		self.topology = self.get_topology()
		self.nodes = self.topology['node']
		self.links = self.topology['link']
		self.graph = self.create_graph()
		self.shortest_paths = dict(nx.all_pairs_shortest_path(self.graph))

	def get_topology(self):
		url = 'http://172.18.0.2:8181/restconf/operational/network-topology:network-topology/'
		auth = ('admin', 'admin')
		headers = {
			'Content-Type': 'application/yang-data+json'
		}
		response = requests.get(url, auth=auth, headers=headers)
		if response.status_code == 200:
			response = response.json().get('network-topology', {}).get('topology', [])[0]
			return response
		else:
			print(f"Failed to fetch data ({response.status_code}): {response.text}")
			return None
	
	def create_graph(self):
		G = nx.Graph()
		for node in self.nodes:
			G.add_node(node['node-id'])
		for link in self.links:
			G.add_edge(link['source']['source-node'], link['destination']['dest-node'])
		return G
