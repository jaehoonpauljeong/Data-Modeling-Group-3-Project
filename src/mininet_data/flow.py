import json
import requests
import traceback
from flow_statistics import FlowStatistics
from flow_retrieval import FlowRetrieval

class FlowManagement:
	def __init__(self):
		self.flow_retrieval = FlowRetrieval()
		self.flow_statistics = FlowStatistics()
		try:
			self.host_list = self.flow_statistics.list_of_hosts()
			self.switch_list = self.flow_statistics.list_of_switches()
		except Exception as e:
			traceback.print_exc()
			print(f" [ERROR] Failed to initialize FlowManagement: {e}")

	def add_path_flow(self, path_list):
		try:
			edges_source_dest = self.flow_statistics.edges_source_dest()
			edges = self.flow_statistics.edges()
		except Exception as e:
			traceback.print_exc()
			print(f" [ERROR] Failed to retrieve edges: {e}")
			return
		
		# Finding edge-id of the edge connecting source and destination nodes
		edge_ids = self._find_edge_ids(path_list, edges_source_dest)
		
		# Finding source and destination port number
		source_ports, dest_ports = self._find_ports(edge_ids, edges)
		
		# Adding flows into the switches
		base_url = 'http://172.18.0.2:8181/restconf/config/opendaylight-inventory:nodes/node/'
		tail_url = '/table/0/flow/'
		headers = {'Content-Type': 'application/xml', 'Accept': 'application/xml'}
		src_host = path_list[0][5:]
		dest_host = path_list[-1][5:]
		
		for m in range(1, len(path_list) - 1):
			node_id = path_list[m]
			end_url = self._get_next_flow_id(node_id)
			url = f"{base_url}{node_id}{tail_url}{end_url}"
			port = source_ports[m].split(':')[-1]
			
			data = f"""<?xml version='1.0' encoding='UTF-8' standalone='no'?>
<flow xmlns='urn:opendaylight:flow:inventory'>
	<priority>10</priority>
	<flow-name>my_flow</flow-name>
	<id>{end_url}</id>
	<hard-timeout>0</hard-timeout>
	<table_id>0</table_id>
	<match>
		<ethernet-match>
			<ethernet-source>
				<address>{src_host}</address>
			</ethernet-source>
			<ethernet-destination>
				<address>{dest_host}</address>
			</ethernet-destination>
		</ethernet-match>
	</match>
	<instructions>
		<instruction>
			<order>0</order>
			<apply-actions>
				<action>
					<order>0</order>
					<output-action>
						<max-length>65535</max-length>
						<output-node-connector>{port}</output-node-connector>
					</output-action>
				</action>
			</apply-actions>
		</instruction>
	</instructions>
	<cookie>3026418949592973326</cookie>
	<idle-timeout>0</idle-timeout>
</flow>
			"""
			try:
				response = requests.put(url, data=data, headers=headers, auth=('admin', 'admin'))
				if response.status_code in [200, 201]:
					print(f" [INFO] Successfully added new flow on switch {node_id}")
				else:
					print(f" [ERROR] Failed to add flow to switch {node_id}")
					print(f"         Status code: {response.status_code}")
					print(f"         Response: {response.text}")
			except Exception as e:
				traceback.print_exc()
				print(f" [ERROR] Failed to add flow to switch {node_id}: {e}")

	def _find_edge_ids(self, path_list, edges_source_dest):
		edge_ids = []
		for i in range(len(path_list) - 1):
			edge_source = path_list[i]
			edge_dest = path_list[i + 1]
			for edge in edges_source_dest:
				if edge['source'] == edge_source and edge['destn'] == edge_dest:
					edge_ids.append(edge['id'])
					break
		return edge_ids

	def _find_ports(self, edge_ids, edges):
		source_ports = []
		dest_ports = []
		for edge_id in edge_ids:
			for edge in edges:
				if edge['id'] == edge_id:
					source_ports.append(edge['source-tp'])
					dest_ports.append(edge['destn-tp'])
					break
		return source_ports, dest_ports

	def _get_next_flow_id(self, node_id):
		id_list = self.flow_retrieval.get_flow_ids(node_id)
		if not id_list:
			return '0'
		try:
			last_id = int(id_list[-1])
			return str(last_id + 1)
		except ValueError:
			return '0'
