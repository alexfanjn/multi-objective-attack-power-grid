# -*- coding: utf-8 -*-
import numpy as np
from Power_Failure import Power_Failure
from Graph import Power_Graph
import random
import math
import  networkx as nx
import matplotlib.pyplot as plt

from pypower.case118 import case118
from pypower.case300 import case300
from pypower.case2383 import case2383
from pypower.case500 import case500
from pypower.rundcpf import rundcpf
from time import clock
import heapq
import matplotlib.ticker as ticker
import os
import time




'''
继承Power_Failure类
'''
class Attack(Power_Failure):
    '''
    graph_list: 电网经过级联失效后的一个或多个子网络
    ini_graph: 未经过失效的原始电网
    '''
    def __init__(self, graph_list, ini_graph, isolate_list = None):
        super(Attack, self).__init__(ini_graph)
        self.ini_bus_dic = {}    #原始电网bus数据
        self.ini_bus_id = []     #原始电网bus id
        self.ini_m_bus = 0       #原始电网bus数目
        self.ini_gen_dic = {}      #原始电网generator数据
        self.ini_gen_id = []       #原始电网generator id
        self.ini_neigh_id = {}     #原始电网的节点邻居id
        self.ini_branch_dic = {}      #原始电网branch数据
        self.ini_branch_id = []
        self.ini_load = {}             #原始电网节点负荷
        self.ini_degree = {}           #原始电网节点度
        self.failure_list = []         #失效的子网络
        self.residual_percent = 0.0
        self.steady_list = graph_list      #稳定状态的子网络
        if isolate_list != None:
            self.isolate_list = isolate_list
        self.init_by_ini_graph(ini_graph)


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

        self.residual_percent = current_power/self.total_power
        return self.residual_percent


def attack_node_list(node_list, size, length):
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



    final_list = node_list

    for k in final_list:
        print(k)
        g.delete_bus(k)


    cf = Power_Failure(g)
    cf.failure_process()

    ini_g = Power_Graph()
    ini_g.init_by_case(G)

    gr = Attack(cf.steady_list, ini_g, cf.isolate_list)

    max_subgraph_node = 0
    for sub_graph in gr.steady_list:
        if max_subgraph_node < len(sub_graph.bus_id):
            max_subgraph_node = len(sub_graph.bus_id)
        # print(len(sub_graph.bus_id))
    max_subgraph_node_decrease_per = max_subgraph_node / size

    rp_decrease_per = gr.cal_residual_power()
    return rp_decrease_per, max_subgraph_node_decrease_per, final_list



if __name__ == '__main__':
    rp_decrease_per, max_subgraph_node_decrease_per, final_list = attack_node_list([18, 16, 17, 11, 4, 15],2383, 6)
    print(rp_decrease_per)
    print(max_subgraph_node_decrease_per)
    print(final_list)



