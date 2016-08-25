#-*- encoding: utf-8 -*-

import os
from ChessGlobal import *

class Chessman:

	_ColorText = ('red ', 'black ')
	_ColorFileText = ('r', 'b')
	_KindText = None
	_board = None
	_pos = None
	_kind = None
	_removed    = False
	
	def getImage(self, manager):
		'''
		根据棋子类型和棋子颜色获得棋子图片对象
		'''
		filename = './IMG/' + self._ColorFileText[self.color] + '_' + self.kindText() + '.png'
		writeErrorLog(filename)
		image = load_image(filename)
		if self.hasSuperpositions(manager):
			alpha = 195+60*self.getProbability(manager)
			image[0].fill((200, 200, 200, alpha), None, pygame.BLEND_RGBA_MULT)
		return (image[0], image[1])
	
	def __init__(self, cboard, color, row, col, id=-1, sid=-1):
		self._board = cboard.condition
		self.color  = color
		self._pos   = (row, col)
		self.id     = id
		self.sid    = sid
	
	def Path(self, pos, posTo):
		#回傳移動路徑上，不包含起點和終點的所有位置
		raise NotImplementedError("Please Implement this method")
	
	def ChessMoveJudge(self, rowTo, colTo):
		raise NotImplementedError("Please Implement this method")
		
	def chessBetweenPath(self, source, target):
		if source!=None and target!=None:
			return self._board.chessBetweenPath(self.Path(source, target))
		else:
			return None
			
	def isPathClear(self, source, target):
		#判斷移動路徑上的障礙，如果有非superPosition的棋，則無法移動
		#若有自己的分身(superposition, entanglement)存在，則略過不計
		manager   = self._board.getManager()
		chessList = self.chessBetweenPath(source, target)
		for chess in chessList:
			if chess.hasSuperpositions(manager) == False:
				return False
		return True
		
	def isSameColor(self, other):
		return other != None and self.color == other.color

	# The region of palace
	def _isInsidePalace(self, posTo):
		if posTo.col < 3 or posTo.col > 5:
			return 0
		if self.getPos().row < 3 and posTo.row >= 3:
			return 0
		if self.getPos().row > 6 and posTo.row <= 6:
			return 0
		return 1
		
	def crossRiverLimit(self):
		if(self._kind == CHESSMAN_KIND_BING):
			return self._riverCrossed == False
		return False	
	
	def measure(self, observer, manager):
		sup    = self.getSuperposition(manager)
		sup.measure(self.id, observer, manager)
		
	# Move piece classically, no checking.
	def move(self, pos):
		self._pos = pos.toList()
		return

	# Move piece classically, no checking.
	def getPos(self):
		return Position(*self._pos)
	
	def getProbability(self, manager):
		sup = manager.get(self.sid)
		return sup.getProb(self.id, manager)
		
	def getSuperposition(self, manager):
		return manager.get(self.sid)
		
	# Check if this piece has other superposition
	def hasSuperpositions(self, manager):
		sup = manager.get(self.sid)
		return len(sup.nodeList) > 1

	# Get the list of all possible superpositions
	def getSupLocationList(self, manager):
		lpos = []
		sup = manager.get(self.sid)
		for chessID in sup.nodeList.keys():
			chess = manager.get(chessID)
			lpos.append(chess.getPos())
		return lpos
	
	def isAbleToGenTopNode(self, manager):
		sup    = self.getSuperposition(manager)
		nodeID = sup.nodeList[self.id]
		node   = manager.get(nodeID)
		return len(node.children) == 0 and node.parent == None
	
	def isDetermined(self, manager):
		if(self._removed):
			return False
		sup  = self.getSuperposition(manager)
		nodeID = sup.nodeList[self.id]
		node   = manager.get(nodeID)
		return node.prob == 1.0
	
	def kindText(self):
		kind = self._KindText
		return kind
		
	def printInfo(self):
		info = self._ColorText[self.color] + self.kindText()
		return info
		
