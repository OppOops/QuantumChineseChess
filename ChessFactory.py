#-*- encoding: utf-8 -*-
import copy
from Chessman import *
from ChessGlobal import *
from SuperPosition import *

class ChessBoardStart:
	@staticmethod
	def initBoard():
		return {
		   (0, 0):ChessmanJu(self, CHESSMAN_COLOR_RED,0, 0),  \
		   (0, 1):ChessmanMa(self, CHESSMAN_COLOR_RED,      0, 1),  \
		   (0, 2):ChessmanXiang(self, CHESSMAN_COLOR_RED,   0, 2),  \
		   (0, 3):ChessmanShi(self, CHESSMAN_COLOR_RED,     0, 3),  \
		   (0, 4):ChessmanJiang(self, CHESSMAN_COLOR_RED,   0, 4),  \
		   (0, 5):ChessmanShi(self, CHESSMAN_COLOR_RED,     0, 5),  \
		   (0, 6):ChessmanXiang(self, CHESSMAN_COLOR_RED,   0, 6),  \
		   (0, 7):ChessmanMa(self, CHESSMAN_COLOR_RED,      0, 7),  \
		   (0, 8):ChessmanJu(self, CHESSMAN_COLOR_RED,      0, 8),  \
		   (9, 0):ChessmanJu(self, CHESSMAN_COLOR_BLACK,    9, 0 ),  \
		   (9, 1):ChessmanMa(self, CHESSMAN_COLOR_BLACK,    9, 1),  \
		   (9, 2):ChessmanXiang(self, CHESSMAN_COLOR_BLACK, 9, 2),  \
		   (9, 3):ChessmanShi(self, CHESSMAN_COLOR_BLACK,   9, 3),  \
		   (9, 4):ChessmanJiang(self, CHESSMAN_COLOR_BLACK, 9, 4),  \
		   (9, 5):ChessmanShi(self, CHESSMAN_COLOR_BLACK, 9, 5),  \
		   (9, 6):ChessmanXiang(self, CHESSMAN_COLOR_BLACK, 9, 6),  \
		   (9, 7):ChessmanMa(self, CHESSMAN_COLOR_BLACK, 9, 7),  \
		   (9, 8):ChessmanJu(self, CHESSMAN_COLOR_BLACK, 9, 8),  \
		   (2, 1):ChessmanPao(self, CHESSMAN_COLOR_RED, 2, 1),  \
		   (2, 7):ChessmanPao(self, CHESSMAN_COLOR_RED, 2, 7),  \
		   (7, 1):ChessmanPao(self, CHESSMAN_COLOR_BLACK, 7, 1),  \
		   (7, 7):ChessmanPao(self, CHESSMAN_COLOR_BLACK, 7, 7),  \
		   (3, 0):ChessmanBing(self, CHESSMAN_COLOR_RED, 3, 0),  \
		   (3, 2):ChessmanBing(self, CHESSMAN_COLOR_RED, 3, 2),  \
		   (3, 4):ChessmanBing(self, CHESSMAN_COLOR_RED, 3, 4),  \
		   (3, 6):ChessmanBing(self, CHESSMAN_COLOR_RED, 3, 6),  \
		   (3, 8):ChessmanBing(self, CHESSMAN_COLOR_RED, 3, 8),  \
		   (6, 0):ChessmanBing(self, CHESSMAN_COLOR_BLACK, 6, 0),  \
		   (6, 2):ChessmanBing(self, CHESSMAN_COLOR_BLACK, 6, 2),  \
		   (6, 4):ChessmanBing(self, CHESSMAN_COLOR_BLACK, 6, 4),  \
		   (6, 6):ChessmanBing(self, CHESSMAN_COLOR_BLACK, 6, 6),  \
		   (6, 8):ChessmanBing(self, CHESSMAN_COLOR_BLACK, 6, 8),  \
		}
	@staticmethod
	def initColor():
		return CHESSMAN_COLOR_RED

class ChessmanBuilder:
	def __init__(self, manager):
		self.mgr = manager
	def buildChess(self, chess, pos):
		pass
	def setSuperpos(self, chess, nodeID):
		pass
	def buildNode(self, chess, chessTo, builder):
		return builder.build(chess, chessTo)
		
	def build(self, chess, builder=NodeBuilder(), pos=None):
		newChess = self.buildChess(chess, pos)
		nodeID   = self.buildNode(chess, newChess, builder)
		self.setSuperpos(newChess, nodeID)
		return newChess
	
class ClassicalChessBuilder(ChessmanBuilder):
	def buildChess(self, chess, pos):
		chess.id  = self.mgr.add(chess)
		return chess
		
	def setSuperpos(self, chess, nodeID):
		sup       = SuperPosition(chess.id, self.mgr)
		supID     = self.mgr.add(sup)
		chess.sid = supID

