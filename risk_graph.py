# -*- coding: utf-8 -*-
import numpy as np
from Power_Failure import Power_Failure
from Graph import Power_Graph
import random
import math
import networkx as nx
import matplotlib.pyplot as plt

from pypower.case118 import case118
from pypower.case300 import case300
from pypower.case500 import case500
from pypower.case2383 import case2383
from pypower.rundcpf import rundcpf
from time import clock
import heapq
import matplotlib.ticker as ticker
import os
import time
from RG import RG



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
        self.failure_list = []  # 在recovery过程中候选失效的子网络
        self.residual_percent = 0.0
        self.steady_list = graph_list  # 在recovery中稳定状态的子网络
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

	if size == 118:
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
    return rp_per, max_subgraph_node_per




def cal_candidate_set(mode, size, P):

    g = Power_Graph()
    new_case = g.case_preprocess(G)
    g.init_by_case(G)
    g.set_ramp_rate(0.3)


    cf = Power_Failure(g)
    cf.failure_process()

    ini_g = Power_Graph()
    ini_g.init_by_case(G)
    gr = Attack(cf.steady_list, ini_g, cf.isolate_list)

    bus_attack_dic = {}

    bus_attack_id = gr.ini_bus_id
    # print(bus_attack_id)
    for bus in bus_attack_id:
        attack_list = []
        attack_list.append(bus)
        rp_per, max_subgraph_node_per = attack_nodes(size, attack_list)
        if mode == 1:
            bus_attack_dic[bus] = rp_per
        elif mode == 2:
            bus_attack_dic[bus] = max_subgraph_node_per
        elif mode == 3:
            bus_attack_dic[bus] = rp_per + max_subgraph_node_per

    sorted_list = sorted(bus_attack_dic.items(), key=lambda item: item[1], reverse=False)

    # print(bus_attack_dic)

    candidate_set = {}
    for item in sorted_list:
        candidate_set[item[0]] = item[1]
        if len(candidate_set) == P:
            break

    # print(candidate_set)
    return candidate_set
    # print(bus_attack_id)

def cal_RSS_set(candidate_set, R, Round, mode):
    RSS_set = {}
    bus_list_dic = {}
    sorted_list = sorted(candidate_set.items(), key=lambda item: item[1], reverse=False)

    for item in sorted_list:
        tmp_list = (item[0],)
        bus_list_dic[tmp_list] = item[1]
        if len(bus_list_dic) == R:
            break

    RSS_set['RSS_1'] = bus_list_dic


    current_round = 1


    while current_round < Round:
        print('cal rss, current round: ', current_round)
        current_dic = {}
        key = 'RSS_' + str(current_round)
        bus_list_dic = RSS_set[key]
        for bus_list in bus_list_dic.items():
            for candidate in candidate_set.items():

                if candidate[0] in bus_list[0]:
                    continue
                seq = []
                seq.extend(list(bus_list[0]))
                seq.append(candidate[0])

                seq.sort(reverse=False)


                rp_per, max_subgraph_node_per = attack_nodes(size, seq)
                seq = tuple(seq)
                if mode == 1:
                    current_dic[seq] = rp_per
                elif mode == 2:
                    current_dic[seq] = max_subgraph_node_per
                elif mode == 3:
                    current_dic[seq] = rp_per + max_subgraph_node_per

        sorted_list = sorted(current_dic.items(), key=lambda item: item[1], reverse=False)

        select_list_dic = {}
        for item in sorted_list:
            select_list_dic[item[0]] = item[1]
            if len(select_list_dic) == R:
                break
        current_round += 1
        key = 'RSS_' + str(current_round)
        RSS_set[key] = select_list_dic

    print(RSS_set)
    return RSS_set


def construct_risk_graph(RSS_set):
    rg = RG()
    for item in RSS_set.items():
        if item[0] == 'RSS_1':
            continue
        bus_list_dic = item[1]
        r = int(item[0][4:])
        # print(r)
        weight = 2.0 / (r*(r-1))
        for seq in bus_list_dic.keys():
            for i in range(len(seq)):
                for j in range(i + 1, len(seq)):
                    edge = (seq[i], seq[j])
                    rg.add_node(seq[i])
                    rg.add_node(seq[j])
                    rg.add_edge(edge,weight)

    return rg


def cal_rg_attack_seq(rg, Round):
    max_EOF = 0.0
    attack_seq = []
    for source in rg.node_list:
        Paths = rg.dfs_from(source, Round-1, [], [])
        for path in Paths:
            current_EOF = 0.0
            for i in range(len(path) - 1):
                edge = (path[i], path[i+1])
                current_EOF += rg.edge_dic[edge]

            if current_EOF > max_EOF:
                max_EOF = current_EOF
                attack_seq = path
    return attack_seq

if __name__ == '__main__':



    size = 2383

    #以哪种形式攻击-> mode=1,2,3  ->> fv,sv,fv+sv
    mode = 2

    P = 100  # 推荐的候选节点个数
    R = 50 # 推荐的攻击序列组合个数
    Round = 6 # 攻击序列的长度


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

    print('mode: ', mode)

    print('begin cal candidate_set')
    candidate_set = cal_candidate_set(mode, size, P)

    print('begin cal rss_net')

    RSS_set = cal_RSS_set(candidate_set, R, Round, mode)

    sorted_list = sorted(RSS_set['RSS_3'].items(), key=lambda item: item[1], reverse=False)
    # print(sorted_list[0][0])
    # print(sorted_list[0][1])
    # for item in sorted_list:
    #     print(item[0])

    print('begin cal rss attack')
    attack_list_1 = sorted_list[0][0]
    rp1, msn1 = attack_nodes(size, attack_list_1)
    print('rss')
    print(rp1)
    print(msn1)
    print(attack_list_1)


    print('begin caonstruct rg')

    rg = construct_risk_graph(RSS_set)


    print('begin cal rg attack')

    #Risk Graph
    attack_list = cal_rg_attack_seq(rg, Round)

    rp, msn = attack_nodes(size, attack_list)
    print('rg')
    print(rp)
    print(msn)
    print(attack_list)