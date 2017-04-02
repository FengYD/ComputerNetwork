#!/usr/bin/env python

"""
Create a 1024-host network, and run the CLI on it.
If this fails because of kernel limits, you may have
to adjust them, e.g. by adding entries to /etc/sysctl.conf
and running sysctl -p. Check util/sysctl_addon.
"""

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.link import TCLink
from jellyfish.topologies.jellyfish import JellyfishTopo
from jelly_routing import setRoutes
import sys
sys.path.append("..")
from tools.tools import iperfTest, minCut
from threading import Timer
import time
import threading
from time import ctime,sleep
import multiprocessing
import random

def JellyfishNet(seed=0, switches=16, nodes=8, ports_per_switch=2, hosts_per_switch=1, bw=1, **kwargs):
    topo = JellyfishTopo(seed, switches, nodes, ports_per_switch, hosts_per_switch, bw)
    return Mininet(topo, **kwargs)

if __name__ == '__main__':
    setLogLevel( 'info' )
    
    switches_ = int(sys.argv[1])
    nodes_    = int(sys.argv[2])
    ports_per_switch_=int(sys.argv[3])
    hosts_per_switch_=int(sys.argv[4])
    seed_     = int(sys.argv[5])
    network = JellyfishNet(seed=seed_, switches=switches_, nodes=nodes_, ports_per_switch=ports_per_switch_, hosts_per_switch=hosts_per_switch_, switch=OVSSwitch, link=TCLink, controller=RemoteController, autoSetMacs=True)
    network.start()
    setRoutes(network)
    time_limit = 600
    #network.pingAll()
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    #for i in [nodes_/2]:
    for i in range(nodes_/2,0,-max(1,nodes_/20)):
        j   = 0
        if(i == 20):
            j = 3
        for k in range(10):
            print >> sys.stderr, "launch pair %d time %d" % (i,j)
            print "launch pair %d time %d" % (i,j)
            p = multiprocessing.Process(target=iperfTest,args=(network,i))
            p.daemon=True
            startTime=time.time()
            p.start()
            lim = 0
            while( p.is_alive() and lim < time_limit ) :
                sleep(1)
                lim=lim+1
            if(p.is_alive()):
                p.terminate()
                print >> sys.stderr, "Time out... @pair %d time %d" % (i,j)
                print "Time out... @pair %d time %d" % (i,j) 
                network.stop()
                network = JellyfishNet(seed=seed_, switches=switches_, nodes=nodes_, ports_per_switch=ports_per_switch_, hosts_per_switch=hosts_per_switch_, switch=OVSSwitch, link=TCLink, controller=RemoteController, autoSetMacs=True)
                network.start()
                setRoutes(network)
                random.seed((29*i+13*j+7*k) % 37)
                time_limit = int(time_limit*0.9+60)
            else:
                j=j+1
                endTime=time.time()
                time_limit = int(1+(endTime-startTime)*1.5+time_limit/2)
            if(j>=5):
                break

    #CLI(network)
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    network.stop()
