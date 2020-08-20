# -*- coding: utf-8 -*-
import numpy as np
from Power_Failure import Power_Failure
from Graph import Power_Graph
import random
import math
import networkx as nx
import matplotlib.pyplot as plt
from pypower.case14 import case14
from pypower.case57 import case57
from pypower.case30 import case30
from pypower.case39 import case39
from pypower.case118 import case118
# from pypower.case118_c import case118_c
from pypower.case300 import case300
from pypower.case500 import case500
from pypower.case2383 import case2383
from pypower.case24_ieee_rts import case24_ieee_rts
from pypower.rundcpf import rundcpf
from time import clock
import heapq
import matplotlib.ticker as ticker
import os
import time
from RG import RG
from sklearn.cluster import AgglomerativeClustering


###随机攻击画图


'''
继承Power_Failure类
'''


class Attack(Power_Failure):
    '''
    graph_list: 电网经过级联失效后的一个或多个子网络
    ini_graph: 未经过失效的原始电网
    '''

    def __init__(self, graph_list, ini_graph, isolate_list=None):
        super(Attack, self).__init__(ini_graph)
        self.ini_bus_dic = {}  # 原始电网bus数据
        self.ini_bus_id = []  # 原始电网bus id
        self.ini_m_bus = 0  # 原始电网bus数目
        self.ini_gen_dic = {}  # 原始电网generator数据
        self.ini_gen_id = []  # 原始电网generator id
        self.ini_neigh_id = {}  # 原始电网的节点邻居id
        self.ini_branch_dic = {}  # 原始电网branch数据
        self.ini_branch_id = []
        self.ini_load = {}  # 原始电网节点负荷
        self.ini_degree = {}  # 原始电网节点度
        self.failure_list = []  # 失效的子网络
        self.residual_percent = 0.0
        self.steady_list = graph_list  # 在稳定状态的子网络
        if isolate_list != None:
            self.isolate_list = isolate_list
        self.init_by_ini_graph(ini_graph)

    '''
    根据原始电网数据初始化Grid_Recovery对象的参数
    '''

    def init_by_ini_graph(self, g):
        for item in g.bus:
            self.ini_bus_dic[int(item[0])] = item
        self.ini_bus_id = g.bus_id
        self.ini_m_bus = g.m_Bus

        for item in g.gens:
            self.ini_gen_dic[int(item[0])] = item
        self.ini_gen_id = g.gen_id

        for item in g.branch:
            tp = (int(item[0]), int(item[1]))
            self.ini_branch_dic[tp] = item
            self.ini_branch_id.append(tp)

        for item in self.ini_branch_dic.keys():
            fr = item[0]
            to = item[1]
            if fr in self.ini_neigh_id.keys():
                self.ini_neigh_id[fr].append(to)
            else:
                self.ini_neigh_id[fr] = [to]
            if to in self.ini_neigh_id.keys():
                self.ini_neigh_id[to].append(fr)
            else:
                self.ini_neigh_id[to] = [fr]

        for item in self.ini_bus_id:
            flag = 0
            for graph in self.steady_list:
                if item in graph.bus_id:
                    flag = 1
                    break
            if flag == 0:
                self.failed_bus_id.append(item)

        for item in self.ini_branch_dic.keys():
            flag = 0
            for graph in self.steady_list:
                if item in graph.edge_list:
                    flag = 1
                    break
            if flag == 0:
                self.failed_branch.append(item)

        self.ini_load = g.load_bus
        self.ini_degree = g.degree

    def set_isolate_list(self, graph_list):
        self.isolate_list = graph_list

    def cal_residual_power(self):
        current_power = 0.0
        for graph in self.steady_list:
            for item in graph.load_bus.values():
                current_power += item

        self.residual_percent = current_power / self.total_power
        return self.residual_percent






