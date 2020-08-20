
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
from individual import individual
from time import sleep
from ga import GA
import sys


class nsga2(object):
	"""docstring for nsga2"""
	def __init__(self, size,attack_num,crossover_num, iters, population_list_num):
		super(nsga2, self).__init__() 
		self.size = size
		self.attack_num = attack_num
		self.crossover_num = crossover_num
		self.iters = iters
		self.population_list_num = population_list_num

	def begin(self):
		init_list = []
		for i in range(self.size):
			init_list.append(i+1)

		init_population_list = []
		init_f1 = []
		init_f2 = []
		for i in range(self.population_list_num):
			attack_list = random.sample(init_list,self.attack_num)
			single_popu_list = individual(0,0,[],0,0,0,attack_list)
			init_population_list.append(copy.deepcopy(single_popu_list))

			#计算rp和sn
			a1,a2,a3,a4,a5 = self.attack_with_cal(init_population_list[i].attack_list)
			self.f1 = a2
			#剩余节点 a3, 连通子图 a4
			self.f2 = a4
			init_f1.append(a2)
			init_f2.append(a3)

		print('---initial values---')
		print('init_f1',init_f1)
		print('init_f2',init_f2)
		self.fast_non_dominated_sort(init_population_list)

		
		pc = 0.5
		pm = 0.8
		return init_population_list,pc,pm,init_f1,init_f2


	def dominate(self,p1,p2):
		if p1.f1 <= p2.f1 and p1.f2 <= p2.f2:
			return True 
		return False

	def fast_non_dominated_sort(self,population_list):
		F = []
		F1 = []
		for p in population_list:
			p.dominate_list = []
			p.be_dominated = 0
			for q in population_list:
				if self.dominate(p,q):
					p.dominate_list.append(q)
				elif self.dominate(q,p):
					p.be_dominated += 1
				else:
					pass

			#print(p.f1,p.dominate_list,p.be_dominated)

			if p.be_dominated == 0:
				p.rank = 1
				F1.append(p)
		F.append(F1)

		i = 0
		while len(F[i])>0:
			Q = []
			for p in F[i]:
				#print(p.dominate_list)
				for q in p.dominate_list:
					q.be_dominated -= 1
					if q.be_dominated == 0:
						q.rank = i + 2
						Q.append(q)
			F.append(Q)
			i += 1
		return F

	def sort_by_object(self,partial_list,m):
		#根据f1排序
		if m == 1:
			partial_list.sort(key=lambda x:x.f1)
		#根据f2排序
		else:
			partial_list.sort(key=lambda x:x.f2)

		return partial_list


	def crowding_distance_sort(self,partial_list):
		if len(partial_list) == 1:
			return partial_list

		l = len(partial_list)
		for i in range(l):
			partial_list[i].crowding_distance = 0
		for i in range(2):
			partial_list = self.sort_by_object(partial_list,i+1)

			partial_list[0].crowding_distance = 10000
			partial_list[-1].crowding_distance = 10000
			#f1
			if i == 0:
				fmax = partial_list[-1].f1
				fmin = partial_list[0].f1
				for j in range(1,l-1):
					if fmax == fmin:
						continue
					temp = (partial_list[j+1].f1 - partial_list[j-1].f1)/(fmax-fmin)
					partial_list[j].crowding_distance += temp
			#f2
			else :
				fmax = partial_list[-1].f2
				fmin = partial_list[0].f2
				for j in range(1,l-1):
					if fmax == fmin:
						continue
					temp = (partial_list[j+1].f2 - partial_list[j-1].f2)/(fmax-fmin)
					partial_list[j].crowding_distance += temp

		partial_list.sort(key=lambda x:x.crowding_distance,reverse=True)
		return partial_list


	def crossover_operation(self,population_list,pc):
		parent_child_list = copy.deepcopy(population_list)
		list = np.arange(len(population_list)).tolist()

		tag_list = np.arange(self.size).tolist()
		for i in range(len(tag_list)):
			tag_list[i] = i+1

		if self.attack_num == 2:
			extra_size = 1
		else:
			extra_size = 2
		for i in range(int(len(population_list)/2)):
			a,b = random.sample(list,2)
			#删除已选择的两个个体
			list.remove(a)
			list.remove(b)
			#print(list)
			child_a = copy.deepcopy(population_list[a])
			child_b = copy.deepcopy(population_list[b])
			attack_list_a,attack_list_b,flag = self.crossover(copy.deepcopy(child_a.attack_list),copy.deepcopy(child_b.attack_list),pc)

			#重组之后attack_list没有变化,则随机从外面选一个

			if set(attack_list_a) == set(child_a.attack_list) and np.random.uniform(0,1) > 0.5 and flag:

				tag = copy.deepcopy(tag_list)
				for i in range(len(attack_list_a)):
					if attack_list_a[i] in tag:
						tag.remove(attack_list_a[i])
				remove_node = random.sample(attack_list_a,extra_size)
				attack_list_a.remove(remove_node[0])
				# attack_list_a.remove(remove_node[1])


				add_node = random.sample(tag,extra_size)
				attack_list_a.append(add_node[0])

			if set(attack_list_b) == set(child_b.attack_list) and np.random.uniform(0,1) > 0.5 and flag:
				tag = copy.deepcopy(tag_list)
				for i in range(len(attack_list_b)):
					if attack_list_b[i] in tag:
						tag.remove(attack_list_b[i])
				remove_node = random.sample(attack_list_b,extra_size)
				attack_list_b.remove(remove_node[0])

				add_node = random.sample(tag,extra_size)
				attack_list_b.append(add_node[0])



			child_a.attack_list = attack_list_a
			child_b.attack_list = attack_list_b

			

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

			for i in range(len(cross_list_b)):
				#原有的去除
				if cross_list_a[i] in population_list_a:
					population_list_a.remove(cross_list_a[i])
				#新增重组的
				if cross_list_b[i] not in population_list_a:
					population_list_a.append(cross_list_b[i])


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
			if i < len(population_list)/2:
				continue
			if np.random.uniform(0,1) > pm:
				#构建候选点
				under_list = []
				for k in range(self.size):
					j = k+1
					if j not in population_list[i].attack_list:
						under_list.append(j)
				delete_node_id = random.sample(population_list[i].attack_list,1)
				#print(delete_node_id)
				#print(population_list[i])
				population_list[i].attack_list.remove(delete_node_id[0])
				add_node_id = random.sample(under_list,1)
				population_list[i].attack_list.append(add_node_id[0])
		return population_list


	def cal_function(self,population_list):
		ab_array = np.zeros((len(population_list),4))
		#print(ab_array)
		temp_f1 = []
		temp_f2 = []

		for i in range(len(population_list)):
			# print('attack_list',population_list[i].attack_list)
			a1,a2,a3,a4,a5 = self.attack_with_cal(population_list[i].attack_list)
			#重新计算目标函数值
			population_list[i].f1 = a2
			#改为a3
			population_list[i].f2 = a4
			temp_f1.append(a2)
			temp_f2.append(a4)
			ab_array[i,0] = a1
			ab_array[i,1] = a2 
			ab_array[i,2] = a3
			ab_array[i,3] = a4  
			#print(a5)

		print('temp_f1/f2')
		print(temp_f1)
		print(temp_f2)

		return population_list,ab_array


	def cal_matrix(self,g):
		matrix = np.zeros((self.size,self.size),dtype=int)

		for item in g.branch:
			i = int(item[0])-1
			j = int(item[1])-1
			matrix[i,j] = matrix[j,i] = 1

		return matrix

	def cal_n_c(self,matrix1):

		eig_list,eig_vec = np.linalg.eig(matrix1)
		eig_list = eig_list.astype(np.float64)

		temp_sum = 0
		for i in range(len(eig_list)):
			temp_sum += np.exp(eig_list[i])

		natural_connectivity = np.log(temp_sum/len(matrix1))
		return natural_connectivity




	def attack_with_cal(self,attack_list):

		if self.size == 118:
			G = case118()
		elif self.size == 500:
			G = case500()
		elif self.size == 2383:
			G = case2383()
		elif self.size == 300:
			G = case300()


		g = Power_Graph()
		new_case = g.case_preprocess(G)
		g.init_by_case(G)
		g.set_ramp_rate(0.3)

		matrix1 = self.cal_matrix(g)
		natural_connectivity_format = self.cal_n_c(matrix1)

		#print(g.edge_list)

		for k in attack_list:
			g.delete_bus(k)


		cf = Power_Failure(g)
		cf.failure_process()


		matrix2 = self.cal_matrix(g)
		natural_connectivity_last = self.cal_n_c(matrix2)



		ini_g = Power_Graph()
		ini_g.init_by_case(G)


		gr = Attack(cf.steady_list, ini_g, cf.isolate_list)

		#画图
		#g.draw_graph_list(gr.steady_list)

		residual_node = 0
		max_subgraph_node = 0
		for sub_graph in gr.steady_list:
			if max_subgraph_node < len(sub_graph.bus_id):
				max_subgraph_node = len(sub_graph.bus_id)
			residual_node += len(sub_graph.bus_id)

		rn_decrease_per = residual_node / self.size
		
		max_subgraph_node_decrease_per = max_subgraph_node / self.size

		nc_decrease_per = (natural_connectivity_format - natural_connectivity_last)/natural_connectivity_format
		rp_decrease_per = gr.cal_residual_power()
		return nc_decrease_per,rp_decrease_per,rn_decrease_per,max_subgraph_node_decrease_per,g.degree


	def find_the_best(self,population_list,F):
		return F[0]


	def discard_same(self,population_list):
		attack_lists = []
		for i in range(len(population_list)):
			attack_list = population_list[i].attack_list
			attack_lists.append(sorted(attack_list))

		length1 = len(population_list)


		attack_lists = list(set(tuple(t) for t in attack_lists))
		attack_lists = [list(v) for v in attack_lists]



		#设置候选节点集
		tag_list = np.arange(self.size).tolist()
		for i in range(len(tag_list)):
			tag_list[i] = i+1


		while len(attack_lists) < length1:
			attack_list = random.sample(tag_list,self.attack_num)
			attack_lists.append(attack_list)



		for i in range(len(population_list)):
			population_list[i].attack_list = copy.deepcopy(attack_lists[i])

		return population_list


	def main(self,t):
		population_list, pc, pm,init_f1,init_f2 = self.begin()

		#循环迭代500次
		flag = True
		iter = 0
		after_F = []
		k = 0
		while flag:
			print('\nt,iter,k：', t,iter,k)

			before_F = copy.deepcopy(after_F)
			population_list = self.crossover_operation(population_list,pc)


			#执行变异操作
			#list包含parent和child
			population_list = self.mutation(population_list,pm)

			#此时的population_list是已经经过变异操作的个体种群


			population_list = self.discard_same(population_list)

			#计算目标函数值
			population_list,ab_array = self.cal_function(population_list)


			F = self.fast_non_dominated_sort(population_list)
			#print(F)
			i = 0
			f1_list = []
			f2_list = []
			while len(F[i]) > 0:
				for j in range(len(F[i])):
					f1_list.append(F[i][j].f1)
					f2_list.append(F[i][j].f2)
				i += 1

			

				
			new_population_list = []
			i = 0
			#没有超过种群总限制时，直接将Fi加入
			while len(new_population_list) + len(F[i]) <= self.population_list_num:
				for j in range(len(F[i])):
					new_population_list.append(F[i][j])
				i += 1
			if len(new_population_list) < self.population_list_num:
				need = self.population_list_num - len(new_population_list)
				#直接使用i，不用+1也不用-1
				#对fi进行拥挤距离计算
				F[i] = self.crowding_distance_sort(F[i])
				#print(F[i])
				j = 0
				while j < need:
					new_population_list.append(F[i][j])
					j += 1
			population_list = new_population_list
			after_F = copy.deepcopy(F[0])
			best_list = self.find_the_best(population_list,F)

			#判断是否收敛
			tag = self.converge(before_F,after_F)

			if tag:
				k += 1
			else:
				k = 0

			iter += 1

			if tag and k >= 30 or iter >=500:
				print("---")
				print("iter:",iter)
				print("---")

				flag = False


		best_list  = self.find_the_best(population_list,F)

		return best_list,population_list,ab_array,iter,init_f1,init_f2

	def converge(self,before_F,after_F):
		#数据预处理
		before_attack_list = []
		after_attack_list = []
		for i in range(len(before_F)):
			#print(type(before_F[i].attack_list))
			before_attack_list.append(sorted(before_F[i].attack_list))
			#print("111:",before_F[i].attack_list)

		for i in range(len(after_F)):
			after_attack_list.append(sorted(after_F[i].attack_list))

		before_attack_list = list(set(tuple(t) for t in before_attack_list))
		before_attack_list = [list(v) for v in before_attack_list]

		after_attack_list = list(set(tuple(t) for t in after_attack_list))
		after_attack_list = [list(v) for v in after_attack_list]


		len1 = len(before_attack_list)
		len2 = len(after_attack_list)
		if len1 != len2 or len1==len2==0 :
			return False



		# print(before_attack_list)
		# print(after_attack_list)


		#print(before_F[0])
		flag = True
		for f in before_attack_list:
			if f not in after_attack_list:
				flag = False
				return flag
		return flag


