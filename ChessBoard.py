#-*- encoding: utf-8 -*-

import sys, string, os
import pygame
import datetime
import copy
import random
from types import *
from pygame.locals import *
from ChessGlobal import *
from Chessman import *
from NetworkChs import *
from GraphSearch import *

import socket

class ChessBoard:
	
	# _movesteps = MOVE_CLASSICAL
	#当前要走棋的棋子颜色，初始化为红色
	curStepColor = CHESSMAN_COLOR_RED
	#下棋源   0--鼠标点击，1--网络信息
	moveFrom = 0
	_board = dict()
	tipInfo = ''
	condition = None
	showProb = False
	
	def __init__(self, ground_image, circleImg):
		random.seed()
		self.ground    = ground_image
		self.circle    = circleImg
		self.condition = ChessBoardCondition(self)
		self.resetBorad()
		self.egraph    = Graph()
			
	def resetBorad(self):
		self.curStepColor = CHESSMAN_COLOR_RED
		self._board = {
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
	
	def __redrawBorad(self, window):
		
		window.fill((0,0,0))
		window.blit(self.ground, (0, 0))
		self.window = window
		#顯示所有棋子
		font = pygame.font.SysFont('Arial', 24)
		for key in self._board.keys():
			chessman = self._board[key]
			if chessman == None:
				continue;
			leftTop = posToLeftTop(Position(key[0], key[1]))
			image, rc = chessman.getImage()
			window.blit(image, leftTop)
			if chessman.color == self.curStepColor:
				window.blit(self.circle, leftTop)
		#顯示所有棋子機率
			if self.showProb and chessman._probability != 1.0:
				probString = '{:d}'.format(int(round(chessman._probability * 100))) + '%'
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
		# 當這個步驟是符合規則的時候:
		# 吃子 / 移動:
			# 1. Path上所有棋子都要被觀測
			# 2. 起點/終點如果有superPosition要被觀測
			# 3. 以上瞬間發生
			# 觀測結束後，重新判斷是否有成功
		# 重新判斷:
			# 起點是否存在, 終點是否到達?
		self.__changeColor()
		chessman = self._getChess(pos)
		if self.condition.entangleCondition(pos, posTo):
			self.EntangelGen(pos, posTo)
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
			self._board[posTo.toList()] = chessman
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
			self.EntangelGen(pos, posTo, midPos=mpos)
			return
		elif Econd(pos, mpos, chessman):
			self.EntangelGen(pos, mpos, endPos=posTo)
			return
		elif Econd(mpos, posTo, chessman):
			self.EntangelGen(mpos, posTo, sPos=pos)
			return
			
		c2 = chessman.createSuperposition(posTo)
		self._board[posTo.toList()] = c2
		
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
		return self._board.get(pos.toList(), None)

	def _getChessmanList(self, posList):
		chessList = [ self._getChess(pos) for pos in posList]
		return [ ch for ch in chessList if ch!=None]
		
	def measure(self, measureList):
		observer = ChessObserver(self)
		observer.observe(measureList, self.egraph)
		return observer.getResult()
			
	def EntangelGen(self, pos, posTo, midPos=None, endPos=None, sPos=None):
		if endPos == None:
			target = posTo
		else:
			target = endPos
		if sPos == None:
			source = pos
		else:
			source = sPos
			
		chessman   = self._getChess(source)
		c2         = chessman.createSuperposition(target)
		self._board[target.toList()] = c2
		if midPos!=None:
			clist		 = [self._getChess(pos)]
			clist 		+= chessman.chessBetweenPath(pos, midPos)
			clist 		+= chessman.chessBetweenPath(midPos, posTo)
			clist		+= [self._getChess(target)]
			self.egraph.buildVertex(clist, self, isQuantumMove=True)
		else:
			clist		 = [self._getChess(source)]
			clist       += chessman.chessBetweenPath(pos, posTo)
			clist		+= [self._getChess(target)]
			if endPos != None or sPos!= None:
				self.egraph.buildVertex(clist, self, isQuantumMove=True)
			else:
				self.egraph.buildVertex(clist, self, isQuantumMove=False)

class ChessBoardCondition: #判斷盤面情況，不會修改到盤面
	def __init__(self, chessboard):
		self.__board = chessboard
	
	def getChessman(self, pos):
		return self.__board.getChessman(pos)
	def _getChessman(self, pos):
		chess = self.__board._getChess(pos)
		if chess != None and chess._removed==False:
			return chess
		else:
			return None
			
	def filterbySameSup(self, clist, ptr):
		sup = ptr._superpositions
		return [ch for ch in clist if ch._superpositions!=sup and ch!=ptr] 
	
	def copyBoard(self):
		newBoard  = copy.deepcopy(self.__board._board)
		moveColor = self.__board.curStepColor
		posList   = [Position(i%10, i//10) for i in range(0,90) ]
		chessList = [self._getChessman(pos) for pos in posList  ]
		chessList = [chess for chess in chessList if chess!=None]
		for c in chessList:
			if c.hasSuperpositions():
				posList      = c.getSupLocationList()
				newchessList = [newBoard[pos.toList()] for pos in posList]
				for n in newchessList:
					n._superpositions = newchessList
		newGraph = copy.deepcopy(self.__board.egraph)
		newGraph.copy(newBoard)
		return {'board':newBoard, 'color':moveColor, 'graph':newGraph}
	
	def moveChessColorJudge(self, pos):
		'''
		判断当前选中棋子是否和允许下的棋子颜色相同，不同不允许走棋
		'''
		chessman = self.__board.getChessman(pos)
		if chessman == None:
			return 1
		elif chessman.color != self.__board.curStepColor:
			return  0
		else:
			return 1
			
	def chessBetweenPath(self, vlist):
		chessInPath = [self._getChessman(pos) for pos in vlist]
		return [chess for chess in chessInPath if chess]
		
	def entangleCondition(self, pos, posTo):
		chessmanTo  = self._getChessman(posTo)
		chessman    = self._getChessman(pos)
		if(chessmanTo != None): #Should Be measured, since capture operation is performed
			return False
		elif not chessman.hasSuperpositions(): #entangle must have superposition
			return False
		clist = chessman.chessBetweenPath(pos, posTo)
		clist = self.filterbySameSup(clist, chessman)
		if clist == []:
			return False
		for c in clist:
			if not c.hasSuperpositions():
				return False
		return True
		
	def QuantumEntangleCondition(self, pos, posTo, chessman):
		tmpChess      = copy.copy(chessman)
		tmpChess._pos = pos
		clist = tmpChess.chessBetweenPath(pos, posTo)
		clist = self.filterbySameSup(clist, chessman)
		if clist == []:
			return False
		for c in clist:
			if not c.hasSuperpositions():
				return False
		return True