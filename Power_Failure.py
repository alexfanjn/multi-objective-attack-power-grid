# -*- coding: utf-8 -*-
import sys
import random
import math
import networkx as nx
import matplotlib.pyplot as plt
from Graph import Power_Graph
from pypower.case118 import case118
from pypower.case300 import case300

from pypower.rundcpf import rundcpf
from time import clock
import  numpy as np
#import Queue
import queue
import os
class  Power_Failure(object):
    def __init__(self, G):
        self.re_list = [0.0]
        self.current = 0.0
        self.failure_list =[]
        self.failure_list.append(G)
        self.steady_list = []
        self.isolate_list = []
        self.load_sum = 0.0
        self.inj_sum = 0.0
        self.cf_branch = {}
        self.failure_dict = {0: 0.0}
        self.largest_dict = {0: 0.0}
        self.z1 = random.random()
        self.total_power = 0.0
        self.cal_first_power(G)
        self.init_node = G.bus_id
        self.critical = {1: 0.449152542373, 2: 0.5076772250795, 3: 0.449152542373, 4: 0.440677966102, 5: 0.440677966102, 6: 0.440677966102, 7: 0.6545069975960001, 8: 0.449152542373, 9: 0.971587594595, 10: 1.83562185353, 11: 0.474576271186, 12: 0.636970970284, 13: 0.449152542373, 14: 0.440677966102, 15: 0.254237288136, 16: 0.449152542373, 17: 0.568814120155, 18: 0.254237288136, 19: 0.254237288136, 20: 0.60852834489, 21: 0.604625338743, 22: 0.5957194578839999, 23: 0.560816094678, 24: 0.35080717816999996, 25: 0.6061779301419999, 26: 0.774314961762, 27: 1.249180174652, 28: 0.440677966102, 29: 0.449152542373, 30: 0.44727862616801, 31: 0.398305084746, 32: 0.588013630636, 33: 0.449152542373, 34: 0.254237288136, 35: 0.449152542373, 36: 0.254237288136, 37: 0.440677966102, 38: 1.273551810387, 39: 0.449152542373, 40: 0.127118644068, 41: 0.440677966102, 42: 0.118644067797, 43: 0.520467968398, 44: 1.010965944999, 45: 0.448913821915, 46: 0.409912881195, 47: 1.038389347168, 48: 0.501160259365, 49: 1.035297477003, 50: 0.40935312405900004, 51: 1.027150737138, 52: 0.40471719311800003, 53: 0.203389830508, 54: 0.194915254237, 55: 0.194915254237, 56: 0.194915254237, 57: 0.40909965140000004, 58: 0.534158753055, 59: 1.012417979353, 60: 0.2920212520782, 61: 1.045197740113, 62: 0.2502298037546, 63: 0.2960753173286, 64: 0.3104706441114, 65: 0.347457627119, 66: 0.342678958129, 67: 0.991585755311, 68: 0.898381000328, 69: 0.4215971242, 70: 0.400521137736, 71: 0.431088629444, 72: 0.424430019633, 73: 0.951689313551, 74: 0.186440677966, 75: 0.429266075433, 76: 0.21186440678, 77: 1.085714633187, 78: 0.237288135593, 79: 0.203389830508, 80: 1.047541713381, 81: 0.408493754944, 82: 0.228813559322, 83: 0.203389830508, 84: 0.417523605029, 85: 0.215617232784, 86: 0.430296058047, 87: 0.43768928950999997, 88: 0.194915254237, 89: 0.186440677966, 90: 0.21186440678, 91: 0.425947582583, 92: 0.21186440678, 93: 0.203389830508, 94: 0.203389830508, 95: 0.21186440678, 96: 0.203389830508, 97: 0.7172297521369999, 98: 0.203389830508, 99: 0.21186440678, 100: 0.23189320178439998, 101: 0.21186440678, 102: 0.494809051982, 103: 0.422340822992, 104: 0.21186440678, 105: 0.21186440678, 106: 0.228813559322, 107: 0.21186440678, 108: 1.053137991686, 109: 1.0529130605350001, 110: 0.22804332659919999, 111: 0.43768928950999997, 112: 0.220338983051, 113: 0.606072245963, 114: 0.440677966102, 115: 0.449152542373, 116: 0.203389830508, 117: 0.449152542373, 118: 0.203389830508}
        self.failed_bus_id = []
        self.failed_branch = []

    def find_failure_node(self):
        fail_list = []
        fail_list.extend(self.init_node)
        for g in self.failure_list:
            for i in g.bus_id:
                fail_list.remove(i)
        for g in self.steady_list:
            for i in g.bus_id:
                fail_list.remove(i)
        return fail_list

    def cal_first_power(self, g):
        power_sum = 0.0
        for (u, v) in g.load_bus.items():
            power_sum += v
        self.total_power = power_sum

    def first_failure_process(self):
        queue1 = queue.Queue()
        
        #g是一个子图   failure_list是子图的集合
        for g in self.failure_list:
            queue1.put(g)
        self.failure_list = []
        while queue1.qsize() != 0:
            g = queue1.get()
            #self.CFS(g)
            ##print 'begin of CFS_2'   #key test
            self.CFS_2(g)
            ##print 'end of CFS_2'    #key test
            if g.is_effect() is False:
                for item in g.bus_id:
                    self.failed_bus_id.append(item)
                if len(g.bus_id) > 0:
                    if g.is_connect() is True:
                        self.isolate_list.append(g)
                    else:
                        graph_list = g.find_con_graph_list_2()
                        for graph in graph_list:
                            self.isolate_list.append(graph)

                for item in g.edge_list:
                    self.failed_branch.append(item)
                continue
            if g.is_connect() is True:
                self.failure_list.append(g)
            else:
                g_list = g.find_con_graph_list_2()
                for sub_g in g_list:
                    queue1.put(sub_g)
        for g in self.failure_list:
            # print(g.gen_id)
            self.power_flow(g)
        for g in self.steady_list:
            if g in self.failure_list:
                self.failure_list.remove(g)


    def sec_failure_progress(self, g):
        new_list = []
        queue1 = queue.Queue()
        queue1.put(g)
        while queue1.qsize() != 0:
            g = queue1.get()
            #self.CFS(g)
            self.CFS_2(g)
            if g.is_effect() is False:
                for item in g.bus_id:
                    self.failed_bus_id.append(item)
                if len(g.bus_id) > 0:
                    if g.is_connect() is True:
                        self.isolate_list.append(g)
                    else:
                        graph_list = g.find_con_graph_list_2()
                        for graph in graph_list:
                            self.isolate_list.append(graph)

                for item in g.edge_list:
                    self.failed_branch.append(item)
                continue
            if g.is_connect() is True:
                self.failure_list.append(g)
                new_list.append(g)
            else:
                g_list = g.find_con_graph_list_2()
                for sub_g in g_list:
                    queue1.put(sub_g)

        for g in new_list:
            self.power_flow(g)
        for g in self.steady_list:
            if g in self.failure_list:
                self.failure_list.remove(g)


    def power_flow(self, g):
        #g.draw_P_graph()
        flag = 0
        flow_model = g.get_case()

        br = rundcpf(flow_model)[0]['branch']
        for line in br:
            fr = int(line[0])
            to = int(line[1])
            current = float('%.2f' % line[13])
            if abs(current) > g.br_limit[(fr,to)]:
                flag = 1
                lim = g.br_limit[(fr, to)]
                pro = (abs(current) - lim) * 1/ lim
                self.cf_branch[((fr,to), pro)] = g

        if flag == 0:
            #self.failure_list.remove(g)
            self.steady_list.append(g)


    '''
    def power_flow_static(self):
        for g in self.failure_dict:
            flag = 0
            flow_model = g.get_case()
            br = rundcpf(flow_model)[0]['branch']
            fail_branch = (0, 0)
            max_overload = 0.0
            for line in br:
                fr = int(line[0])
                to = int(line[1])
                current = float('%.2f' % line[13])
                lim = g.br_limit[(fr, to)]
                if abs(current) > lim:
                    flag = 1
                    current_overload = (abs(current) - lim) / lim
                    if current_overload > max_overload:
                        max_overload = current_overload
                        fail_branch = (fr, to)

            if flag == 0:
                self.failure_list.remove(g)
                self.steady_list.append(g)
            else:
                g.delete_branch(fail_branch[0], fail_branch[1])
    '''

    #@staticmethod
    def cut_load(self, g, remain):
        load_list = sorted(g.load_bus.items(), key=lambda item: item[1], reverse=True)
        for tp in load_list:
            if tp[0] in g.gen_id:
                continue
            elif tp[1] > remain:
                ##print 'cut load'  #key test
                g.load_bus[tp[0]] -= remain
                break
            else:
                remain = remain - tp[1]
                ##print 'delete bus', tp[0]   #key test
                self.append_failed_branch(g, tp[0])
                g.delete_bus(tp[0])
                self.failed_bus_id.append(tp[0])


    def cut_load_2(self, g, remain):
        load_list = sorted(g.load_bus.items(), key=lambda  item: item[1], reverse=True)
        for tp in load_list:
            ##print 'remain', remain     #key test
            if tp[0] in g.gen_id:
                if tp[1] >= remain:
                    g.load_bus[tp[0]] -= remain
                    break
                else:
                    remain -= tp[1]
                    g.load_bus[tp[0]] = 0
            else:
                if tp[1] > remain:
                    g.load_bus[tp[0]] -= remain
                    break
                else:
                    remain -= tp[1]
                    ##print 'delete bus', tp[0]   #key test
                    self.append_failed_branch(g, tp[0])
                    g.delete_bus(tp[0])
                    self.failed_bus_id.append(tp[0])



    #@staticmethod
    def cut_gen(self, g, remain):
        gen_list = sorted(g.inj_gens.items(), key=lambda item: item[1])
        for tp in gen_list:
            if tp[1] > remain:
                g.inj_gens[tp[0]] -= remain
                break
            else:
                remain = remain - tp[1] + g.load_bus[tp[0]]
                ##print 'delete bus', tp[0]   #key test
                self.append_failed_branch(g, tp[0])
                g.delete_bus(tp[0])
                self.failed_bus_id.append(tp[0])


    def cut_gen_2(self, g, remain):
        gen_list = sorted(g.inj_gens.items(), key=lambda item: item[1])
        for tp in gen_list:
            remain = remain - tp[1] + g.load_bus[tp[0]]
            ##print 'delete bus', tp[0]   #key test
            self.append_failed_branch(g, tp[0])
            g.delete_bus(tp[0])
            self.failed_bus_id.append(tp[0])
            if remain <= 0:
                break


    def Ramp_up(self, g):
        remain = self.load_sum - self.inj_sum
        ##print 'remain', remain   #key test
        max_sum = 0
        inj_max = {}
        for i in g.gen_id:
            inj_max[i] = min(g.inj_gens[i] * (1 + g.ramp_rate), g.max_gens[i])
            max_sum += inj_max[i]
        ##print 'max_sum', max_sum, 'load_sum', self.load_sum     #key test
        if max_sum < self.load_sum:
            for i in g.gen_id:
                g.inj_gens[i] = inj_max[i]
            #self.cut_load(g, self.load_sum - max_sum)
            ##print 'begin cut load'          #key test
            self.cut_load_2(g, self.load_sum - max_sum)
            ##print 'end cut load'            #key test
        else:
            r = remain / (max_sum - self.inj_sum)
            ##print 'r', r
            ##print (max_sum-self.inj_sum)
            for (u, v) in g.inj_gens.items():
                g.inj_gens[u] = v + r * (inj_max[u] - v)

    def Ramp_down(self, g):
        remain = self.inj_sum - self.load_sum
        min_sum = 0.0
        inj_min = {}
        for i in g.gen_id:
            inj_min[i] = max(g.inj_gens[i] * (1 - g.ramp_rate), g.min_gens[i])
            min_sum += inj_min[i]
        if min_sum > self.load_sum:
            self.cut_gen(g, remain)
        else:
            r = remain / (self.inj_sum - min_sum)
            for (u, v) in g.inj_gens.items():
                g.inj_gens[u] = v - r * (v - inj_min[u])


    def Ramp_down_2(self, g):
        remain =self.inj_sum - self.load_sum
        min_sum = 0.0
        inj_min = {}
        for i in g.gen_id:
            inj_min[i] = max(g.inj_gens[i] * (1 - g.ramp_rate), g.min_gens[i])
            min_sum += inj_min[i]
        if min_sum > self.load_sum:
            for i in g.gen_id:
                g.inj_gens[i] = inj_min[i]
            self.cut_gen_2(g, min_sum - self.load_sum)
        else:
            r = remain / (self.inj_sum - min_sum)
            for (u, v) in g.inj_gens.items():
                g.inj_gens[u] = v - r * (v - inj_min[u])



    def CFS(self, g):

        self.load_sum = g.cal_load_sum()
        self.inj_sum = g.cal_gen_sum()
        ##print self.load_sum, self.inj_sum

        if round(self.load_sum, 1) == round(self.inj_sum, 1):
            return
        elif self.load_sum > self.inj_sum:
            self.Ramp_up(g)
        else:
            self.Ramp_down(g)
        g.update()


    #g是一个子图
    def CFS_2(self, g):

        self.load_sum = g.cal_load_sum()
        self.inj_sum = g.cal_gen_sum()

        #while round(self.load_sum, 2) != round(self.inj_sum, 2):
        while '%.2f' %self.load_sum != '%.2f' %self.inj_sum and abs(self.load_sum - self.inj_sum) > 1e-7:
            ##print 'load sum', self.load_sum, str(self.load_sum)   #key test
            ##print 'inj sum', self.inj_sum, str(self.inj_sum)   #key test
            if self.load_sum > self.inj_sum:
                ##print 'begin ramp up'   #key test
                self.Ramp_up(g)
                ##print 'end ramp up'    #key test
            else:
                ##print 'begin ramp down'      #key test  
                self.Ramp_down_2(g)
                ##print 'end ramp down'     #key test
            g.update()
            self.load_sum = g.cal_load_sum()
            self.inj_sum = g.cal_gen_sum()
            # for i in g.load_bus.items():
            #     print (i)
            if self.load_sum <= 0 and self.inj_sum == 0:
                break


    def pop_dict(self, g):
        ##print self.cf_branch
        del_list = []
        for (u, v) in self.cf_branch.items():
            if v == g:
                del_list.append(u)
        ##print del_list
        for i in del_list:
            self.cf_branch.pop(i)

        ##print self.cf_branch

    def choose_failure_prob(self):
        pro_sum = 0.0
        pro_list = []
        z2 = random.random()
        for (data, g) in self.cf_branch.items():
            pro = data[1]
            pro_sum += pro
        delta_t = (1.0 / pro_sum) * math.log(1/(1-self.z1))
        self.current += delta_t
        self.re_list.append(delta_t)
        self.current = round(self.current, 3)
        for (data, g) in self.cf_branch.items():
            tp = data[0]
            pro = data[1]
            if (pro / pro_sum) < z2:
                z2 = z2 - (pro / pro_sum)
            else:
                self.failure_branch(data, g)
                break
        #self.sec_failure_progress(g)
        return g


    def choose_failure_static(self):

        fail_branch_data = (0, 0)
        max_overload = 0.0
        for (data, g) in self.cf_branch.items():
            if data[1] > max_overload:
                max_overload = data[1]
                fail_branch_data = (data, g)

        self.failure_branch(fail_branch_data[0], fail_branch_data[1])
        return fail_branch_data[1]


    def failure_branch(self, data, g):
        tp = data[0]
        self.pop_dict(g)
        self.failure_list.remove(g)
        #self.update_failed_branch(g, int(tp[0]), int(tp[1]))
        self.failed_branch.append((int(tp[0]), int(tp[1])))
        g.delete_branch(int(tp[0]), int(tp[1]))



    def append_failed_branch(self, g, node):
        for i in range(len(g.branch)):
            item = g.branch[i]
            fr = int(item[0])
            to = int(item[1])
            if node == fr or node == to:
                self.failed_branch.append((fr, to))


    def cal_failure(self):

        res_dict = {}
        maxx = 0.0
        to_sum = 0.0
        for g in self.failure_list:
            power_sum = 0.0
            value_list = g.load_bus.values()
            for value in value_list:
                power_sum += value
            to_sum += power_sum
            if power_sum > maxx:
                maxx = power_sum
        for g in self.steady_list:
            power_sum = 0.0
            value_list = g.load_bus.values()
            for value in value_list:
                power_sum += value
            to_sum += power_sum
            if power_sum > maxx:
                maxx = power_sum
        p1 = 1 - to_sum / self.total_power
        self.failure_dict[self.current] = p1
        p2 = 1 - maxx / self.total_power
        self.largest_dict[self.current] = p2
        if p1 == 1:
            return 1.0, self.current
        elif p1 > 0.9:
            return 0.9, self.current
        elif p1 > 0.8:
            return 0.8, self.current
        elif p1 > 0.7:
            return 0.7, self.current
        elif p1 > 0.6:
            return 0.6, self.current
        elif p1 > 0.5:
            return 0.5, self.current
        elif p1 > 0.4:
            return 0.4, self.current
        elif p1 > 0.3:
            return 0.3, self.current
        elif p1 > 0.2:
            return 0.2, self.current
        elif p1 > 0.1:
            return 0.1, self.current
        else:
            return 0.0, self.current


    def later_failure(self):
        while len(self.cf_branch) != 0:
            #g = self.choose_failure_prob()
            g = self.choose_failure_static()
            ##print 'begin of second failure process'      #key test
            self.sec_failure_progress(g)
            ##print 'end of second failure process'           #key test
            self.cal_failure()
            self.current += 1
            ##print len(self.cf_branch)   #test



    def failure_process(self):
        ##print "begin of first failure process"    #key test
        self.first_failure_process()
        self.cal_failure()
        self.current += 1
        ##print 'end of first failure process'   #key test
        ##print 'begin of later failure'   #key test
        self.later_failure()
        ##print 'end of later failure'    #key test


    def attack_degree(self, num):
        g = self.failure_list.pop()
        degree_list = sorted(g.degree.items(), key=lambda item: item[1], reverse=True)
        self.steady_list.append(g)
        for item in degree_list:
            if num == 0:
                break

            for g in self.steady_list:
                if item[0] in g.bus_id:
                    self.append_failed_branch(g, item[0])
                    #print 'delete bus with order of degree', item[0]
                    g.delete_bus(item[0])
                    self.failed_bus_id.append(item[0])
                    self.failure_list.append(g)
                    self.steady_list.remove(g)
                    self.failure_process()
                    num -= 1
                    break
        return self.cal_failure()


    def attack_load(self, num):
        g = self.failure_list.pop()
        load_list = sorted(g.load_bus.items(), key=lambda item: item[1], reverse=True)
        self.steady_list.append(g)
        for item in load_list:
            if num == 0:
                break
            for g in self.steady_list:
                if item[0] in g.bus_id:
                    self.append_failed_branch(g, item[0])
                    #print 'delete bus with order of load', item[0]
                    g.delete_bus(item[0])
                    self.failed_bus_id.append(item[0])
                    self.failure_list.append(g)
                    self.steady_list.remove(g)
                    self.failure_process()
                    num -= 1
                    break
        return self.cal_failure()


    def attack_random(self, num):
        attack_list = np.arange(1, len(self.init_node)+1)
        random.shuffle(attack_list)
        g = self.failure_list.pop()
        self.steady_list.append(g)
        for item in attack_list:
            if num ==0:
                break
            for g in self.steady_list:
                if item in g.bus_id:
                    self.append_failed_branch(g, item)
                    #print 'delete bus with random order', item
                    g.delete_bus(item)
                    self.failed_bus_id.append(item)
                    self.failure_list.append(g)
                    self.steady_list.remove(g)
                    self.failure_process()
                    num -= 1
                    break

        return self.cal_failure()

    def draw_graph(self):
        x = []
        y = []
        y1 = []
        failure_l = sorted(self.failure_dict.items(), key=lambda item: item[0])
        largest_l = sorted(self.largest_dict.items(), key=lambda item: item[0])
        for i in failure_l:
            x.append(i[0])
            y.append(i[1])
        #x.append(i[0] * 1.2)
        #y.append(i[1])
        for i in largest_l:
            y1.append(i[1])
        #y1.append(i[1])

        plt.xlabel('Time(s)')
        plt.ylabel('Percentage of failure P')
        plt.plot(x, y, marker='o')
        plt.plot(x, y1, marker='*')
        plt.xlim(0, i[0])
        plt.ylim(0, 1)
        plt.show()

    def train_node(self, gra):#critical node identification
        degree_dict = nx.degree(gra.tran_to_nx())
        dict_robust = {}
        for i in range(1, 119):
            dict_robust[i] = 0.0
        dict_cal = {}
        run_time = clock()
        for i in range(1, 119):
            #print 'current_node:  ' + str(i) + '      runtime: ' + str(clock() - run_time)
            cal = 0.0
            for j in range(0, 100):
                G = case118()
                g = Power_Graph()
                g.init_by_case(G)
                g.set_ramp_rate(0.3)
                self.append_failed_branch(g, i)
                g.delete_bus(i)
                self.failed_bus_id.append(i)
                if i != 69:
                    self.append_failed_branch(g, 69)
                    g.delete_bus(69)
                    self.failed_bus_id.append(69)
                cf1 = Power_Failure(g)
                cf1.first_failure_process()
                cf1.later_failure()
                failure_l = sorted(cf1.failure_dict.items(), key=lambda item: item[1], reverse=True)
                final_failure = failure_l[0][1]
                cal += final_failure
                id = 118
                for p in cf1.steady_list:
                    for q in p.bus_id:
                        dict_robust[q] += 1.0
                        id -= 1
            ##print 'id:    ' + str(id)
            cal = cal / 100
            dict_cal[i] = cal
        #self.critical = dict_cal
        #print dict_robust
        #print dict_cal
        #print 'runtime: ' + str(clock() - run_time)
        list_cal = sorted(dict_cal.items(), key=lambda item: item[1], reverse=True)
        list_robust = sorted(dict_robust.items(), key=lambda item: item[1], reverse=True)
        fil = open('node_influence.txt', 'a')
        fil2 = open('node_val.txt', 'a')
        fil3 = open('node_importance.txt', 'a')
        dict_total = {}
        for i in range(1, 119):
            dict_total[i] = dict_cal[i] + 1 - (dict_robust[i] / 11800.0)
            fil3.write('node_number:  ' + str(i) + '     failure_rate: ' + str(dict_total[i]) + '     degree: ' + str(degree_dict[i]) + '\n')
        for i in list_cal:
            fil.write('node_number:  ' + str(i[0]) + '           failure_rate: ' + str(i[1]) + '\n')
        for i in list_robust:
            fil2.write('node_number:  ' + str(i[0]) + '           failure_rate: ' + str(1 - (i[1] / 11800.0)) + '\n')
        fil.close()
        fil2.close()


