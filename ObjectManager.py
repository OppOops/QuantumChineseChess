
class ObjectManager:
	def __init__(self):
		self.list    = dict()
		self.idCount = 0
		
	def add(self, obj):
		id            = self.idCount
		self.list[id] = obj
		self.idCount  = self.idCount + 1
		return id
		
	def get(self, id):
		return self.list.get(id, None)
	
	def delete(self, id):
		self.list.pop(id, None)