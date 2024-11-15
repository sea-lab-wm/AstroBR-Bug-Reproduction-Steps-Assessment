#https://www.youtube.com/watch?v=7XVTnCrWDPY
import queue
import networkx as nx
import matplotlib.pyplot as plt
import time
import math
from PIL import Image, ImageTk
import matplotlib
import tkinter as tk
import matplotlib.gridspec as gridspec
from networkx.drawing.nx_pydot import graphviz_layout

class GraphVisualzation:
	def __init(self):
		self.ax = 0

	def graph_start(self):
		#matplotlib.use('TkAgg')
		fig,axs = plt.subplots(1, 2, figsize=(30,10))
		plt.title("Graph Visualization")
		plt.gca().set_axis_off()
		#plt.gca().set_frame_on(False) 
	

	def image_show(self, screen_id):
		cur_dir = "/data/graphs_json_data/Bug248/1-org.odk.collect.android-v1.20.0/states"
		im_path = cur_dir + "/" + str(screen_id) + ".png"
		img = Image.open(im_path)
		
		return img

	def current_node_visualization(self, node, neighbors, screen_id, matched, s2r_sentence, last_matched_node, G, pos):
		plt.clf()
		plt.title("Graph Visualization")
		plt.gca().set_axis_off()

		gs = gridspec.GridSpec(1, 2, width_ratios=[3,1])

		plt.subplot(gs[0])
		nx.draw(G, pos, with_labels=True, node_color = ['r' if n==node else 'g' for n in G.nodes], node_size=1000, font_size=10, arrows=True)
		plt.legend(["Last Matched Node:  " + str(last_matched_node), "Current Node:  " + str(node), "Neighbors: " + str(neighbors), " S2R-Intr Match:  " + str(matched), "Screen: " + str(screen_id[:10]), "S2R: " + str(s2r_sentence)], loc='upper right', fontsize=10, fancybox=True, shadow=True, framealpha=0.5)

		plt.subplot(gs[1])
		im = self.image_show(screen_id)
		plt.imshow(im)
		
		plt.gca().set_axis_off()
		plt.draw()

		plt.pause(2.5)
		

	def graph_end(self):
		#plt.show()
		time.sleep(1)

	def create_visualization_graph(self, edge_list):

		G = nx.DiGraph()
		G.add_edges_from(edge_list)
		#pos = nx.spring_layout(G)
		#pos = nx.spring_layout(G, k=5/math.sqrt(G.order()))

		G.graph['graph'] = {'ranksep': '5.0', 'nodesep': '1.5', 'splines': 'polyline'}
		
		#"dot" or "neato" or "twopi" or "fdp"
		pos = graphviz_layout(G, prog="dot")  

		return G, pos

	def visualize_search(self, order, title, G, pos):
		plt.figure()
		plt.title(title)

		for i, node in enumerate(order, start=1):
			plt.clf()
			plt.title(title)
			nx.draw(G, pos, with_labels=True, node_color = ['r' if n==node else 'g' for n in G.nodes])
			plt.legend(["Current Node:  " + str(node), i])
			plt.draw()
			plt.pause(2)
		plt.show()
		time.sleep(0.5)

if __name__ == '__main__':
	vis = GraphVisualzation()

	G = nx.Graph()
	G.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), ('B', 'E'), ('C', 'F'), ('C', 'G')])
	pos = nx.spring_layout(G)
	order = ['A', 'B', 'D', 'E', 'C', 'F', 'G']

	vis.visualize_search(order, 'DFS visualization', G, pos)

