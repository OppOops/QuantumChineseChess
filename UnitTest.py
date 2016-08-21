#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
from ChessGlobal import *
from ChessBoard import *
from BoardStage import *

# 紅: (0,0)俥傌相士帥士相傌俥(0,8)

# 紅: (2,1)  砲          砲  (2,7)

# 紅: (3,0)兵  兵  兵  兵  兵(3,8)

# ================================

# 黑: (6,0)兵  兵  兵  兵  兵(6,8)

# 黑: (7,1)  炮          炮  (7,7)

# 黑: (9,0)車馬象士將士象馬車(9,8)

class NewStage():
	def __init__(self):
		self.chessboard = ChessBoard(None)
		self.controller = StageController(self.chessboard, None)
	def reset(self):
		self.chessboard.resetBorad()
	def click(self, coord):
		self.controller.boardStage.actChess(coord, self.controller)
	def getChess(self, coord):
		chess = self.chessboard.getChessman(coord)
		return chess
		
class TestClassLogic(unittest.TestCase):
	def testInterface(self):
		obj = BoardStageInterface(None, None, None)
		self.assertTrue(isinstance(obj, BoardStageInterface), '測試')
		
class TestChessBoard(unittest.TestCase):
	def testfirstTest(self):
		self.assertTrue(True, '必定會過!')
		
	def testPaoEat(self):
		board = NewStage()
		board.click(Position(2,7))
		board.click(Position(2,7))
		board.click(Position(1,7))
		board.click(Position(1,4))
		board.click(Position(6,4))
		board.click(Position(5,4))
		board.click(Position(2,7))
		board.click(Position(2,7))
		board.click(Position(2,6))
		board.click(Position(2,4))
		ch = board.getChess(Position(1,4)).isJumpable(Position(1,4),Position(6,4))
		print(ch)
		self.assertTrue(1+1==2, '測試')
	def testPosition(self):
		board = NewStage()
		print(board.chessboard._board)
		print('')
		print(copy.deepcopy(board.chessboard._board))
		

if __name__ == '__main__':
	pygame.init()
	unittest.main()