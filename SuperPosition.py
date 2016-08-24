#-*- encoding: utf-8 -*-
from ObjectManager import *
from Chessman import ChessObserver

class SuperPosition:
	def __init__(self, chessID, nodeID):
		self.nodeList  = { chessID: nodeID }
	
	def getNode(self, ChessID):
		return self.nodeList.get(ChessID, None)
	
	def getProb(self, chessID, manager):
		nodeID = self.nodeList.get(chessID, -1)
		node   = manager.get(nodeID)
		return node.getProb()
	
	def add(self, ChessID, nodeID):
		if self.getNode(chessID) == None:
			self.nodeList[chessID] = nodeID

	def __distributeProb(self, ChessID, manager):
		allNode = [ manager.get(nodeID) for nodeID in self.nodeList.values()]
		allTopNode = [ node for node in allNode if node.parent==None]
		removedNodeID = self.getNode(chessID)
		removedNode   = manager.get(removedNodeID)
		prob  = removedNode.prob
		ratio = prob / (1-prob)
		for n in allTopNode:
			n.setProb( n.prob + (n.prob * ratio) )
	
	def remove(self, ChessID, observer, manager, distribute=False):
		if(self.getNode(chessID))==None:
			return
		if(distribute):
			self.__distributeProb(ChessID, manager)
		removedNodeID    = self.getNode(ChessID)
		removedNode      = manager.get(removedNodeID)
		removedChessIDs  = removedNode.destruct(observer, manager)
		for id in removedChessIDs:
			self.nodeList.pop(id, None)
	
	def removeAll(self, observer, manager, remain):
		for cid, nid in self.NodeList.items():
			if cid != remain:
				removedNode = manager.get(nid)
				removedNode.destruct(observer, manager)
		self.nodeList = { remain : self.getNode(remain) }
			
	def determine(self, nodeID, observer, manager):
		node     = manager.get(nodeID)
		subChess = manager.get(node.cid)
		if node.parent == None:
			return True
		while node.parent != None:
			node = manager.get(node.parent)	
		self.measure(node.cid, observer, manager)
		return self.getNode(subChess.id) != None
				
	def measure(self, chessID, observer, manager):
		nodeID = self.getNode(chessID)
		if nodeID == None:
			return False
		if self.determine(nodeID, observer, manager) == False:
			return False
		topNode = manager.get(nodeID)
		if(topNode.binomial()):
			prob = topNode.prob
			result = topNode.execute(1.0, chessID, observer, manager, remover=self.remove, realProb=prob)
			if result.onPos() == False:
				return False
			self.removeAll(observer, manager, remain=nodeID)
			return True
		else:
			self.remove(chessID, observer, manager, distribute=True)
			return False
			
	def checkDependency(observer, manager):
		for cid, nid in self.nodeList.items():
			node = manager.get(nid)
			node.checkDependency(observer, manager, remover=self.remove)
			
class MeasureResult:
	def __init__(self, onPos, prob=0.0, type=None):
		self.on   = onPos
		self.prob = prob
		self.type = self.type
	def onPos(self):
		return self.on
	def isChildRemoved(self):
		return type=='ClassicalNode' and self.onPos()
	def prob(self):
		if type == None or type=='ClassicalNode':
			return 0.0
		else:
			return self.prob
			
class Node:
	def __init__(self, cid, prob=1.0, parent=None, children=[]):
		self.cid        = cid
		self.prob       = prob
		self.showProb   = prob
		self.parent     = parent
		self.children   = children
		self.isEntangle = False
	
	def setProb(self, prob):
		self.prob = self.showProb = prob
	
	def getProb(self):
		return self.showProb
		
	def getPos(self, manager):
		chess = manager.get(self.cid)
		return chess.getPos()
	
	def destruct(self, observer, manager):
		chess       = manager.get(self.cid)
		result      = [self.cid]
		for nodeID in self.children:
			child = manager.get(nodeID)
			result.extend(child.destruct(observer, manager))
		self.children  = []
		self.parent    = None
		chess._removed = True
		observer.append(observedList=[], removedList=[chess])
		return result
		
	def binomial(self):
		sample = random.random()
		if(self.parent == None):
			return self.prob - sample >= 0.0
	
	def reJudge(self, realProb, observer, manager, remover, topList):
		if self.binomial():
			for nodeID in self.children:
				node = manager.get(nodeID)
				remover(node.cid, observer, manager, distribute=False)
			self.children = []
			observer.append([manager.get(self.cid)], [])
			return MeasureResult(onPos=True)
		else:
			probList = []
			self.children = []
			for nodeID in topList:
				node = manager.get(nodeID)
				node.parent = -1
				node.setProb(node.prob * realProb)
			self.setProb( (1-self.prob) * realProb)
			remover(self.cid, observer, manager, distribute=True)
			for nodeID in topList:
				node = manager.get(nodeID)
				node.parent = None
			return MeasureResult(onPos=False)
		
	def execute(self, prob, chessID, observer, manager, remover, realProb=1.0):
		self.setProb(prob)
		if chessID != self.cid: #Upgrade to top node
			return MeasureResult(onPos=True)
		topList = []
		for nodeID in self.children:
			child  = manager.get(nodeID)
			result = child.execute(self.prob/2, chessID, observer, manager, remover) 
			child.parent = None
			if result.onPos():
				if result.type != 'ClassicalNode':
					topList.append(nodeID)
				self.setProb( (self.prob / 2) + result.prob() )
			else:
				self.children = topList
				return MeasureResult(onPos=False)
		return self.reJudge(realProb, observer, manager, remover, topList)

	def checkDependency(self, observer, manager, remover):
		self.sovleDependency(observer, manager, remover)
		for nodeID in self.children:
			node = manager.get(nodeID)
			node.checkDependency(observer, manager, remover)
		
	def sovleDependency(self, observer, manager, remover):
		return None
		
