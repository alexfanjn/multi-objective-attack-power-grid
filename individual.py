
class individual(object):
	"""docstring for p
opulation"""
	def __init__(self, rank, be_dominated,dominate_list, f1,f2,crowding_distance,attack_list):
		super(individual, self).__init__()
		self.rank = rank
		self.be_dominated = be_dominated
		self.dominate_list = dominate_list		
		self.f1 = f1
		self.f2 = f2
		self.crowding_distance = crowding_distance
		self.attack_list = attack_list


	def print(self):
		print('f1:',self.f1,',','f2:',self.f2)

	# def __eq__(self,other):
	# 	return self.__dict__ == other.__dict__

