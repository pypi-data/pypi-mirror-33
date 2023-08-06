import sys
import json

import graph
import grew
import granalysis

grew.init()

g = dict()
graph.add_node(g, 'W1', {'phon' : 'the', 'cat' : 'DET'} )
graph.add_node(g, 'W2', {'phon' : 'child', 'cat' : 'N'} )
graph.add_node(g, 'W3', {'phon' : 'plays', 'cat' : 'V'} )
graph.add_node(g, 'W4', {'phon' : 'the', 'cat' : 'DET'})
graph.add_node(g, 'W5', {'phon' : 'fool', 'cat' : 'N'})
graph.add_edge(g, 'W2', 'det', 'W1')
graph.add_edge(g, 'W3', 'suj', 'W2')
graph.add_edge(g, 'W3', 'obj', 'W5')
graph.add_edge(g, 'W5', 'det', 'W4')

print("\n==================== search 'pattern {M -> N}' in 'The child plays the fool ====================\n")
matchs = grew.search ("pattern {M -> N}", g)
print ("number of matches: %d" % (len (matchs)))
print (matchs)

print("\n==================== rewrite 'Elle pense venir' with grs in 'data/test.grs' ====================\n")
ipv = dict()
graph.add_node(ipv, 'A', {'phon' : 'Elle', 'lemma':"il", 'cat' : 'PRO'} )
graph.add_node(ipv, 'B', {'phon' : 'pense', 'lemma':"penser", 'cat' : 'V'} )
graph.add_node(ipv, 'C', {'phon' : 'venir', 'lemma': 'venir', 'cat' : 'V', 'm':'inf'} )
graph.add_edge(ipv, 'B', 'suj', 'A')
graph.add_edge(ipv, 'B', 'obj', 'C')

print("\n--- before ---")
print (ipv)

print("\n--- after ---")
test_grs = grew.grs('data/test.grs')
rew = grew.run (test_grs, ipv)
print (rew)

print("\n==================== to_json ====================\n")
print  (json.dumps (grew.json_grs (test_grs), indent=2))

graph.draw(g)


