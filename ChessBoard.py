#-*- encoding: utf-8 -*-
import sys, string, os
import pygame
import copy
from types import *
from pygame.locals import *
from ChessGlobal import *
from Chessman import *
from ChessFactory import *
from ObjectManager import *

class ChessBoard:
	
	curStepColor = CHESSMAN_COLOR_RED
	tipInfo = ''
	condition = None
	showProb = False
	
	def __init__(self, ground_image, circleImg):
		self.ground    = ground_image
		self.circle    = circleImg
		self.condition = ChessBoardCondition(self)
		self.resetBorad()
	
	def resetBorad(self):
		self.mgr          = ObjectManager()
		self._board       = ChessBoardStart.initBoard(self)
		self.curStepColor = ChessBoardStart.initColor()
		cb = ClassicalChessBuilder(self.mgr)
		nb = NodeBuilder(self.mgr)
		for pos, chess in self._board.items():
			self._board[pos] = cb.build(chess, nb).id
		
	
	def __redrawBorad(self, window):
		window.fill((0,0,0))
		window.blit(self.ground, (0, 0))
		self.window = window
		#顯示所有棋子
		font = pygame.font.SysFont('Arial', 24)
		for key in self._board.keys():
			chessman = self._getChess(Position(*key))
			if chessman == None:
				continue
			leftTop = posToLeftTop(Position(key[0], key[1]))
			image, rc = chessman.getImage(self.mgr)
			window.blit(image, leftTop)
			if chessman.color == self.curStepColor:
				window.blit(self.circle, leftTop)
		#顯示所有棋子機率
			prob = chessman.getProbability(self.mgr)
			if self.showProb and prob != 1.0:
				probString = '{:d}'.format(int(round(prob * 100))) + '%'
				text = font.render(probString, 1, (0, 0, 255))
				window.blit(text, leftTop)
		
	def __showTipInfo(self, window):
		lines = self.tipInfo.split('\n')
		count = 0
		for ln in lines:
			text, textpos = load_font(ln)
			textpos = Rect(0,532+count*20, 460, 28)
			window.blit(text, textpos)
			count += 1
	
	def draw(self, window):
		self.__redrawBorad(window)
		self.__showTipInfo(window)
		
	def setTip(self, tipText):
		self.tipInfo = tipText
	
	def updateChessBoard(self, resultList): #should modify chess object before assign
		for resPos, ref in resultList:
			self._board[resPos.toList()] = ref
			
	# Classical move: move the piece (without checking capture)
	def sendChessMove(self, pos, posTo):
		self.__changeColor()
		chessman = self._getChess(pos)
		if self.condition.entangleCondition(pos, posTo):
			p1 = [pos, posTo]
			self.EntangleGen(chessman, posTo, False, p1)
			return
		
		measureList = self._getChessmanList( [pos] + chessman.Path(pos, posTo) + [posTo] )
		measureList = self.condition.filterbySameSup(measureList, chessman)
		measureList = [chessman] + measureList
		if len(measureList) > 1 or self._getChess(posTo):
			resultList  = self.measure(measureList)
			self.updateChessBoard(resultList)
		
		##Rejudge()	
		chessman = self._getChess(pos)
		chessmanTo = self._getChess(posTo)
		if(chessman == None):
			return
		if(chessman.ChessMoveJudge(posTo)):
			self._board[posTo.toList()] = chessman.id
			chessman.move(posTo)
			self._board[pos.toList()]  = None
		if isinstance(chessmanTo, ChessmanJiang):
			self.endChessBoard(self.curStepColor)
					
	def sendChessMoveQuantum(self, pos, mpos, posTo):
		#這個步驟不會造成任何棋子被觀察，只有entangle狀況要處理
		self.__changeColor()
		chessman   = self._getChess(pos)
		Econd      = self.condition.QuantumEntangleCondition
		if Econd(pos, mpos, chessman) and Econd(mpos, posTo, chessman):
			p1 = [pos, mpos]
			p2 = [mpos, posTo]
			self.EntangleGen(chessman, posTo, True, p1, p2)
		elif Econd(pos, mpos, chessman):
			self.EntangleGen(chessman, posTo, True, p1=[pos, mpos])
		elif Econd(mpos, posTo, chessman):
			self.EntangleGen(chessman, posTo, True, p1=[mpos, posTo])
		else:
			self.QuantumChessGen(chessman, posTo)
		
	def __changeColor(self):
		#换方下棋
		if self.curStepColor == CHESSMAN_COLOR_BLACK:
			self.curStepColor = CHESSMAN_COLOR_RED
		else:
			self.curStepColor = CHESSMAN_COLOR_BLACK
	
	def endChessBoard(self, captureColor):
		tipText = ''
		if CHESSMAN_COLOR_BLACK == captureColor:
			tipText += "\ngame over,red win!"
		else :
			tipText += "\ngame over,black win!"
		self.resetBorad()
		self.setTip(tipText)
	
	def getChessman(self, pos): #public API
		return copy.copy(self._getChess(pos))
	
	def _getChess(self, pos): #private API
		id = self._board.get(pos.toList(), -1)	
		return self.mgr.get(id)

	def _getChessmanList(self, posList):
		chessList = [ self._getChess(pos) for pos in posList]
		return [ ch for ch in chessList if ch!=None]
		
	def measure(self, measureList):
		observer = ChessObserver()
		for ch in measureList:
			ch.measure(observer, self.mgr)
		self.checkDependency(observer)
		return observer.getResult()
	
	def checkDependency(self, observer):
		allChess = [ self.mgr.get(id) for id in self._board.values() if id]
		allChess = [ ch for ch in allChess if ch._removed==False ]
		allSup   = list(set([self.mgr.get(ch.sid) for ch in allChess]))
		for sup in allSup:
			sup.checkDependency(observer, self.mgr)
	
	def EntangleGen(self, chess, TargetPos, isQuantum, p1=[], p2=[]):
		observer = ChessObserver()
		factory  = ChessFactory(self)
		newChess = factory.buildChess(chess, TargetPos, isQuantum, p1, p2)
		
		observer.append([newChess], [])
		self.updateChessBoard(observer.getResult())
		
	def QuantumChessGen(self, chess, TargetPos):
		observer = ChessObserver()
		factory  = ChessFactory(self)
		newChess = factory.buildChess(chess, TargetPos, True)
		
		observer.append([newChess], [])
		self.updateChessBoard(observer.getResult())
	
