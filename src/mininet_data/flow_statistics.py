import json
import requests
import traceback

class FlowStatistics:
	BASE_URL = 'http://172.18.0.2:8181/restconf/operational'
	AUTH = ('admin', 'admin')

	def __init__(self):
		self.stat_node_list = self.statistics()
		response = self.get_topology()
		self.tp_nodes = response.get('node', [])
		self.tp_links = response.get('link', [])

	def statistics(self):
		node_list = []
		try:
			response = requests.get(f'{self.BASE_URL}/opendaylight-inventory:nodes/', auth=self.AUTH)
			nodes = response.json().get('nodes', {}).get('node', [])
		except Exception:
			traceback.print_exc()
			return []
		for node in nodes:
			node_info = {
				'node-id': node['id'],
				'node-connector': self.parse_node_connectors(node['node-connector'])
			}
			node_list.append(node_info)
		return node_list

	def parse_node_connectors(self, connectors):
		connector_list = []
		for connector in connectors:
			connector_id = connector['id'].split(':')
			node_connector = {
				'id': connector_id[0] + ':' + connector_id[1] if 'LOCAL' in connector_id else connector['id'],
				'state': {
					'link-down': connector['flow-node-inventory:state']['link-down'],
					'blocked': connector['flow-node-inventory:state']['blocked'],
					'live': connector['flow-node-inventory:state']['live']
				},
				'port-number': connector['flow-node-inventory:port-number'],
				'packets-transmitted': connector['opendaylight-port-statistics:flow-capable-node-connector-statistics']['packets']['transmitted'],
				'packets-received': connector['opendaylight-port-statistics:flow-capable-node-connector-statistics']['packets']['received'],
				'status': connector.get('stp-status-aware-node-connector:status', '')
			}
			connector_list.append(node_connector)
		return connector_list

	def node_connector_state(self, nc_id):
		for node in self.stat_node_list:
			for connector in node['node-connector']:
				if connector['id'] == nc_id:
					return connector['state']['link-down']
		return None

	def getNodeConnectors(self, node_id):
		nc_list = []
		for node in self.stat_node_list:
			if node['node-id'] == node_id:
				nc_list.extend([connector['id'] for connector in node['node-connector'] if connector['port-number'] != 'LOCAL'])
		return nc_list

	def port_number(self, nc_id):
		for node in self.stat_node_list:
			for connector in node['node-connector']:
				if connector['id'] == nc_id:
					return connector['port-number']
		return None

	def total_packets(self, nc_id):
		for node in self.stat_node_list:
			for connector in node['node-connector']:
				if connector['id'] == nc_id:
					return connector['packets-transmitted'] + connector['packets-received']
		return 0

	def get_topology(self):
		try:
			response = requests.get(f'{self.BASE_URL}/network-topology:network-topology/', auth=self.AUTH)
			return response.json().get('network-topology', {}).get('topology', [])[0]
		except Exception:
			traceback.print_exc()
			return {}

	def list_of_nodes(self):
		return [node['node-id'] for node in self.tp_nodes]

	def list_of_switches(self):
		return [node for node in self.list_of_nodes() if not node.startswith('host')]

	def list_of_hosts(self):
		return [node for node in self.list_of_nodes() if node.startswith('host')]

	def list_of_edges(self):
		return [link['link-id'] for link in self.tp_links]

	def edges_source_dest(self):
		return [{'id': link['link-id'], 'source': link['source']['source-node'], 'destn': link['destination']['dest-node']} for link in self.tp_links]

	def edges(self):
		return [{'id': link['link-id'], 'source-tp': link['source']['source-tp'], 'destn-tp': link['destination']['dest-tp']} for link in self.tp_links]

	def nodes(self):
		nodelist = []
		for node in self.tp_nodes:
			node_dict = {
				'id': node['node-id'],
				'tp-id': [tp['tp-id'] for tp in node['termination-point']],
				'ap-id': '',
				'mac': '',
				'ip': ''
			}
			if node['node-id'].startswith('host'):
				attachment_point = node['host-tracker-service:attachment-points'][0]
				address = node['host-tracker-service:addresses'][0]
				node_dict.update({
					'ap-id': attachment_point['tp-id'],
					'mac': address['mac'],
					'ip': address['ip']
				})
			nodelist.append(node_dict)
		return nodelist

	def edge_packets(self, edge_id):
		for edge in self.edges():
			if edge['id'] == edge_id:
				source_packets = self.total_packets(edge['source-tp']) or 0
				dest_packets = self.total_packets(edge['destn-tp']) or 0
				return source_packets + dest_packets
		return 0

	def edge_state(self, edge_id):
		for edge in self.edges():
			if edge['id'] == edge_id:
				source_tp_state = self.node_connector_state(edge['source-tp'])
				dest_tp_state = self.node_connector_state(edge['destn-tp'])
				if source_tp_state == 'True' or dest_tp_state == 'True':
					return 0
				return 1
		return 0
