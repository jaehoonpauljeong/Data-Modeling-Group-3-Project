import json
import requests
import traceback

class FlowRetrieval:

	def __init__(self):
		self.base_url = 'http://172.18.0.2:8181/restconf/operational/opendaylight-inventory:nodes/node/'
		self.tail_url = '/table/0/'
		self.header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
		self.auth = ('admin', 'admin')

	def retrieve_flow(self, switch):
		url = self.base_url + switch + self.tail_url
		try:
			response = requests.get(url, auth=self.auth, headers=self.header)
			response.raise_for_status()
			flow_list = response.json().get('flow-node-inventory:table', [])[0].get('flow', [])
		except requests.RequestException as e:
			traceback.print_exc()
			print(f"Error in retrieving flow from switch {switch}: {e}")
			return []
		except (IndexError, KeyError) as e:
			traceback.print_exc()
			print(f"Unexpected response structure: {e}")
			return []
		return flow_list

	def get_flow_ids(self, switch):
		flow_list = self.retrieve_flow(switch)
		flow_id_list = []
		for flow in flow_list:
			flow_id_list.append(flow.get('id', ''))
		return flow_id_list