class QuantumChessBuilder(ChessmanBuilder):
	def buildChess(self, chess, pos):
		newChess = copy.copy(chess)
		newChess.move(pos)
		return newChess
		
	def setSuperpos(self, chess, nodeID):
		sup       = chess.getSuperposition()
		sup.create(chess.id, nodeID)

		
class NodeBuilder:
	def __init__(self, manager):
		self.mgr = manager
	def setProb(self, chess, newNode):
		pass
	def setRelation(self, chess, nodeID):
		pass
	def buildNode(self, chess, chessTo)
		newNode = Node(chessTo.id)
		nodeID  = self.mgr.add(newNode)
		return newNode, nodeID
	def getTopNode(self, chess):
		sup    = chess.getSuperposition(self.mgr)
		nodeID = sup.getNode(chess.id)[0]
		return self.mgr.get(nodeID)
	def build(self, chess, chessTo):
		newNode, nodeID = self.buildNode(chess, chessTo)
		self.setProb(chess, newNode)
		self.setRelation(chess, nodeID)
		return nodeID

class QuantumTopNodeBuilder(NodeBuilder):
	def setProb(self, chess, newNode):
		sourceNode          = self.getTopNode(chess)
		newNode.prob        = sourceNode.prob / 2
		newNode.showProb    = sourceNode.prob / 2
		sourceNode.showProb = sourceNode.prob / 2
		sourceNode.prob     = sourceNode.prob / 2
		
class QuantumSubNodeBuilder(NodeBuilder):
	def buildNode(self, chess, chessTo):
		newNode = Node(chessTo.id, parent=chess.id)
		nodeID  = manager.add(newNode)
		return newNode, nodeID
	def setProb(self, chess, newNode):
		sourceNode          = self.getTopNode(chess)
		newNode.prob        = sourceNode.showProb / 2
		newNode.showProb    = sourceNode.showProb / 2
		sourceNode.showProb = sourceNode.showProb / 2
	def setRelation(self, chess, nodeID):
		sourceNode          = self.getTopNode(chess)
		sourceNode.children.append(nodeID)
	
		
class ClassicalEntangleNodeBuilder(QuantumSubNodeBuilder):
	def __init__(self, chessList, manager):
		self.mgr       = manager
		self.chessList = chessList
		
	def buildNode(self, chess, chessTo, manager):
		newNode = ClassicalNode(chess.id, chessTo.id, path=self.chessList)
		nodeID  = self.mgr.add(newNode)
		return nodeID
		
class QuantumEntangleNodeBuilder(ClassicalEntangleNodeBuilder):
	def buildNode(self, chess, chessTo, manager):
		newNode = QuantumNode(chess.id, chessTo.id, path=self.chessList)
		nodeID  = self.mgr.add(newNode)
		return nodeID
		
class ChessFactory:
	def __init__(self, chessboard):
		self.board    = chessboard
		self.mgr      = chessboard.mgr
		
	def nodeBuilderSelect(self, str, chessList):
		if str == 'Node':
			return NodeBuilder(self.mgr)
		elif str == 'QuantumTopNode':
			return QuantumTopNodeBuilder(self.mgr)
		elif str == 'QuantumSubNode':
			return QuantumSubNodeBuilder(self.mgr)
		elif str == 'ClassicalEntangleNode':
			return ClassicalEntangleNodeBuilder(chessList, self.mgr)
		elif str == 'QuantumEntangleNode':
			return QuantumEntangleNodeBuilder(chessList, self.mgr)
		else:
			return None
	
	def getPath(self, chess, path):
		if path == []:
			return []
		source = path[0]
		target = path[1]
		posList = chess.Path(source, target)
		chessList = [ self.board.getChessman(pos) for pos in posList ]
		chessList = [ ch.id for ch in chessList if ch ]
		return chessList
	
	def nodeTypeSelect(chess, isQuantum, p1, p2):
		pathData = self.getPath(chess, p1) + self.getPath(chess, p2)
		
		if p1==[] and p2==[] and chess.isAbleToGenTopNode():
			return 'QuantumTopNode', pathData
		elif p1==[] and p2==[]:
			return 'QuantumSubNode', pathData
		elif not isQuantum:
			return 'ClassicalEntangleNode', pathData
		else:
			return 'QuantumEntangleNode', pathData
	
	def buildChess(self, chess, TargetPos, isQuantum, p1=[], p2=[]):
		chessBuilder       = QuantumChessBuilder(self.mgr)
		nodeType, pathData = self.nodeTypeSelect(chess, isQuantum, p1, p2)
		nodeBuilder        = self.nodeBuilderSelect(nodeType, pathData)
		newChess           = chessBuilder.build(chess, nodeBuilder, TargetPos)
		return newChess
		