class ChessObserver:
	def __init__(self):
		self.resultMap  = dict()
		self.determined = dict()
	
	def append(self, observedList, removedList):
		for ch in observedList:
			self.resultMap[ch.getPos().toList()] = ch.id
			self.determined[ch.id]              = True
		for ch in removedList:
			self.resultMap[ch.getPos().toList()] = None
			self.determined[ch.id]               = False
	
	def moveChess(self, chess, pos, posTo, isDetermined=False):
		chess.move(posTo)
		self.resultMap[pos.toList()]   = None
		self.resultMap[posTo.toList()] = chess.id
		if isDetermined:
			self.determined[chess.id] = True
	
	def combine(self, other):
		removedList  = [ key for key, val in other.determined.items() if not val ]
		observedList = [ key for key, val in other.determined.items() if val ]
		self.append(observedList, removedList)
	
	def getResult(self):
		resultMap = self.resultMap
		return [ (Position(*key), val) for key, val in resultMap.items()]
	
	def getDetermined(self):
		return [ (key, val) for key, val in self.determined.items() ]
	

class ChessmanShi(Chessman):
	_kind = CHESSMAN_KIND_SHI
	_KindText = "shi"
	def Path(self, pos, posTo):
		return []
		
	def ChessMoveJudge(self, posTo):
		if self.getPos().rowDist(posTo) != 1 or self.getPos().colDist(posTo) != 1:
			return 0
		if not self._isInsidePalace(posTo):
			return 0
		return 1


class ChessmanXiang(Chessman):
	_kind = CHESSMAN_KIND_XIANG
	_KindText = "xiang"
	def Path(self, pos, posTo):
		x = (self.getPos().row + posTo.row) //2
		y = (self.getPos().col + posTo.col) //2
		return [Position(x, y)]
		
	def ChessMoveJudge(self, posTo):
		if self.getPos().rowDist(posTo) != 2 or self.getPos().colDist(posTo) != 2:
			return 0
		if 4 == self.getPos().row  and posTo.row > 4:
			return 0
		if 5 == self.getPos().row and posTo.row < 5:
			return 0
		#夹心象判断
		return self.isPathClear(self.getPos(), posTo)


class ChessmanMa(Chessman):
	_kind = CHESSMAN_KIND_MA
	_KindText = "ma"
	def Path(self, pos, posTo):
		if self.getPos().rowDist(posTo) == 1:
			x = self.getPos().row
			y = (self.getPos().col + posTo.col) // 2
			return [Position(x, y)]
		elif self.getPos().colDist(posTo) == 1:
			y = self.getPos().col
			x = (self.getPos().row + posTo.row) // 2
			return [Position(x, y)]
		else:
			return []
		
	def ChessMoveJudge(self, posTo):
		if not (self.getPos().rowDist(posTo) > 0 and self.getPos().colDist(posTo) > 0 and
			self.getPos().distance(posTo) == 3):
			return 0
		#别脚马判断
		return self.isPathClear(self.getPos(), posTo)


class ChessmanJu(Chessman):
	_kind = CHESSMAN_KIND_JU
	_KindText = "ju"
	def isSameLine(self, s, t):
		return (s.row == t.row) or (s.col == t.col)
		
	def _betweenCol(self, col, r1, r2): #modified
		if r2 < r1:
			r2, r1 = r1, r2
		Location   = lambda k : Position(k, col)
		return [ Location(i) for i in range(r1+1, r2)]

	def _betweenRow(self, row, c1, c2): #modified
		if c2 < c1:
			c2, c1 = c1, c2
		Location   = lambda k : Position(row, k)
		return [ Location(i) for i in range(c1+1, c2)]
		
	def Path(self, pos, posTo):
		if pos.col == posTo.col:
			return self._betweenCol(pos.col, pos.row, posTo.row)
		if pos.row == posTo.row:
			return self._betweenRow(pos.row, pos.col, posTo.col)
		return []
			
	def isTargetClear(self, target):
		chessmanTo   = self._board.getChessman(target)
		return (chessmanTo==None) or (self.color != chessmanTo.color)
		
	def ChessMoveJudge(self, target):
		source = self.getPos()
		if (source == target) or not(self.isSameLine(source, target)):
			return 0
		#车拦路判断
		chessBetween = self.chessBetweenPath(source, target)
		countBetween = len(chessBetween)
		if countBetween == 0 and self.isTargetClear(target):
			return 1
		elif self.isPathClear(source, target) and self.isTargetClear(target):
			return 1
		else:
			return 0


