# -*- coding: utf-8 -*-
import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pypower.case300 import case300

import os

class Power_Graph(object):

    def __init__(self):
        self.pro_a = 0
        self.ramp_rate = 0
        self.m_Bus = 0
        self.bus = np.array([])
        self.bus_id = []
        self.branch = np.array([])
        self.edge_list = []
        self.gens = np.array([])
        self.gen_id = []
        self.matrix = []
        self.baseMVA = 100
        self.br_limit = {}
        self.max_gens = {}
        self.min_gens = {}
        self.load_bus = {}
        self.inj_gens = {}
        self.critical = {1: 0.493050847458, 2: 0.818645592338, 3: 0.493728813559, 4: 0.482542372881, 5: 0.769357400415, 6: 0.482457627119, 7: 0.771436300031, 8: 0.5538405258012, 9: 1.045800485302, 10: 1.2851833788890001, 11: 0.529237288136, 12: 0.763799823139, 13: 0.494406779661, 14: 0.7681405531109999, 15: 0.300423728814, 16: 0.494576271186, 17: 0.659045773106, 18: 0.300254237288, 19: 0.300169491525, 20: 0.692088150625, 21: 0.644986802295, 22: 0.713902968695, 23: 0.629710197521, 24: 0.37414592840899996, 25: 0.84213044233, 26: 0.9223851993850001, 27: 0.647919816088, 28: 0.7714034700329999, 29: 0.487711864407, 30: 0.677393904946, 31: 0.435508474576, 32: 0.66158242638, 33: 0.492627118644, 34: 0.300677966102, 35: 0.493305084746, 36: 0.301101694915, 37: 0.48868176413915, 38: 0.761474295946, 39: 0.491271186441, 40: 0.158898305085, 41: 0.485084745763, 42: 0.145762711864, 43: 0.571500318167, 44: 0.5196014198750001, 45: 0.547501909656, 46: 0.507747740744, 47: 0.7357854673359999, 48: 0.569537210537, 49: 0.8058923055189999, 50: 0.49737035040300004, 51: 0.511824169022, 52: 0.476640275456, 53: 0.214830508475, 54: 0.175084745763, 55: 0.175084745763, 56: 0.175084745763, 57: 0.49705399151999996, 58: 0.507497906932, 59: 0.8091070344710001, 60: 0.782019858411, 61: 0.7292005963679999, 62: 0.46852196583600003, 63: 0.566926449074, 64: 0.558773736392, 65: 0.335084745763, 66: 0.51994738959, 67: 0.421050695038, 68: 0.6603036763479999, 69: 0.810656064719, 70: 0.40097554357, 71: 0.453612491656, 72: 0.470519003348, 73: 0.54995837465, 74: 0.182542372881, 75: 0.31220682410489997, 76: 0.194322033898, 77: 0.753646569504, 78: 0.272033898305, 79: 0.207711864407, 80: 0.734123935698, 81: 0.536546472074, 82: 0.249915254237, 83: 0.5656291175, 84: 0.501204731876, 85: 0.211718927699, 86: 0.52304823632, 87: 0.602149239409, 88: 0.189576271186, 89: 0.1985671744318, 90: 0.207966101695, 91: 0.521269514139, 92: 0.207966101695, 93: 0.50423579208, 94: 0.207033898305, 95: 0.216610169492, 96: 0.207372881356, 97: 0.512262640706, 98: 0.206949152542, 99: 0.207881355932, 100: 0.662565727257, 101: 0.207966101695, 102: 0.534606331397, 103: 0.577459457067, 104: 0.203728813559, 105: 0.203728813559, 106: 0.221610169492, 107: 0.203728813559, 108: 0.52681953536, 109: 0.528662377685, 110: 0.2199077333782, 111: 0.5049077802090001, 112: 0.212203389831, 113: 0.729970750379, 114: 0.754776577213, 115: 0.488728813559, 116: 0.192796610169, 117: 0.816104772195, 118: 0.204661016949}
        self.degree = {}  
  
    def init_by_case(self, case, rm_repeat = True):
        self.bus = case['bus']
        self.branch = case['branch']
        self.gens = case['gen']
        if rm_repeat:
            #判断是否有重复的busid,genid,branch
            self.remove_repeated()
    
        self.m_Bus = len(self.bus)
        for i in self.bus:
            self.bus_id.append(int(i[0]))
        #for i in range(len(self.branch)):
            #self.branch[i][5] = 355.0

        for i in self.gens:
            if int(i[0]) == 69:
                i[1] = 381
        for i in self.gens:
            self.gen_id.append(int(i[0]))
        self.baseMVA = case['baseMVA']

        #   generate the connect matrix:


        self.make_init()

    def init_by_subgraph(self, sub):

        g = Power_Graph()
        g.pro_a = self.ramp_rate
        g.ramp_rate = self.ramp_rate
        g.m_Bus = self.m_Bus
        g.baseMVA = self.baseMVA

        g.bus_id = list(sub.nodes())
        g.bus = np.array([line for line in self.bus if int(line[0]) in g.bus_id])

        g.gen_id = [i for i in g.bus_id if i in self.gen_id]
        g.gens = np.array([line for line in self.gens if int(line[0]) in g.gen_id])

        g.branch = np.array([line for line in self.branch if int(line[0]) in g.bus_id and int(line[1]) in g.bus_id])

        g.make_init()

        return g

    def make_init(self):

        self.matrix = np.zeros([self.m_Bus + 1, self.m_Bus + 1], dtype='int')
        #print(self.branch)
        # print('branch')

        for line in self.branch:
            fr = int(line[0])
            to = int(line[1])
            # print(fr,to)
            self.edge_list.append((fr, to))
            self.matrix[fr][to] = 1

        for i in range(len(self.branch)):
            tp = (int(self.branch[i][0]), int(self.branch[i][1]))
            self.br_limit[tp] = self.branch[i][5]

        for i in range(len(self.gens)):
            g_id = int(self.gens[i][0])
            self.max_gens[g_id] = (self.gens[i][8])
            self.min_gens[g_id] = (self.gens[i][9])
            self.inj_gens[g_id] = (self.gens[i][1])

        # load_list = []
        # print('bus_id')
        for i in range(len(self.bus)):
            b_id = int(self.bus[i][0])
            # print(b_id,b_id)
            self.load_bus[b_id] = (self.bus[i][2])
            # load_list.append(self.bus[i][2])

        g = self.tran_to_nx()
        for i in g.nodes():
            self.degree[i] = g.degree(i)



    def draw_graph_3(self,G):
        nlist=list()
        for d_level in set(sorted([d for n, d in G.degree()])):
            sub_list = [n for n,d in G.degree() if d == d_level]
            nlist.insert(0,sub_list)
        i=1
        #print('before:',nlist)
        plt.figure(figsize=(4,4))
        while(i<len(nlist)-4): #忽略最中心一层与最外三层
            if(len(nlist[i])<=1):
                nlist[i+1].extend(nlist[i])
                nlist.pop(i)
            elif(len(nlist[i]) <= 2**(i)
                and len(nlist[i])+len(nlist[i+1]) > len(nlist[i+2])
                and (len(nlist[i+1])+len(nlist[i+2])) < 2**(i)):
                nlist[i+2].extend(nlist[i+1])
                nlist.pop(i+1)
            else:
                i+=1
        #print('after:',nlist)
        n_color = list()
        # [110, 129, 204, 213, 113, 266, 116, 210, 55, 98]
        list_a = [45,65,49,70]
        for i in G.nodes:
            if i in list_a:
                n_color.append("#00FFFF")
            else:
                n_color.append("#FF0000")
        nx.draw_shell(G, nlist=nlist, with_labels=True,node_size=15,font_size=7,
            width=0.2,edge_color='#272727',node_color=n_color)
        plt.show()
        return None

    @staticmethod
    def case_preprocess(case):
        bus_list = []

        #test
        # for item in case['bus']:
        #     print(item)
            
        for item in case['bus']:
            if item[0] not in bus_list:
                bus_list.append(item[0])
                #print(item[0])
            item[0] = bus_list.index(item[0]) + 1

        for item in case['gen']:
            item[0] = bus_list.index(item[0]) + 1

        for item in case['branch']:
            item[0] = bus_list.index(item[0]) + 1
            item[1] = bus_list.index(item[1]) + 1

        return case


    def set_ramp_rate(self, r):
        self.ramp_rate = r

    def set_failure_pro(self, p):
        self.pro_a = p

    def draw_P_graph(self):
        G = nx.Graph()
        for i in self.bus_id:
            G.add_node(i)
            for j in range(len(self.matrix[i])):
                if self.matrix[i][j] == 1:
                    G.add_edge(i, j, l = '14/22')
        pos = nx.circular_layout(G)
        nx.draw_networkx_nodes(G, pos, nodelist=self.bus_id,  node_color='g', node_size=200, label=self.bus_id)
        nx.draw_networkx_nodes(G, pos, nodelist=self.gen_id, node_color='r', node_size=200)
        nx.draw_networkx_edges(G, pos)
        nx.draw_networkx_labels(G, pos)

        #nx.draw_networkx_edge_labels(G, pos)
        plt.show()

    @staticmethod
    def draw_graph_list(graph_list):
        G = nx.Graph()
        node_list = []
        gen_list = []
        for graph in graph_list:
            for i in graph.bus_id:
                G.add_node(i)
                node_list.append(i)
                for j in range(len(graph.matrix[i])):
                    if graph.matrix[i][j] == 1:
                        G.add_edge(i, j, l = '14/22')
            for i in graph.gen_id:
                gen_list.append(i)
        pos = nx.circular_layout(G)
        nx.draw_networkx_nodes(G, pos, nodelist=node_list, node_color='g', node_size=200, label=node_list)
        nx.draw_networkx_nodes(G, pos, nodelist=gen_list, node_color='r', node_size=200)
        nx.draw_networkx_edges(G, pos)
        nx.draw_networkx_labels(G, pos)

        # nx.draw_networkx_edge_labels(G, pos)
        plt.show()


    def tran_to_nx(self):
        g = nx.Graph()
        g.add_nodes_from(self.bus_id)
        g.add_edges_from(self.edge_list)
        return g

    def get_case(self):
        case = {}
        case['baseMVA'] = self.baseMVA
        case['bus'] = self.bus
        case['gen'] = self.gens
        case['branch'] = self.branch
        case['version'] = 2
        #case['gencost'] = np.array([])
        return case

    def delete_branch(self, fr, to):
        #print 'delete_br', str((fr, to))
        #print self.br_limit
        self.br_limit.pop((fr, to))
        if (fr, to) in self.edge_list:
            self.edge_list.remove((fr, to))
        else:
            self.edge_list.remove((to, fr))
        self.matrix[fr][to] = 0
        for i in range(len(self.branch)):
            line = self.branch[i]
            if fr == int(line[0]) and to == int(line[1]):
                self.branch = np.delete(self.branch, i, axis=0)
                break
        if fr in self.degree.keys():
            self.degree[fr] = self.degree[fr] - 1
        if to in self.degree.keys():
            self.degree[to] = self.degree[to] - 1

    def add_branch(self, branch):
        fr = int(branch[0])
        to = int(branch[1])
        self.br_limit[(fr, to)] = branch[5]
        self.edge_list.append((fr, to))
        self.matrix[fr][to] = 1
        self.branch = np.append(self.branch, [branch], axis=0)
        if fr in self.degree.keys():
            self.degree[fr] = self.degree[fr] + 1
        if to in self.degree.keys():
            self.degree[to] = self.degree[to] + 1



    def delete_bus(self, num):
        #print 'delete bus' + str(num)
        # judge for gens
        if num in self.gen_id:
            self.gen_id.remove(num)
            self.inj_gens.pop(num)
            for i in range(len(self.gens)):
                if num == int(self.gens[i][0]):
                    self.gens = np.delete(self.gens, i, axis=0)
                    break

        # delete bus
        self.bus_id.remove(num)
        self.load_bus.pop(num)
        self.degree.pop(num)
        for i in range(len(self.bus)):
            if num == int(self.bus[i][0]):
                self.bus = np.delete(self.bus, i, 0)
                break

        # delete relative branch
        for line in self.branch:
            fr = int(line[0])
            to = int(line[1])
            if num == fr or num == to:
                self.delete_branch(fr, to)


    def add_bus(self, new_bus):
        new_bus_id = int(new_bus['bus'][0])
        self.bus = np.append(self.bus, [new_bus['bus']], axis=0)
        self.bus_id.append(new_bus_id)
        self.load_bus[new_bus_id] = new_bus['bus'][2]
        self.degree[new_bus_id] = 0

        if 'gen' in new_bus.keys():
            new_gen_id = int(new_bus['gen'][0])
            self.gens = np.append(self.gens, [new_bus['gen']], axis=0)
            self.gen_id.append(new_gen_id)
            self.inj_gens[new_gen_id] = new_bus['gen'][1]
            self.max_gens[new_gen_id] = new_bus['gen'][8]
            self.min_gens[new_gen_id] = new_bus['gen'][9]

        for item in new_bus['branch']:
            self.add_branch(item)



    def find_con_graph_list(self):
        subgraph_list = []
        P_graph_list = []
        G = nx.Graph()
        G.add_nodes_from(self.bus_id)
        G.add_edges_from(self.edge_list)
        for g in nx.connected_component_subgraphs(G):
            if g.number_of_nodes() == 1 or len([node for node in g.nodes() if node in self.gen_id]) == 0:
                continue
            else:
                subgraph_list.append(g)
        for g in subgraph_list:
            P_graph_list.append(self.init_by_subgraph(g))
        return P_graph_list


    def find_con_graph_list_2(self):
        subgraph_list = []
        P_graph_list = []
        G = nx.Graph()
        G.add_nodes_from(self.bus_id)
        G.add_edges_from(self.edge_list)
        for g in nx.connected_component_subgraphs(G):
            subgraph_list.append(g)
        for g in subgraph_list:
            P_graph_list.append(self.init_by_subgraph(g))
        return P_graph_list


    def is_effect(self):
        g = self.tran_to_nx()
        if g.number_of_nodes() == 1 or len([node for node in g.nodes() if node in self.gen_id]) == 0:
            return False
        return True

    def is_connect(self):
        g = self.tran_to_nx()
        return nx.is_connected(g)

    def cal_load_sum(self):
        load_sum = 0
        for i in self.load_bus.values():
            load_sum += i
        return load_sum

    def cal_gen_sum(self):
        inj_sum = 0
        for i in self.inj_gens.values():
            inj_sum += i
        return inj_sum

    def update(self):
        for i in range(len(self.bus)):
            line = self.bus[i]
            id_ = int(line[0])
            #print (self.bus[i][2]), (self.load_bus[id_])
            self.bus[i][2] = self.load_bus[id_]
        for i in range(len(self.gens)):
            line = self.gens[i]
            id_ = int(line[0])
            self.gens[i][1] = self.inj_gens[id_]

    def remove_repeated(self):
        new_bus = []
        new_gen = []
        new_branch = []

        i = 0
        while i < len(self.bus):
            bus_id = self.bus[i][0]
            if bus_id in new_bus:
                self.bus = np.delete(self.bus, i, axis=0)
            else:
                new_bus.append(bus_id)
                i+=1
        i = 0
        while i < len(self.gens):
            gen_id = self.gens[i][0]
            if gen_id in new_gen:
                self.gens = np.delete(self.gens, i, axis=0)
            else:
                new_gen.append(gen_id)
                i+=1
        i = 0
        while i < len(self.branch):
            fr = self.branch[i][0]
            to = self.branch[i][1]
            if (fr, to) in new_branch:
                self.branch = np.delete(self.branch, i, axis=0)
            else:
                new_branch.append((fr, to))
                i+=1


if __name__ == '__main__':
    G = case300()
    g = Power_Graph()
    new_case = g.case_preprocess(G)
