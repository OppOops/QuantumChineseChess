#-*- encoding: utf-8 -*-

import os
import copy
import random
from ChessGlobal import *

class Chessman:
	'''
	棋子基类
	数据成员：棋子类型（车，马。。），棋子颜色（黑，红）,棋子当前行列
	操作：1、仅靠位置判断是否能走棋,不考虑其它棋子的影响   
			2、获得棋子图片对象
	'''

	_ColorText = ('red ', 'black ')
	_ColorFileText = ('r', 'b')
	_KindText = None
	_board = None
	_pos = None
	_kind = None
	_superpositions = None
	_probability = 1.0
	entangleKey = None
	_removed    = False
	
	def getImage(self):
		'''
		根据棋子类型和棋子颜色获得棋子图片对象
		'''
		filename = './IMG/' + self._ColorFileText[self.color] + '_' + self.kindText() + '.png'
		writeErrorLog(filename)
		image = load_image(filename)
		if self.hasSuperpositions():
			alpha = 195+60*self._probability
			image[0].fill((200, 200, 200, alpha), None, pygame.BLEND_RGBA_MULT)
		return (image[0], image[1])
	
	def __init__(self, cboard, color, row, col):
		self._board = cboard.condition
		self.color = color
		self._pos = Position(row, col)
		self._superpositions = [self]
	
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
		#若有自己的分身(superposition, entanglement)存在，也無法移動
		#若回傳值為成功的話，應該將所有路徑上的棋全部measure一次
		chessList = self.chessBetweenPath(source, target)
		for chess in chessList:
			if chess.hasSuperpositions() == False:
				return False
		return True
	
	# Move piece classically, no checking.
	def move(self, pos):
		self._pos = pos
		return

	# Move piece classically, no checking.
	def getPos(self):
		return self._pos
		
	def crossRiverLimit(self):
		if(self._kind == CHESSMAN_KIND_BING):
			return self._riverCrossed == False
		return False
		
	# Create a new superpostiion by copying itself and setting the list
	def createSuperposition(self, posTo):
		lsp = self._superpositions
		new = copy.copy(self)
		lsp.append(new)
		new.move(posTo)
		new.entangleKey = None
		new._probability = self._probability = self._probability / 2
		new._superpositions = lsp
		return new

	# Check if this piece has other superposition
	def hasSuperpositions(self):
		return len(self._superpositions) > 1

	# Get the list of all possible superpositions
	def getSupLocationList(self):
		lpos = []
		for sp in self._superpositions:
			lpos.append(sp._pos)
		return lpos
		
	def _assignRemoved(self, notExist):
		for ch in notExist:
			ch._removed = True
			
	# Measure and clear the remaining superpositions
	# Reture the measured position
	def distributeProb(self, notExist, observed):
		self._assignRemoved(notExist)
		if(len(self._superpositions) - len(notExist)==1):
			observed._probability  = 1.0
			observed._superpositions  = [observed]
			return [observed], notExist
		lsp        = self._superpositions
		prob       = sum([e._probability for e in notExist])
		other_prob = 1 - prob
		for sp in lsp:
			sp._probability += sp._probability * prob / other_prob
		for e in notExist:
			lsp.remove(e)
		return lsp, notExist
		
	def binomialCoin(self):
		frac   = 0.0
		r      = random.random()
		for sp in self._superpositions:
			frac += sp._probability
			if r <= frac:
				observed = sp
				break
		return observed
	
	def measure(self, other=[]):
		if	self._removed:
			return [], []
		elif self.hasSuperpositions() == False:
			return [self], []
		observed    = self.binomialCoin()
		eventPos    = [self._pos] + [ch._pos for ch in other]

		if (observed._pos not in eventPos):
			return self.distributeProb([self] + other, observed)
		else:
			removedSet = set(observed._superpositions) - set([self]+other)
			return self.distributeProb(list(removedSet), observed)
						
	def kindText(self):
		'''
		Get text mapping for both filename and log
		'''
		kind = self._KindText
		return kind
		
	def getInfo(self):
		info = self._ColorText[self.color] + self.kindText() + ", superposition: "
		for c in self._superpositions:
			info += c._pos.str() + "*" + str(c._probability) + " "
		return info
	
	def printInfo(self):
		info = self.getInfo()
		return info
		
	def isSameColor(self, other):
		return other != None and self.color == other.color

	# The region of palace
	def _isInsidePalace(self, posTo):
		if posTo.col < 3 or posTo.col > 5:
			return 0
		if self._pos.row < 3 and posTo.row >= 3:
			return 0
		if self._pos.row > 6 and posTo.row <= 6:
			return 0
		return 1
		

