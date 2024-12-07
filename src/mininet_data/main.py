from topology_min import setup_mininet
from topology_odl import TopologyODL
from latency import measure_latency
from flow import FlowManagement
from mininet.cli import CLI
from mininet.clean import cleanup
import time

def display_topology_menu():
	print()
	print("Please choose the topology you want to use:")
	print(" [1] Ring")
	print(" [2] Mesh")
	print(" [100] For Exit")
	choice =  input("Enter your choice: ")
	print()
	return choice

def display_action_menu():
	print()
	print("Please choose the action you want to perform:")
	print(" [1] Run Mininet Console")
	print(" [2] Measure latency")
	print(" [3] Optimize path between two hosts")
	print(" [100] For going back to topology selection")
	choice = input("Enter your choice: ")
	print()
	return choice

def handle_topology_choice(choice):
	while True:
		if choice in ['1', '2']:
			return setup_mininet(choice)
		elif choice == '100':
			print("Exiting...")
			return None
		else:
			print("Invalid choice. Please try again...")
			print()
			choice = display_topology_menu()

def handle_action_choice(choice, net):
	while True:
		if choice == '1':
			CLI(net)
			return True
		elif choice == '2':
			measure_latency(net)
			return True
		elif choice == '3':
			T = TopologyODL()
			nodes = T.nodes
			if not any(node['node-id'].startswith('host') for node in nodes):
				print("Nodes not initialized yet. Please perform 'Measure latency' action first.")
				return True
			nodes.sort(key=lambda x: x['node-id'])
			node_arr = []
			for node in nodes:
				node_id = node['node-id']
				if node_id.startswith("host"):
					node_arr.append(node_id)
			print("List of hosts:")
			for i, node in enumerate(node_arr):
				print(f" {i+1}. {node}")
			print()
			src = input("Enter the source host: ")
			dst = input("Enter the destination host: ")
			shortest_path_1 = T.shortest_paths[node_arr[int(src)-1]][node_arr[int(dst)-1]]
			shortest_path_2 = T.shortest_paths[node_arr[int(dst)-1]][node_arr[int(src)-1]]
			print()
			print("Shortest path between '{}' and '{}' is:".format(node_arr[int(src)-1], node_arr[int(dst)-1]))
			print(" ---> ".join(shortest_path_1))
			print()
			choice2 = input("Should this path be pushed to the switches? (Y) ")
			if choice2.lower() == 'y':
				fm = FlowManagement()
				fm.add_path_flow(shortest_path_1)
				time.sleep(5)
				fm.add_path_flow(shortest_path_2)
			return True
		elif choice == '100':
			print("Going back to topology selection...")
			return False
		else:
			print("Invalid choice. Please try again...")
			print()
			choice = display_action_menu()

def cleanup_mininet(net):
	if net is not None:
		net.stop()
	cleanup()

def main():
	print("Welcome to our project!")
	while True:
		net = None
		choice = display_topology_menu()
		net = handle_topology_choice(choice)
		if net is None:
			break
		loop = True
		while loop:
			choice = display_action_menu()
			try:
				loop = handle_action_choice(choice, net)
			except Exception as e:
				print(f"Error: {e}")
				cleanup_mininet(net)
				break
		cleanup_mininet(net)

if __name__ == "__main__":
	main()