class EntangleNode(Node):
	def __init__(self, s1, s2, prob=1.0, path=[]):
		self.s1 = s1
		self.s2 = s2
		self.cid = s2
		self.prob       = prob
		self.showProb   = prob
		self.parent     = s1
		self.children   = []
		self.cpath      = path
		self.isEntangle = True
	def goDown(self, observer, manager, remover, isExec=False):
		pass
	def stay(self, observer, manager, remover, isExec=False):
		pass
		
	def getNID(self, manager):
		chess = manager.get(self.cid)
		sup   = chess.getSuperposition(manager)
		return sup.getNode(self.cid)
	
	def solveMiddle(self, observer, manager):
		for ChessID in self.cpath:
			chess  = manager.get(chessID)
			chess.measure(observer, manager)
	
	def isPathClear(self, manager):
		isClear = True
		for ChessID in self.cpath:
			chess   = manager.get(chessID)
			isClear = isClear and chess._removed 
			if chess.isDetermined(manager):
				return False
		return isClear
	
	def updateStayParent(self, manager, isExec):
		parentNode = manager.get(self.parent)
		parentNode.showProb = self.prob * 2
		startIdx   = parentNode.children.index(self.getNID())
		for i in range(startIdx+1, len(parentNode.children)):
			childNode = manager.get(parentNode.children[i])
			childNode.setProb(parentNode.showProb / 2)
			parentNode.showProb = parentNode.showProb / 2
		if isExec == False:
			parentNode.children.remove(self.getNID())
	
	def updateParentTopList(self, manager, isExec):
		if isExec:
			return
		parentNode = manager.get(self.parent)
		tmpList    = parentNode.children
		for idx, nid in enumerate(parentNode.children):
			childNode = manager.get(nid)
			if childNode.isEntangle:
				break
			childNode.parent = None
			tmpList = parentNode.children[idx+1:]
		parentNode.children = tmpList
	
	def sovleDependency(self, observer, manager, remover):
		if self.isPathClear(manager):
			self.goDown(observer, manager, remover)
		for ChessID in self.cpath:
			chess   = manager.get(chessID)
			if chess.isDetermined(manager):
				self.stay(observer, manager, remover)
	
	def execute(self, prob, chessID, observer, manager, remover, realProb=1.0):
		self.setProb(prob)
		self.solveMiddle(observer, manager)
		if self.isPathClear(manager):
			return self.goDown(observer, manager, remover, isExec=True)
		else:
			return self.stay(observer, manager, remover, isExec=True)
	
class ClassicalNode(EntangleNode):
	#'ClassicalNode'
	def moveParent(self, observer, manager):
		parentNode = manager.get(self.parent)
		parentChess = manager.get(parentNode.cid)
		TargetChess = manager.get(self.cid)
		posTo       = TargetChess.getPos()
		parentChess.move(posTo)
		observer.moveChess(parentChess, parentChess.getPos(), posTo, parentChess.prob==1.0)	
		
	def goDown(self, observer, manager, remover, isExec=False):
		parentNode = manager.get(self.parent)
		parentNode.showProb = self.prob * 2
		startIdx = parentNode.children.index(self.getNID())
		for i in range(startIdx+1, len(parentNode.children)):
			remover(parentNode.children[i], observer, manager, distribute=False)
		parentNode.children = parentNode.children[0:startIdx]
		parentNode.children.remove(self.getNID())
		for nid in self.children:
			childNode = manager.get(nid)
			childNode.setProb(childNode.prob * 2)
		parentNode.children.extend(self.children)
		self.children = []
		self.moveParent(observer, manager)
		remover(self.cid, observer, manager, distribute=False)
		self.updateParentTopList(manager, isExec)
		return MeasureResult(onPos=False, prob=0.0, type='ClassicalNode')
		
	def stay(self, observer, manager, remover, isExec=False):
		self.updateStayParent(manager, isExec)
		remover(self.cid, observer, manager, distribute=False)
		return MeasureResult(onPos=True, prob=self.prob, type='ClassicalNode')

class QuantumNode(EntangleNode):
	def createNewNode(self, manager):
		newNode = Node(self.cid, self.prob, parent=self.parent, children=self.children)
		return manager.add(newNode)
		
	def updateSuperPosition(self, manager):
		newNodeID = self.createNewNode(manager)
		chess = manager.get(self.cid)
		sup   = chess.getSuperposition(manager)
		sup[chess.id] = newNodeID
		for nid in self.children:
			node = manager.get(nid)
			node.parent = newNodeID
		parentNode = manager.get(self.parent)
		idx        = parentNode.children.index(self.getNID())
		parentNode.children[idx] = newNodeID
		
	def goDown(self, observer, manager, remover, isExec=False):
		self.updateSuperPosition(manager)
		self.updateParentTopList(manager, isExec)
		return MeasureResult(onPos=True, prob=0.0)
		
	def stay(self, observer, manager, remover, isExec=False):
		self.updateStayParent(manager, isExec)
		remover(self.cid, observer, manager, distribute=False)
		return MeasureResult(onPos=True, prob=self.prob)
