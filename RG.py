# -*- coding: utf-8 -*-
import numpy as np
import networkx as nx
import copy
import matplotlib.pyplot as plt


class RG(object):
    def __init__(self, directed = True):
        self.node_list = []
        self.edge_dic = {}
        self.neighbor = {}
        self.directed = directed

        self.tag = {}

    def add_node(self, node_id):
        if node_id not in self.node_list:
            self.node_list.append(node_id)
            self.neighbor[node_id] = []
            self.tag[node_id] = 0     #tag
            return len(self.node_list)-1
        else:
            return -1


    def add_edge(self, edge, weight = 1):
        if edge not in self.edge_dic.keys():
            self.edge_dic[edge] = weight
        else:
            self.edge_dic[edge] =self.edge_dic[edge] + weight

        fr = edge[0]
        to = edge[1]
        if to not in self.neighbor[fr]:
            self.neighbor[fr].append(to)

        return self.edge_dic[edge]


    def tran_to_nx(self):
        g = nx.DiGraph()
        edge_list = []
        for key, val in self.edge_dic.items():
            edge = (key[0], key[1], val)
            edge_list.append(edge)

        g.add_nodes_from(self.node_list)
        g.add_weighted_edges_from(edge_list)
        return g


    def dfs_from(self, source, step, path = [], paths = []):
        #print 'dfs_dfs_dfs', source, len(path)     #test
        #print 'neigh of source', self.neighbor[source]      #test
        #print 'paths length', len(paths)      #test
        path.append(source)
        if len(path) == step+1:
            new_path = copy.copy(path)
            paths.append(new_path)
            path.remove(source)
            return paths

        for neigh in self.neighbor[source]:
            if neigh not in path:
                self.dfs_from(neigh, step, path, paths)
        path.remove(source)

        return paths


    def max_path_dfs_from(self, source, step, path = [], max_path = {}):
        path.append(source)
        if len(path) == step+1:
            sum_EOF = self.cal_sum_EOF(path)
            if len(max_path) == 0:
                new_path = copy.copy(path)
                max_path[tuple(new_path)] = sum_EOF
            else:
                max_sum_EOF = max_path.values()
                if sum_EOF > max_sum_EOF[0]:
                    new_path = copy.copy(path)
                    max_path.popitem()
                    max_path[tuple(new_path)] = sum_EOF
            path.remove(source)
            return max_path

        for neigh in self.neighbor[source]:
            if neigh not in path:
                self.max_path_dfs_from(neigh, step, path, max_path)
        path.remove(source)

        return max_path



    def max_path_dfs_from_2(self, source, step, path = [], max_path = {}):
        path.append(source)
        self.tag[source] = 1
        if len(path) == step+1:
            sum_EOF = self.cal_sum_EOF(path)
            if len(max_path) == 0:
                new_path = copy.copy(path)
                max_path[tuple(new_path)] = sum_EOF
            else:
                max_sum_EOF = max_path.values()
                if sum_EOF > max_sum_EOF[0]:
                    new_path = copy.copy(path)
                    max_path.popitem()
                    max_path[tuple(new_path)] = sum_EOF
            path.remove(source)
            self.tag[source] = 0
            return max_path

        for neigh in self.neighbor[source]:
            if self.tag[neigh] == 0:
                self.max_path_dfs_from(neigh, step, path, max_path)
        path.remove(source)
        self.tag[source] = 0

        return max_path



    def cal_sum_EOF(self, path):
        current_EOF = 0.0
        for i in range(len(path) - 1):
            edge = (path[i], path[i + 1])
            current_EOF += self.edge_dic[edge]

        return current_EOF


    def draw_graph(self):
        G = self.tran_to_nx()
        pos = nx.shell_layout(G)
        #weight_list = self.edge_dic.values()
        weight_list = []
        for edge in G.edges():
            weight_list.append(self.edge_dic[edge])
        nx.draw_networkx(G, pos, node_color = 'cyan', edge_color = 'navy' , label = self.node_list, node_size =800, width = [item for item in weight_list], linewidths = 0.1)
        plt.show()


    def save_graph(self, path):
        new_file = open(path, 'w')
        for item in self.edge_dic.keys():
            new_file.write(str(item[0]) + ' ' + str(item[1]) + ' ' + str(self.edge_dic[item]) +'\n')

        new_file.close()





