#-*- encoding: utf-8 -*-
from Chessman import ChessObserver

class Vertex:
	_isMarked = False
	def __init__(self, chessList, chessboard, time, isQuantumMove=False):
		self.s1         = chessList[0]
		self.s2         = chessList[-1]
		self.list       = chessList
		self.Path       = chessList[1:-1]
		self.edgeList   = []
		self.chessboard = chessboard
		self.time       = time
		self.softSolve  = False
		if isQuantumMove:
			self.solve = self.QuantumMeasure
		else:
			self.solve = self.ClassicalMeasure
	
	def copy(self, mapDict, chessboard):
		getchess = lambda p : chessboard.get(p.toList(), None)
		self.edgeList   = [ mapDict[p.time] for p in self.edgeList]
		self.s1         = getchess(self.s1._pos)
		self.s2         = getchess(self.s2._pos)
		self.list       = [ getchess(ch._pos) for ch in self.list]
		self.Path       = [ getchess(ch._pos) for ch in self.Path]
	
	def destruct(self):
		for ch in self.list:
			ch.entangleKey = None
	
	def isCritical(self, chess):
		return chess==self.s1 or chess==self.s2
	
	def determinedChess(self, chess):
		return chess in self.list
	
	def removeChess(self, chess):
		if not chess in self.list:
			return False
		if chess == self.s1 or chess == self.s2:
			return True
		else:
			isClear     = sum([ 1 for ch in self.Path if ch._removed==False ]) == 0
			if isClear and self.solve == self.QuantumMeasure:
				self.softSolve = True
			return isClear
			
	def getDependency(self):
		allEntangleChess = [ch for ch in self.list if ch.entangleKey != None]
		allEntangleGroup = [ch.entangleKey for ch in allEntangleChess    ]
		return list(set(allEntangleGroup))
	
	def _groupSuper(self, clist):
		mapDict = {}
		for c in clist:
			if c._removed==True:
				continue
			lsp       = tuple(c._superpositions)
			container = mapDict.get(lsp, None)
			if container == None:
				mapDict[lsp] = [c]
			else:
				container.append(c)
		return list(mapDict.values())
	
	def conditionSolve(self, independentList, observer, boolfunc=None):
		tmpObserver = ChessObserver(self.chessboard)
		measureList = self._groupSuper(independentList)
		print('MeasureList:  ',measureList)
		for group in measureList:
			other = set(group) - set([group[0]])
			tmpObserver.observeSimple(group[0], list(other))
		#combine two result
		res = tmpObserver.getResult()
		for pos, val in res:
			if val!=None:
				print(pos.toList(), val._probability)
			else:
				print(pos.toList(), None)
		
		observer.combine(tmpObserver)
		if boolfunc!=None:
			result = sum([1 for ch in independentList if boolfunc(ch._removed)])
			atLeastOneSucess = bool(result > 0)
			return atLeastOneSucess
		
	def QuantumMeasure(self, observer):
		#觀測後，兩側至少有一側真的在位置上
		sideChess      = [self.s1, self.s2]
		boolfunc       = lambda chIsremoved : chIsremoved==False
		
		# Solve by binomial process:
		if self.softSolve:
			pass
		elif self.conditionSolve(sideChess, observer, boolfunc):
			self.ClassicalMeasure(observer)
		else:
			self.conditionSolve(self.Path, observer)
		self.destruct()
		
	def ClassicalMeasure(self, observer):
		#當有障礙時，移除s2;否則移除s1
		sideChess      = self.Path
		boolfunc       = lambda chIsremoved : chIsremoved==False
		print(self.s1._pos.toList(),len(self.s1._superpositions), self.s1._removed)
		print(self.s2._pos.toList(),len(self.s2._superpositions), self.s2._removed)
		# Solve by binomial process:
		if self.conditionSolve(sideChess, observer, boolfunc):
			observer.remove(self.s2)
		else:
			observer.remove(self.s1)
		self.destruct()

class Graph:
	def __init__(self):
		self.timeSequence = []
		self.time = 0
	
	def copy(self, chessboard):
		tmpDict = {}
		for tn in self.timeSequence:
			tmpDict[tn.time] = tn
		for tn in self.timeSequence:
			tn.copy(tmpDict, chessboard)
	
	def findCriticalGroup(self, chess):
		for i in range(len(self.timeSequence)-1,-1,-1):
			if(self.timeSequence[i].isCritical(chess)):
				return self.timeSequence[i]
		return None
	
	def addKey(self, key):
		self.timeSequence.append(key)
		self.time = self.time + 1
		
	def remove(self, key):
		if key in self.timeSequence:
			self.timeSequence.remove(key)
		print(self.timeSequence, self.time)
			
	def entangleSolve(self, node, observer):
		if node._isMarked:
			return
		node._isMarked = True
		for parent in node.edgeList:
			self.entangleSolve(parent, observer)
		node.solve(observer)
		self.remove(node)
		
	def checkDependency(self, observer):
		chessList = observer.getDetermined()
		for chess, isDetermined in chessList:
			for tn in self.timeSequence:
				if (not isDetermined) and tn.removeChess(chess):
					self.entangleSolve(tn, observer)
				elif ( isDetermined ) and tn.determinedChess(chess):
					self.entangleSolve(tn, observer)
					
	def trySolve(self, chess, observer):
		CriticalNode = self.findCriticalGroup(chess)
		if CriticalNode==None:
			observer.observeSimple(chess)
		else:
			self.entangleSolve(CriticalNode, observer)
	
	def LinkParent(self, chessList, newVertex):
		result = []
		for ch in chessList:
			if ch.entangleKey != None:
				result += ch.entangleKey.getDependency()
		newVertex.edgeList = list(set(result))
		
	def markLatest(self, chessList, newVertex):
		for ch in chessList:
			ch.entangleKey = newVertex
	
	def buildVertex(self, chessList, chessboard, isQuantumMove=False):
		newVertex = Vertex(chessList, chessboard, self.time, isQuantumMove)
		self.addKey(newVertex)
		self.LinkParent(chessList, newVertex)
		self.markLatest(chessList, newVertex)