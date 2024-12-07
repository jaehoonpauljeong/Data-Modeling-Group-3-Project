import re
import sys
import select

def measure_latency(net):
	hosts = net.hosts
	for i, src in enumerate(hosts):
		for dst in hosts[i+1:]:
			while True:
				result = src.cmd(f'ping -c 1 {dst.IP()}')
				match = re.search(r'time=(\d+\.\d+) ms', result)
				if match:
					latency = float(match.group(1))
					break
				if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
					input()  # Consume the Enter key press
					print("Latency measurement stopped by user.")
					return
				print(f'{src.name}: Failed to ping {dst.name}, retrying... (press Enter to exit)')
			print(f'{src.name} -> {dst.name}: {latency} ms')			
