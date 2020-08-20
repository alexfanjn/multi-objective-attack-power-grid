# -*- coding: utf-8 -*-

import numpy as np
import copy
import random
import matplotlib.pyplot as plt
from Power_Failure import Power_Failure
from Graph import Power_Graph

from pypower.case118 import case118

from pypower.case300 import case300

from pypower.case500 import case500
from pypower.case2383 import case2383

from pypower.rundcpf import rundcpf
from time import clock
import heapq
from Attack import Attack
from time import sleep
import math
import time

class SGA(object):
	"""docstring for ClassName"""
	def __init__(self,size,attack_num,crossover_num,iters,population_list_num):
		super(SGA, self).__init__()
		self.size = size
		self.attack_num = attack_num
		self.crossover_num = crossover_num
		self.iters = iters
		self.population_list_num = population_list_num

	def begin(self,size):
		#sleep(1)
		init_list = []
		for i in range(size):
			init_list.append(i+1)

		init_population_list = []

		for i in range(self.population_list_num):
			single_popu_list = []
			single_popu_list = random.sample(init_list,self.attack_num)
			init_population_list.append(copy.deepcopy(single_popu_list))
		pc = 0.5
		pm = 0.8
		return init_population_list,pc,pm


	def crossover_operation(self,population_list,pc):
		#print(len(population_list))
		parent_child_list = copy.deepcopy(population_list)
		#生成一个0-19，大小为20的序列
		list = np.arange(len(population_list)).tolist()


		#结点编号list
		tag_list = np.arange(self.size).tolist()
		for i in range(len(tag_list)):
			tag_list[i] = i+1

		if self.size == 57:
			extra_size = 1
		else:
			extra_size = 2
		#print(list)
		#print(int(len(population_list)/2))
		for i in range(int(len(population_list)/2)):
			a,b = random.sample(list,2)
			#删除已选择的两个个体
			list.remove(a)
			list.remove(b)
			#print(list)
			child_a,child_b,flag = self.crossover(copy.deepcopy(population_list[a]),copy.deepcopy(population_list[b]),pc)

			if set(child_a) == set(population_list[a]) and np.random.uniform(0,1) > 0.5 and flag:

				tag = copy.deepcopy(tag_list)
				for i in range(len(child_a)):
					if child_a[i] in tag:
						tag.remove(child_a[i])
				remove_node = random.sample(child_a,extra_size)
				child_a.remove(remove_node[0])
				if self.size != 57:
					child_a.remove(remove_node[1])


				add_node = random.sample(tag,extra_size)
				child_a.append(add_node[0])
				if self.size != 57:
					child_a.append(add_node[1])


			if set(child_b) == set(population_list[a]) and np.random.uniform(0,1) > 0.5 and flag:

				tag = copy.deepcopy(tag_list)
				for i in range(len(child_b)):
					if child_b[i] in tag:
						tag.remove(child_b[i])
				remove_node = random.sample(child_b,extra_size)
				child_b.remove(remove_node[0])
				if self.size != 57:
					child_b.remove(remove_node[1])

				add_node = random.sample(tag,extra_size)
				child_b.append(add_node[0])
				if self.size != 57:
					child_b.append(add_node[1])



			parent_child_list.append(copy.deepcopy(child_a))
			parent_child_list.append(copy.deepcopy(child_b))

		return parent_child_list


	def crossover(self,population_list_a,population_list_b,pc):
		#随机将每个个体的交换两个

		length = len(population_list_a)

		child_a = population_list_a
		child_b = population_list_b

		tag = False

		if np.random.uniform(0,1) > pc:
			#满足基因重组条件
			#随机挑选两个点交换
			tag = True
			cross_list_a = random.sample(population_list_a,self.crossover_num)
			cross_list_b = random.sample(population_list_b,self.crossover_num)


			i = 0
			while i < len(population_list_a):
				if population_list_a[i] in cross_list_b:
					population_list_a.remove(population_list_a[i])
				else:
					i+=1
			#print(1,len(child_a),len(child_b))

			for i in range(len(cross_list_b)):
				#原有的去除
				if cross_list_a[i] in population_list_a:
					population_list_a.remove(cross_list_a[i])
				#新增重组的
				if cross_list_b[i] not in population_list_a:
					population_list_a.append(cross_list_b[i])

			#print(2,len(child_a),len(child_b))

			if(len(population_list_a) < length):
				need = length - len(population_list_a)
				#构建候选list
				under_list = []
				for i in range(self.size):
					j = i+1
					if j not in population_list_a:
						under_list.append(j)
				select_list = random.sample(under_list,need)

				for i in range(need):
					population_list_a.append(select_list[i])

			child_a = population_list_a
			#print(3,len(child_a),len(child_b))


			i = 0
			while i < len(population_list_b):
				if population_list_b[i] in cross_list_a:
					population_list_b.remove(population_list_b[i])
				else:
					i+=1

			for i in range(len(cross_list_a)):
				if cross_list_b[i] in population_list_b:
					population_list_b.remove(cross_list_b[i])
				if cross_list_a[i] not in population_list_b:
					population_list_b.append(cross_list_a[i])

			if(len(population_list_b) < length):
				need = length - len(population_list_b)
				#构建候选list
				under_list = []
				for i in range(self.size):
					j = i+1
					if j not in population_list_b:
						under_list.append(j)
				select_list = random.sample(under_list,need)
				for i in range(need):
					population_list_b.append(select_list[i])

			child_b = population_list_b


		return child_a,child_b,tag






	def mutation(self,population_list,pm):
		for i in range(len(population_list)):
			#达到变异条件
			if np.random.uniform(0,1) > pm:
				#构建候选点
				under_list = []
				for k in range(self.size):
					j = k+1
					if j not in population_list[i]:
						under_list.append(j)
				delete_node_id = random.sample(population_list[i],1)
				#print(delete_node_id)
				#print(population_list[i])
				population_list[i].remove(delete_node_id[0])
				add_node_id = random.sample(under_list,1)
				population_list[i].append(add_node_id[0])
		return population_list


	def elite_retention(self,population_list,tar):
		final_list = []
		#采用2路锦标赛算法事项精英保留策略
		tag = []
		for i in range(len(population_list)):
			tag.append(i)

		ab_array = np.zeros((self.population_list_num,4))
		#print(ab_array)
		for i in range(self.population_list_num):
			#随机选择两个序号，然后再将他们从taglist中删除
			# print("第%d个节点序列\n",i)
			a,b = random.sample(tag,2)
			tag.remove(a)
			tag.remove(b)
			a1,a2,a3,a4,lista = self.attack_with_cal(self.size,population_list[a])

			b1,b2,b3,b4,listb = self.attack_with_cal(self.size,population_list[b])
			#print(length_a,length_b)
			#看谁更接近self.target


			temp1 = temp2 = 0
			if tar == 1:
				temp1 = a2
				temp2 = b2
			elif tar == 2:
				temp1 = a4
				temp2 = b4
			else:
				temp1 = a2 + a4
				temp2 = b2 + b4

			if temp1 <= temp2:
				#a list是更优的路径
				final_list.append(population_list[a])
				ab_array[i,0] = a1
				ab_array[i,1] = a2 
				ab_array[i,2] = a3
				ab_array[i,3] = a4  
				#print(length_a)
			else:
				final_list.append(population_list[b])
				ab_array[i,0] = b1
				ab_array[i,1] = b2 
				ab_array[i,2] = b3
				ab_array[i,3] = b4 
				#print(length_b)
		return final_list,ab_array


	def cal_matrix(self,g,size):
		matrix = np.zeros((size,size),dtype=int)

		for item in g.branch:
			i = int(item[0])-1
			j = int(item[1])-1
			matrix[i,j] = matrix[j,i] = 1

		return matrix

	def  cal_n_c(self,matrix1):

		eig_list,eig_vec = np.linalg.eig(matrix1)
		eig_list = eig_list.astype(np.float64)

		temp_sum = 0
		for i in range(len(eig_list)):
			temp_sum += np.exp(eig_list[i])

		natural_connectivity = np.log(temp_sum/len(matrix1))
		return natural_connectivity




	def attack_with_cal(self,size,attack_list):
		if size == 118:
			G = case118()
		elif size == 500:
			G = case500()
		elif size == 300:
			G = case300()
		elif size == 2383:
			G = case2383()


		g = Power_Graph()
		new_case = g.case_preprocess(G)
		g.init_by_case(G)
		g.set_ramp_rate(0.3)

		matrix1 = self.cal_matrix(g,size)
		natural_connectivity_format = self.cal_n_c(matrix1)

		for k in attack_list:
			g.delete_bus(k)

		cf = Power_Failure(g)
		cf.failure_process()


		matrix2 = self.cal_matrix(g,size)
		natural_connectivity_last = self.cal_n_c(matrix2)


		ini_g = Power_Graph()
		ini_g.init_by_case(G)


		gr = Attack(cf.steady_list, ini_g, cf.isolate_list)

		residual_node = 0
		max_subgraph_node = 0
		for sub_graph in gr.steady_list:
			if max_subgraph_node < len(sub_graph.bus_id):
				max_subgraph_node = len(sub_graph.bus_id)
			residual_node += len(sub_graph.bus_id)

		rn_per = residual_node / size
		max_subgraph_node_per = max_subgraph_node / size

		nc_decrease_per = natural_connectivity_last/natural_connectivity_format
		rp = gr.cal_residual_power()
		return nc_decrease_per,rp,rn_per,max_subgraph_node_per,attack_list


	def find_the_best(self,population_list,ab_array,tar):
		change_list = []
		min = 50000
		index = -1
		temp1 = 0
		temp2 = 0
		if tar == 1:
			temp1 = 1
		elif tar == 2:
			temp1 = 3
		else:
			temp1 = 1
			temp2 = 3
		for i in range(len(population_list)):
			if tar == 3:
				change_list.append(ab_array[i,temp1]+ab_array[i,temp2])
			else:
				change_list.append(ab_array[i,temp1])
			if change_list[i] < min:
				min = change_list[i]
				index = i
		print('min:',index,min)
		return index,min



	def main(self,tar):
		population_list, pc, pm = self.begin(self.size)

		new_min = 100
		old_min = new_min
		k = 0

		old_list = []
		#循环迭代500次
		flag = True
		iter = 0
		f1_list = []
		f2_list = []
		ab_array = np.zeros((self.population_list_num,4))

		while flag:
			print('\niter,k：', iter,k)

			iter += 1
			if math.fabs(old_min - new_min) <= 0.0001:
				k+=1
			else:
				k = 0
			if k >= 60 or iter >= 500:
				flag = False

			a,b = self.find_the_best(population_list,ab_array,tar)
			old_list = copy.deepcopy(population_list[a])
			temp_a = ab_array[a]

			old_min = new_min
			#记得list的更新问题！！！
			#此时的population_list有40个
			print('start corssover')
			population_list = self.crossover_operation(population_list,pc)

			#执行变异操作
			print('start mutation')

			population_list = self.mutation(population_list,pm)

			#此时的population_list是已经经过变异操作的个体种群
			#进行精英保留策略
			print('elite retention')

			population_list,ab_array = self.elite_retention(population_list,tar)


			index,new_min = self.find_the_best(population_list,ab_array,tar)


			print(ab_array[index])
			f1_list.append(ab_array[index][1])
			f2_list.append(ab_array[index][3])
			print('---')
			print(f1_list)
			print(f2_list)
			f3_list = []
			for i in range(len(f1_list)):
				f3_list.append(f1_list[i] + f2_list[i])
			print(f3_list)
			print('---')

		index,last_min = self.find_the_best(population_list,ab_array,tar)
		print(ab_array[index])
		print(ab_array)

		avg = np.mean(ab_array,axis=0)
		print('avg',avg)


		return ab_array,population_list,f1_list,f2_list,ab_array[index][1],ab_array[index][3]




if __name__ == '__main__':


	for i in range(1):
		sga = SGA(300,10,5,500,60)

		al_list = []
		new_min_list_a = []
		new_min_list_b = []

		# tar->1:fr, 2:sv, 3:sv+fv
		ab_array,population_list,f1_list,f2_list,a,b = sga.main(1)
		new_min_list_a.append(a)
		new_min_list_b.append(b)
		for i in range(len(population_list)):

			print(ab_array[i])
			print(population_list[i])
			al_list = al_list + population_list[i]
			print('\n')

		print(f1_list)
		print(f2_list)
		print(al_list)