class ChessBoardCondition: #判斷盤面情況，不會修改到盤面
	def __init__(self, chessboard):
		self.__board = chessboard
	
	def getManager(self):
		return self.__board.mgr
	
	def getChessman(self, pos):
		return self.__board.getChessman(pos)
			
	def filterbySameSup(self, clist, ptr):
		sup = ptr.sid
		return [ch for ch in clist if ch.sid!=sup and ch.id!=ptr.id] 
	
	def copyBoard(self):
		newBoard   = copy.copy(self.__board._board)
		newManager = copy.copy(self.__board.mgr)
		moveColor = self.__board.curStepColor
		newManager.list = dict()
		for key,val in self.__board.mgr.list.items():
			if isinstance(val, Chessman):
				newVal = copy.copy(val)
				newVal._board = self
			else:
				newVal = copy.deepcopy(val)
			newManager.list[key] = newVal
		return {'board':newBoard,
			    'color':moveColor,
				'manager':newManager}
	
	def moveChessColorJudge(self, pos):
		chessman = self.__board.getChessman(pos)
		if chessman == None:
			return 1
		elif chessman.color != self.__board.curStepColor:
			return  0
		else:
			return 1
			
	def chessBetweenPath(self, vlist):
		chessInPath = [self.getChessman(pos) for pos in vlist]
		return [chess for chess in chessInPath if chess]
		
	def entangleCondition(self, pos, posTo):
		mgr			= self.__board.mgr
		chessmanTo  = self.getChessman(posTo)
		chessman    = self.getChessman(pos)
		if(chessmanTo != None): #Should Be measured, since capture operation is performed
			return False
		elif not chessman.hasSuperpositions(mgr): #entangle must have superposition
			return False
		clist = chessman.chessBetweenPath(pos, posTo)
		clist = self.filterbySameSup(clist, chessman)
		if clist == []:
			return False
		for c in clist:
			if not c.hasSuperpositions(mgr):
				return False
		return True
		
	def QuantumEntangleCondition(self, pos, posTo, chessman):
		mgr	  = self.__board.mgr
		clist = chessman.chessBetweenPath(pos, posTo)
		clist = self.filterbySameSup(clist, chessman)
		if clist == []:
			return False
		for c in clist:
			if not c.hasSuperpositions(mgr):
				return False
		return True