def attack_nodes(size, attack_list):

    if size == 57:
        G = case57()
    elif size == 118:
        G = case118()
    elif size == 300:
        G = case300()
    elif size == 500:
        G = case500()
    elif size == 2383:
        G = case2383()

    g = Power_Graph()
    new_case = g.case_preprocess(G)
    g.init_by_case(G)
    g.set_ramp_rate(0.3)

    for k in attack_list:
        g.delete_bus(k)

    # g.delete_branch(24, 70)
    # g.delete_branch(2, 4)
    cf = Power_Failure(g)
    cf.failure_process()
    # for graph in cf.steady_list:
    # print 'steady graph', graph.bus_id

    # print 'draw steady graph before recovery'
    #    for g in cf.steady_list:
    #        g.draw_P_graph()
    # Power_Graph.draw_graph_list(cf.steady_list)

    # for graph in cf.isolate_list:
    # print 'isolate graph', graph.bus_id

    ini_g = Power_Graph()
    ini_g.init_by_case(G)
    # gr = Grid_Recovery(cf.steady_list, ini_g)
    # gr.recover_with_bus(4)
    gr = Attack(cf.steady_list, ini_g, cf.isolate_list)

    load_np = np.zeros((size,))
    for graph in cf.steady_list:
        # print(graph.load_bus)

        for item in graph.load_bus.items():
            # print(item[0])
            # print(item[1])
            load_np[item[0]-1] = item[1]
    load_np[attack_list[0]-1] = gr.ini_load[attack_list[0]]


    max_subgraph_node = 0
    for sub_graph in gr.steady_list:
        if max_subgraph_node < len(sub_graph.bus_id):
            max_subgraph_node = len(sub_graph.bus_id)

    max_subgraph_node_per = max_subgraph_node / size
    # g.draw_graph_list(gr.steady_list)
    # print (len(gr.failed_bus_id))
    # print (str(gr.failed_bus_id))
    # print (len(gr.ini_branch_dic))
    # gr.recover_with_bus(8)
    # gr.recover_with_bus(7)
    # residual_per = gr.recover_with_sequence([167, 206, 202, 122, 15, 225, 243, 199])

    # print('攻击后的rp值',gr.cal_residual_power())
    rp_per = gr.cal_residual_power()
    return rp_per, max_subgraph_node_per, load_np


def cal_distance(load_all_nodes, max_load_node):
    distance_np = np.zeros((len(max_load_node),len(max_load_node)))
    for i in range(len(max_load_node)):
        for j in range(len(max_load_node)):
            if i == j or i > j:
                continue
            distance_np[i,j] = np.sqrt(np.sum(np.square(load_all_nodes[i] - load_all_nodes[j])))
            distance_np[j, i] = distance_np[i, j]

    # print(distance_np)
    return distance_np


def generate_attack_seq(distance_np, max_load_node, label, attack_length):
    attack_seq = []
    attack_seq_tmp_id = []
    #选择第一个节点
    id = -1
    max_dist = -1
    tag_np = np.zeros(len(distance_np))
    print(len(distance_np))
    for i in range(len(distance_np)):
        tmp =distance_np[i].sum()
        if tmp > max_dist:
            max_dist = tmp
            id = i

    for i in range(len(tag_np)):
        if label[i] == label[id]:
            tag_np[i] = -1

    attack_seq.append(max_load_node[id])
    attack_seq_tmp_id.append(id)


    while len(attack_seq) < attack_length:
        max_id = -1
        max_dist = -1
        for i in range(len(distance_np)):
            if tag_np[i] == -1:
                continue

            current_max_dist = 0
            for j in attack_seq_tmp_id:
                current_max_dist += distance_np[i,j]
            if current_max_dist > max_dist:
                max_dist = current_max_dist
                max_id = i

        attack_seq.append(max_load_node[max_id])
        attack_seq_tmp_id.append(max_id)

        for i in range(len(tag_np)):
            if label[i] == label[max_id]:
                tag_np[i] = -1

    return attack_seq



if __name__ == '__main__':


	#网络规模
    size = 2383
    #选前k个load最大的点作为候选解
    top_k_load = 2383

	#攻击序列长度
    attack_length = 6


    if size == 57:
        G = case57()
    elif size == 118:
        G = case118()
    elif size == 300:
        G = case300()
    elif size == 500:
        G = case500()
    elif size == 2383:
        G = case2383()



    g = Power_Graph()
    new_case = g.case_preprocess(G)
    g.init_by_case(G)
    g.set_ramp_rate(0.3)


    cf = Power_Failure(g)
    cf.failure_process()

    ini_g = Power_Graph()
    ini_g.init_by_case(G)

    gr = Attack(cf.steady_list, ini_g, cf.isolate_list)

    # print(gr.ini_load)
    loads = np.zeros((size,))
    for item in gr.ini_load.items():
        loads[item[0]-1] = item[1]


    # print(loads)

    max_load_node = loads.argsort()[-top_k_load:][::-1]
    #恢复原始的id

    max_load_node = max_load_node +1


    load_all_nodes = np.zeros((len(max_load_node),size))
    for i in range(len(max_load_node)):
        print('i: ',i)
        attack_list = []
        attack_list.append(max_load_node[i])
        rp, msn, load_np = attack_nodes(size, attack_list)
        # print(rp)
        # print(msn)
        # print(attack_list)
        load_all_nodes[i] = load_np[:]
        # print('finish one')
    np.set_printoptions(threshold=1e6)
    # print(load_all_nodes)



    # 聚类

    ward = AgglomerativeClustering(affinity = 'euclidean',n_clusters=attack_length, linkage='ward').fit(load_all_nodes)

    #获得label
    label = ward.labels_
    # print(label)

    distance_np = cal_distance(load_all_nodes, max_load_node)

    attack_seq = generate_attack_seq(distance_np, max_load_node, label, attack_length)

    print(attack_seq)

    rp, msn, loads = attack_nodes(size, attack_seq)
    print(rp)
    print(msn)