def calhv(best_list):
	f_list = []
	for i in range(len(best_list)):
		a = best_list[i].f1
		b = best_list[i].f2
		temp = (a,b)
		f_list.append(temp)
	#print(f_list)
	f_list = sorted(f_list)
	hv = 0
	for i in range(len(f_list)-1):
		hv = hv + (f_list[i+1][0] - f_list[i][0]) * f_list[i][1]
	#leftest one
	hv = hv + f_list[0][0]

	#rightest one
	hv = hv + (1 - f_list[-1][0]) * f_list[-1][1]

	hv = 1 - hv

	return hv

def doc(t):

	nsga = nsga2(300,10,5,500,60)

	best_list,population_list,ab_array,iter,init_f1,init_f2 = nsga.main(t)


	f1_list = []
	f2_list = []
	attack_lists = []


	hv = calhv(best_list)
	print('hv:',hv)

	print('--best_list---')
	print(len(best_list))
	for i in range(len(best_list)): 
		print(best_list[i].attack_list)
		print(best_list[i].f1,best_list[i].f2)
		attack_lists.append(best_list[i].attack_list)
		f1_list.append(best_list[i].f1)
		f2_list.append(best_list[i].f2)
	print('-----')

	avg_rp = np.mean(f1_list)
	avg_msn = np.mean(f2_list)

	f3_list = []
	f4_list = []
	for i in range(len(population_list)):
		print(population_list[i].attack_list)
		print(population_list[i].f1,population_list[i].f2)
		if population_list[i] not in best_list:
			f3_list.append(population_list[i].f1)
			f4_list.append(population_list[i].f2)

	print('优化前')
	print(f1_list)
	print(f2_list)

	print('---initial values---')
	print('init_f1', init_f1)
	print('init_f2', init_f2)


	return iter,best_list,hv,len(best_list)




if __name__ == '__main__':



	iter_list = []
	best_lists = []
	hv_list = []
	len_lists = []
	for i in range(50):
		iter,best_list,hv,len_list = doc(i)
		iter_list.append(iter)
		best_lists.append(best_list)
		hv_list.append(hv)
		len_lists.append(len_list)
	print(iter_list)

	print('average:', np.mean(iter_list),np.mean(hv_list),np.mean(len_lists))


	all_list = []
	for i in range(len(best_lists)):

		for j in range(len(best_lists[i])):
			print('i,attack_list,f1,f2',i,best_lists[i][j].attack_list,best_lists[i][j].f1,best_lists[i][j].f2)
			all_list.append(best_lists[i][j].attack_list)

