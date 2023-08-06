# Simple Directed Graph Class for Waypoint Graphs
# Tung M. Phan
# California Institute of Technology
# May 9th, 2018
import numpy as np

class DirectedGraph():
    def __init__(self):
        self._nodes = set() # set of nodes
        self._edges = {} # set of edges is a dictionary of sets (of nodes)
        self._sources = set()
        self._sinks = set()

    def add_node(self, node): # add a node
            self._nodes.add(node)

    def add_edges(self, edge_set): # add edges
        for edge in edge_set:
            if len(edge) != 2:
                raise SyntaxError('Each edge must be a 2-tuple of the form (start, end)!')
            for node in edge:
                if node not in self._nodes:
                    self.add_node(node)
            try: self._edges[edge[0]].add(edge[1])
            except KeyError:
                self._edges[edge[0]] = {edge[1]}

    def add_double_edges(self, edge_set): # add two edges (of the same weight) for two nodes
        for edge in edge_set:
            self.add_edges([edge])
            edge_other = list(edge) # turns into a list, since tuple is immutable
            temp = edge_other[0]
            edge_other[0] = edge_other[1]
            edge_other[1] = temp
            self.add_edges([edge_other])

    def print_graph(self):
        print('The directed graph has ' + str(len(self._nodes)) + ' nodes: ')
        print(str(list(self._nodes)).strip('[]'))
        print('and ' + str(sum([len(self._edges[key]) for key in self._edges])) + ' edges: ')
        for start_node in self._edges:
            print(str(start_node) + ' -> ' +  str(list(self._edges[start_node])).strip('[]'))

    def plot_edges(self, plt, plt_src_snk = True, edge_width = 0.5, head_width = 0.5, alpha = 0.5,
            markersize = 10):
        for start_node in self._edges:
            start_x = start_node[0]
            start_y = start_node[1]
            for end_node in self._edges[start_node]:
                end_x = end_node[0]
                end_y = end_node[1]
                dx = end_x - start_x
                dy = end_y - start_y
                # plot transition
                plt.arrow(start_x,start_y, dx, dy, linestyle='dashed', color = 'r',
                        width=edge_width,head_width=head_width, alpha=0.5)
        if plt_src_snk == True:
            node_x = np.zeros(len(self._sources))
            node_y = np.zeros(len(self._sources))
            k = 0
            for node in self._sources:
                print(node)
                node_x[k] = node[0]
                node_y[k] = node[1]
                k += 1
            plt.plot(node_x, node_y, 'ro', alpha = alpha, markersize=10)
            node_x = np.zeros(len(self._sinks))
            node_y = np.zeros(len(self._sinks))
            k = 0
            for node in self._sinks:
                node_x[k] = node[0]
                node_y[k] = node[1]
                k += 1
            plt.plot(node_x, node_y, 'bo', alpha = alpha, markersize=10)
            plt.legend(['sources', 'sinks'])

class WeightedDirectedGraph(DirectedGraph):
    def __init__(self):
        DirectedGraph.__init__(self)
        self._weights = {} # a dictionary of weights

    def add_edges(self, edge_set): # override parent's method to allow for edge weights
        for edge in edge_set:
            if len(edge) != 3:
                raise SyntaxError('Each edge must be a 3-tuple of the form (start, end, weight)!') 
            for node in edge[0:2]:
                if node not in self._nodes:
                    self.add_node(node)
            try: self._edges[edge[0]].add(edge[1])
            except KeyError:
                self._edges[edge[0]] = {edge[1]}
            self._weights[(edge[0], edge[1])] = edge[2] # add weight

    def print_graph(self):
        print('The directed graph has ' + str(len(self._nodes)) + ' nodes: ')
        print(str(list(self._nodes)).strip('[]'))
        print('and ' + str(sum([len(self._edges[key]) for key in self._edges])) + ' edges: ')
        for start_node in self._edges:
            for end_node in self._edges[start_node]:
                print(str(start_node) + ' -(' + str(self._weights[start_node, end_node]) +  ')-> ' +  str(end_node))