def save_cascade_graph():
    G0 = case24_ieee_rts()
    G1 = case39()
    G2 = case57()
    G3 = case118()
    G4 = case200()
    G5 = Power_Graph.case_preprocess(case300())
    G_list = [G0, G1, G2, G3, G4, G5]

    for G in G_list:
        for i in range(0, len(G['bus'])):
            ini_fail_bus = i + 1

            g = Power_Graph()
            g.init_by_case(G)
            g.set_ramp_rate(0.3)
            cf = Power_Failure(g)
            #ini_fail_bus = 1



            g.delete_bus(ini_fail_bus)
            cf.failed_bus_id.append(ini_fail_bus)
            cf.failure_process()
            #print 'failed bus id'
            #print cf.failed_bus_id
            #print 'steady bus id'
            #for graph in cf.steady_list:
                #print graph.bus_id
            #print 'isolate bus id'
            #for graph in cf.isolate_list:
                #print graph.bus_id

            path = 'graph_data/case' + str(len(G['bus']))
            if os.path.exists(path) == False:
                os.mkdir(path)
            file_name = path + '/case' + str(len(G['bus'])) + '_cascade_attack_' + str(ini_fail_bus) + '_'+ str(len(cf.failed_bus_id)) + '.txt'
            new_file = open(file_name, 'w')

            new_file.write('ramp rate '+ str(g.ramp_rate) + '\n')
            new_file.write('\n')
            new_file.write('failed bus id\n')
            new_file.write(str(cf.failed_bus_id) + '\n')
            new_file.write('num of failed bus ' + str(len(cf.failed_bus_id)) + '\n')
            new_file.write('\n')

            steady_num = 0
            new_file.write('steady graph\n')
            for graph in cf.steady_list:
                new_file.write(str(graph.bus_id) + '\n')
                steady_num += len(graph.bus_id)
            new_file.write('num of steady bus ' + str(steady_num) + '\n')
            new_file.write('\n')

            isolate_num = 0
            new_file.write('isolate graph\n')
            for graph in cf.isolate_list:
                new_file.write(str(graph.bus_id) + '\n')
                isolate_num += len(graph.bus_id)
            new_file.write('num of isolate bus ' + str(isolate_num) + '\n')

            new_file.close()




