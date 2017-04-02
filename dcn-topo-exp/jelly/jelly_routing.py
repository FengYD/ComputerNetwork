from struct import pack
from zlib import crc32
from jellyfish.routing.shortest_path import KPathsRouting
import random
import os
import sys
def setRoutes(net):
    routing = KPathsRouting(net.topo)
    hosts = [net.topo.id_gen(name = h.name) for h in net.hosts]
    for src in hosts:
        print >> sys.stderr, "installing %s" % src.name_str()
        for dst in hosts:
            _install_proactive_path(net, routing, src, dst)
    print "all routes were installed"

def _src_dst_hash(src_dpid, dst_dpid):
  return crc32(pack('QQ', src_dpid, dst_dpid))

def _install_proactive_path(net, routing, src, dst):
  
  src_sw = net.topo.up_nodes(src.name_str())
  assert len(src_sw) == 1
  src_sw_name = src_sw[0]
  dst_sw = net.topo.up_nodes(dst.name_str())
  assert len(dst_sw) == 1
  dst_sw_name = dst_sw[0]
  hash_ = _src_dst_hash(src.dpid, dst.dpid)
  route = routing.get_route(src_sw_name, dst_sw_name, hash_)
  #print >> sys.stderr, "route: %s" % route

  final_out_port, ignore = net.topo.port(route[-1], dst.name_str())
  for i, node in enumerate(route):
    next_node = None
    if i < len(route) - 1:
      next_node = route[i + 1]
      port_pairs = net.topo.port(node, next_node)
      if type(port_pairs) == list:
        out_port = [t[0] for t in port_pairs]
        out_port = out_port[hash_ % len(out_port)]
      else:
        out_port = port_pairs[0]
    else:
      out_port = final_out_port
    ##add routes statically
    os.system("ovs-ofctl add-flow %s dl_type=0x0800,nw_dst=%s,nw_src=%s,idle_timeout=0,hard_timeout=0,priority=10,action=output:%d" % (node, dst.ip_str(), src.ip_str(), out_port))
    os.system("ovs-ofctl add-flow %s dl_type=0x0806,nw_dst=%s,nw_src=%s,idle_timeout=0,hard_timeout=0,priority=10,action=output:%d" % (node, dst.ip_str(), src.ip_str(), out_port))
