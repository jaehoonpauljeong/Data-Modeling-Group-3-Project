from mininet.net import Mininet
from mininet.node import RemoteController

def setup_mininet_ring(net):
	#CREATE HOSTS
	h1 = net.addHost('h1', ip='10.0.0.1')
	h2 = net.addHost('h2', ip='10.0.0.2')
	h3 = net.addHost('h3', ip='10.0.0.3')
	h4 = net.addHost('h4', ip='10.0.0.4')
	h5 = net.addHost('h5', ip='10.0.0.5')

	#CREATE SWITCHES
	s1 = net.addSwitch('s1')
	s2 = net.addSwitch('s2')
	s3 = net.addSwitch('s3')
	s4 = net.addSwitch('s4')
	s5 = net.addSwitch('s5')

	#CREATE LINKS BETWEEN SWITCHES AND HOSTS
	net.addLink(h1, s1, delay='10ms')
	net.addLink(h2, s2, delay='10ms')
	net.addLink(h3, s3, delay='10ms')
	net.addLink(h4, s4, delay='10ms')
	net.addLink(h5, s5, delay='10ms')

	#CREATE LINKS BETWEEN SWITCHES AND SWITCHES
	net.addLink(s1, s2, delay='10ms')
	net.addLink(s2, s3, delay='10ms')
	net.addLink(s3, s4, delay='10ms')
	net.addLink(s4, s5, delay='10ms')
	net.addLink(s5, s1, delay='10ms')

	return net

def setup_mininet_mesh(net):
	#CREATE HOSTS
	host1 = net.addHost('h1')
	host2 = net.addHost('h2')
	host3 = net.addHost('h3')
	host4 = net.addHost('h4')
	host5 = net.addHost('h5')
	
	#CREATE SWITCHES
	switch1 = net.addSwitch('s1')
	switch2 = net.addSwitch('s2')
	switch3 = net.addSwitch('s3')
	switch4 = net.addSwitch('s4')
	switch5 = net.addSwitch('s5')
	switch6 = net.addSwitch('s6')

	#CREATE LINKS BETWEEN SWITCHES AND HOSTS
	net.addLink(host1, switch1, delay='10ms')
	net.addLink(host2, switch1, delay='10ms')
	net.addLink(host3, switch2, delay='10ms')
	net.addLink(host4, switch3, delay='10ms')
	net.addLink(host5, switch3, delay='10ms')

	#CREATE LINKS BETWEEN SWITCHES AND SWITCHES
	net.addLink(switch1, switch2, delay='10ms')
	net.addLink(switch1, switch4, delay='10ms')
	net.addLink(switch1, switch6, delay='10ms')
	net.addLink(switch4, switch5, delay='10ms')
	net.addLink(switch5, switch6, delay='10ms')
	net.addLink(switch5, switch2, delay='10ms')
	net.addLink(switch5, switch3, delay='10ms')
	net.addLink(switch2, switch3, delay='10ms')

	return net

def setup_mininet(choice):
	net = Mininet(controller=RemoteController)
	net.addController('c0', ip='172.18.0.2', port=6633)

	if choice == '1':
		net = setup_mininet_ring(net)
	elif choice == '2':
		net = setup_mininet_mesh(net)
	else:
		print("Something went wrong. Please try again.")
		return None

	for h in net.hosts:
		h.cmd('hostname %s' % h.name)
		h.setMAC('00:00:00:00:00:0%s' % h.name[1])

	net.start()
	return net