class ChessObserver:
	def __init__(self, chessboard):
		self.board      = chessboard
		self.resultMap  = dict()
		self.determined = dict()
		
	def _reorder(self, clist):
		#同樣順序下，先觀測有Entangle關係的棋子
		hasEntangle = [ch for ch in clist if ch.entangleKey!=None]
		noEntangle  = [ch for ch in clist if ch.entangleKey==None]
		return hasEntangle + noEntangle
	
	def remove(self, notExist, assignGroup=[]):
		if(notExist._removed):
			return
		sup    = notExist._superpositions
		print(notExist._pos.toList())
		other  = [ch for ch in sup if ch!=notExist]
		result = notExist.distributeProb([notExist], other[0])
		self.append(*result)
	
	def append(self, observedList, removedList):
		for ch in observedList:
			self.resultMap[ch._pos.toList()] = ch
			self.determined[ch]              = True
		for ch in removedList:
			self.resultMap[ch._pos.toList()] = None
			self.determined[ch]              = False
	
	def combine(self, other):
		removedList  = [ key for key, val in other.determined.items() if not val ]
		observedList = [ key for key, val in other.determined.items() if val ]
		self.append(observedList, removedList)
	
	def getResult(self):
		resultMap = self.resultMap
		return [ (Position(*key), val) for key, val in resultMap.items()]
	
	def getDetermined(self):
		return [ (key, val) for key, val in self.determined.items() ]
	
	def observeEntangle(self, chess, egraph):
		egraph.trySolve(chess, self)
	
	def observeSimple(self, chess, other=[]):
		result = chess.measure(other)
		self.append(*result)
		
	def observe(self, measureList, egraph):
		measureList = self._reorder(measureList)
		for chess in measureList:
			if chess._removed==True:
				continue
			elif chess.entangleKey == None:
				self.observeSimple(chess)
			else:
				self.observeEntangle(chess, egraph)
				self.observeSimple(chess)
		egraph.checkDependency(self)

class ChessmanShi(Chessman):
	_kind = CHESSMAN_KIND_SHI
	_KindText = "shi"
	def Path(self, pos, posTo):
		return []
		
	def ChessMoveJudge(self, posTo):
		if self._pos.rowDist(posTo) != 1 or self._pos.colDist(posTo) != 1:
			return 0
		if not self._isInsidePalace(posTo):
			return 0
		return 1


class ChessmanXiang(Chessman):
	_kind = CHESSMAN_KIND_XIANG
	_KindText = "xiang"
	def Path(self, pos, posTo):
		x = (self._pos.row + posTo.row) //2
		y = (self._pos.col + posTo.col) //2
		return [Position(x, y)]
		
	def ChessMoveJudge(self, posTo):
		if self._pos.rowDist(posTo) != 2 or self._pos.colDist(posTo) != 2:
			return 0
		if 4 == self._pos.row  and posTo.row > 4:
			return 0
		if 5 == self._pos.row and posTo.row < 5:
			return 0
		#夹心象判断
		return self.isPathClear(self._pos, posTo)


class ChessmanMa(Chessman):
	_kind = CHESSMAN_KIND_MA
	_KindText = "ma"
	def Path(self, pos, posTo):
		if self._pos.rowDist(posTo) == 1:
			x = self._pos.row
			y = (self._pos.col + posTo.col) // 2
		elif self._pos.colDist(posTo) == 1:
			y = self._pos.col
			x = (self._pos.row + posTo.row) // 2
		return [Position(x, y)]
		
	def isPathClear(self, source, target):
		chessList = self.chessBetweenPath(source, target)
		for chess in chessList:
			if chess.hasSuperpositions() == False:
				return False
		return True
		
	def ChessMoveJudge(self, posTo):
		if not (self._pos.rowDist(posTo) > 0 and self._pos.colDist(posTo) > 0 and
			self._pos.distance(posTo) == 3):
			return 0
		#别脚马判断
		return self.isPathClear(self._pos, posTo)


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
		source = self._pos
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
		realChess     = [1 for c in chessList if not(c.hasSuperpositions())]
		possibleChess = [1 for c in chessList if (c.hasSuperpositions())   ]
		return sum(realChess) < 2 and sum(realChess) + sum(possibleChess) > 0
		
	def isJumpable(self, source, target):
		chessList = self.chessBetweenPath(source, target)
		realSelf  = self._board._getChessman(source)
		chessList = [ch for ch in chessList if not realSelf in ch._superpositions ]
		return self.isPossibleOneReal(chessList)
		
	def ChessMoveJudge(self, target):
		source = self._pos
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
		if self._pos.distance(posTo) != 1:
			return 0
		# cannot move backward
		r1, r2 = self._pos.row, posTo.row
		if CHESSMAN_COLOR_BLACK == self.color:
			r2, r1 = r1, r2
		if r1 > r2:
			return 0
		if 0 == self._riverCrossed and (not self._pos.isSameCol(posTo)):
			return 0
		return 1

	def move(self, pos):
		# 兵：过河
		if (4 == self._pos.row and 5 == pos.row) or (5 == self._pos.row and 4 == pos.row):
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
		source = self._pos
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
		if (self._pos.isSameCol(target)) and (CHESSMAN_KIND_JIANG == chessmanTo._kind) and (0 == countBetween):
			return 1
		return 0