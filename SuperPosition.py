#-*- encoding: utf-8 -*-
import random
from ObjectManager import *
from Chessman import ChessObserver

class SuperPosition:
	def __init__(self, chessID, nodeID):
		random.seed()
		self.nodeList  = { chessID: nodeID }
	
	def getNode(self, chessID):
		return self.nodeList.get(chessID, None)
	
	def getProb(self, chessID, manager):
		nodeID = self.getNode(chessID)
		node   = manager.get(nodeID)
		return node.getProb()
	
	def add(self, chessID, nodeID):
		if self.getNode(chessID) == None:
			self.nodeList[chessID] = nodeID

	def __distributeProb(self, chessID, manager):
		allNode = [ manager.get(nodeID) for nodeID in self.nodeList.values()]
		allTopNode = [ node for node in allNode if node.parent==None]
		removedNodeID = self.getNode(chessID)
		removedNode   = manager.get(removedNodeID)
		prob  = removedNode.prob
		ratio = prob / (1-prob)
		for n in allTopNode:
			n.setProb( n.prob + (n.prob * ratio) )
	
	def remove(self, chessID, observer, manager, distribute=False):
		print 'Before:',self.nodeList
		print 'remove:',self.getNode(chessID),manager.get(chessID).getPos().toList()
		
		if(self.getNode(chessID))==None:
			return
		if(distribute):
			self.__distributeProb(chessID, manager)
		removedNodeID    = self.getNode(chessID)
		removedNode      = manager.get(removedNodeID)
		removedChessIDs  = removedNode.destruct(observer, manager)
		for id in removedChessIDs:
			self.nodeList.pop(id, None)
		print 'After:',self.nodeList
	
	def removeAll(self, observer, manager, remain):
		for cid, nid in self.nodeList.items():
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
		nodeID = self.getNode(chessID) #nodeID can be changed
		topNode = manager.get(nodeID)
		if(topNode.binomial()):
			prob = topNode.prob
			result = topNode.execute(1.0, chessID, observer, manager, remover=self.remove, realProb=prob)
			if result.onPos() == False:
				return False
			self.removeAll(observer, manager, remain=chessID)
			return True
		else:
			self.remove(chessID, observer, manager, distribute=True)
			return False
			
	def checkDependency(self, observer, manager):
		topNodes = [ manager.get(nid) for nid in self.nodeList.values()]
		topNodes = [ node for node in topNodes if node.parent==None]
		for node in topNodes:
			node.checkDependency(observer, manager, remover=self.remove)
			
class MeasureResult:
	def __init__(self, onPos, prob=0.0, type=None):
		self.on   = onPos
		self.prob = prob
		self.type = type
	def onPos(self):
		return self.on
	def isChildRemoved(self):
		return type=='ClassicalNode' and self.onPos()
	def getProb(self):
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
		self.children   = list(children)
		self.isEntangle = False
	
	def setProb(self, prob):
		self.prob = self.showProb = prob
	
	def getProb(self):
		return self.showProb
		
	def getPos(self, manager):
		chess = manager.get(self.cid)
		return chess.getPos()
		
	def getNID(self, manager):
		chess = manager.get(self.cid)
		sup   = chess.getSuperposition(manager)
		return sup.getNode(self.cid)
		
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
				self.setProb( (self.prob / 2) + result.getProb() )
			else:
				self.children = topList + self.children
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
	
	def solveMiddle(self, observer, manager):
		for chessID in self.cpath:
			chess  = manager.get(chessID)
			chess.measure(observer, manager)
	
	def isPathClear(self, manager):
		isClear = True
		for chessID in self.cpath:
			chess   = manager.get(chessID)
			isClear = isClear and chess._removed 
			if chess.isDetermined(manager):
				return False
		return isClear
	
	def updateStayParent(self, manager, isExec):
		parentNode = manager.get(self.parent)
		parentNode.showProb = self.prob * 2
		startIdx   = parentNode.children.index(self.getNID(manager))
		for i in range(startIdx+1, len(parentNode.children)):
			childNode = manager.get(parentNode.children[i])
			childNode.setProb(parentNode.showProb / 2)
			parentNode.showProb = parentNode.showProb / 2
		if isExec == False:
			parentNode.children.remove(self.getNID(manager))
	
	def updateParentTopList(self, manager, isExec, isClassical=False):
		if isExec and not isClassical:
			return
		parentNode = manager.get(self.parent)
		tmpList    = parentNode.children
		for idx, nid in enumerate(parentNode.children):
			childNode = manager.get(nid)
			if childNode.isEntangle:
				break
			childNode.parent = None
			tmpList = parentNode.children[idx+1:]
			parentNode.setProb( childNode.prob )
		parentNode.children = tmpList
	
	def sovleDependency(self, observer, manager, remover):
		if self.isPathClear(manager):
			self.goDown(observer, manager, remover)
		for chessID in self.cpath:
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
		TargetChess.move(parentChess.getPos())
		observer.moveChess(parentChess, parentChess.getPos(), posTo, parentNode.prob==1.0)	
		
	def goDown(self, observer, manager, remover, isExec=False):
		parentNode = manager.get(self.parent)
		parentNode.showProb = self.prob * 2
		startIdx = parentNode.children.index(self.getNID(manager))
		for i in range(startIdx+1, len(parentNode.children)):
			remover(parentNode.children[i], observer, manager, distribute=False)
		parentNode.children = parentNode.children[0:startIdx]
		for nid in self.children:
			childNode = manager.get(nid)
			childNode.setProb(childNode.prob * 2)
		parentNode.children.extend(self.children)
		self.children = []
		self.moveParent(observer, manager)
		self.updateParentTopList(manager, isExec, isClassical=True)
		remover(self.cid, observer, manager, distribute=False)
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
		oldNodeID = self.getNID(manager)
		newNodeID = self.createNewNode(manager)
		chess = manager.get(self.cid)
		sup   = chess.getSuperposition(manager)
		sup.nodeList[chess.id] = newNodeID
		for nid in self.children:
			node = manager.get(nid)
			node.parent = newNodeID
		parentNode = manager.get(self.parent)
		idx        = parentNode.children.index(oldNodeID)
		parentNode.children[idx] = newNodeID
		
	def goDown(self, observer, manager, remover, isExec=False):
		self.updateSuperPosition(manager)
		self.updateParentTopList(manager, isExec)
		return MeasureResult(onPos=True, prob=0.0)
		
	def stay(self, observer, manager, remover, isExec=False):
		self.updateStayParent(manager, isExec)
		remover(self.cid, observer, manager, distribute=False)
		return MeasureResult(onPos=True, prob=self.prob)