class ChessmanPao(ChessmanJu): #modified
	_kind = CHESSMAN_KIND_PAO
	_KindText = "pao"
	def isPossibleOneReal(self, chessList):
		mgr = self._board.getManager()
		realChess     = [1 for c in chessList if not(c.hasSuperpositions(mgr))]
		possibleChess = [1 for c in chessList if (c.hasSuperpositions(mgr))   ]
		return sum(realChess) < 2 and sum(realChess) + sum(possibleChess) > 0
		
	def isJumpable(self, source, target):
		chessList = self.chessBetweenPath(source, target)
		chessList = [ch for ch in chessList if ch.sid != self.sid ]
		return self.isPossibleOneReal(chessList)
		
	def ChessMoveJudge(self, target):
		source = self.getPos()
		if (source == target) or not(self.isSameLine(source, target)):
			return 0
		#隔山炮判断
		chessmanTo   = self._board.getChessman(target)
		chessBetween = self.chessBetweenPath(source, target)
		countBetween = len(chessBetween)
		if (countBetween == 0) and (chessmanTo == None):
			return 1
		elif (chessmanTo == None) and (self.isPathClear(source, target)):
			return 1
		elif (None != chessmanTo) and (self.color != chessmanTo.color):
			if self.isJumpable(source, target):
				return 1
			else:
				return 0
		else:
			return 0



class ChessmanBing(Chessman):
	_kind = CHESSMAN_KIND_BING
	_KindText = "bing"
	#过河判断，用于兵
	_riverCrossed = False
	def Path(self, pos, posTo):
		return []
		
	def ChessMoveJudge(self, posTo):
		if self.getPos().distance(posTo) != 1:
			return 0
		# cannot move backward
		r1, r2 = self.getPos().row, posTo.row
		if CHESSMAN_COLOR_BLACK == self.color:
			r2, r1 = r1, r2
		if r1 > r2:
			return 0
		if 0 == self._riverCrossed and (not self.getPos().isSameCol(posTo)):
			return 0
		return 1

	def move(self, pos):
		# 兵：过河
		if (4 == self.getPos().row and 5 == pos.row) or (5 == self.getPos().row and 4 == pos.row):
			self._riverCrossed = 1
		Chessman.move(self, pos)
		return
		
# Jiang:
# Normal move: 1 grid in 3x3 palace
# Capturing: get another Jiang in a straight line (col)
class ChessmanJiang(ChessmanJu):
	_kind = CHESSMAN_KIND_JIANG
	_KindText = "jiang"
		
	def ChessMoveJudge(self, target):
		source = self.getPos()
		isSuc = 1
		if source.distance(target) != 1:
			isSuc = 0
		if not self._isInsidePalace(target):
			isSuc = 0
		if 1 == isSuc:
			return 1
		#将判断
		chessmanTo = self._board.getChessman(target)
		chessBetween = self.chessBetweenPath(source, target)
		countBetween = len(chessBetween)
		if None == chessmanTo:
			return 0
		if (self.getPos().isSameCol(target)) and (CHESSMAN_KIND_JIANG == chessmanTo._kind) and (0 == countBetween):
			return 1
		return 0