if __name__ == '__main__':





    # for i in range(1, 40):
    #     cal = 0.0
    #     for j in range(0, 200):
    #         g = Power_Graph()
    #         g.init_by_case(G)
    #         g.set_ramp_rate(0.5)
    #         g.delete_bus(i)
    #         cf = Power_Failure(g)
    #         cf.first_failure_process()
    #         cf.later_failure()
    #         failure_l = sorted(cf.failure_dict.items(), key=lambda item: item[1], reverse=True)
    #         final_failure = failure_l[0][1]
    #         cal += final_failure
    #     cal = cal / 200
    #     dict_cal[i] = cal
    # list_cal = sorted(dict_cal.items(), key=lambda item: item[1], reverse=True)
    # fil = open('res.txt', 'a')
    # for i in list_cal:
    #     fil.write('node_number:  ' + str(i[0]) + '           failure_rate: ' + str(i[1]) + '\n')
    # fil.close()

    '''
    G = case24_ieee_rts()
    g = Power_Graph()
    g.init_by_case(G)
    g.set_ramp_rate(0.3)
    #g.delete_bus(5)
    g.draw_P_graph()
    #print 'draw initial graph'
    cf = Power_Failure(g)

    failure_percent, current = cf.attack_random(2)#cf.attack_load(2)#cf.attack_degree(2)
    #print 'failure percent', failure_percent
    Power_Graph.draw_graph_list(cf.steady_list)
    #print 'failed bus id', cf.failed_bus_id
    for item in cf.isolate_list:
        #print 'isolate graph', item.bus_id
    for graph in cf.steady_list:
        #print 'steady graph', graph.bus_id
    '''

    save_cascade_graph()

    '''
    G = Power_Graph.case_preprocess(case300())
    g = Power_Graph()
    g.init_by_case(G)
    g.set_ramp_rate(0.3)
    cf = Power_Failure(g)
    g.delete_bus(64)
    cf.failed_bus_id.append(64)
    cf.failure_process()

    Power_Graph.draw_graph_list(cf.steady_list)
    #print 'failed bus id', cf.failed_bus_id
    for item in cf.isolate_list:
        #print 'isolate graph', item.bus_id
    for graph in cf.steady_list:
        #print 'steady graph', graph.bus_id
    '''


