#-*- encoding: utf-8 -*-

import sys, string, os
import pygame
from pygame.locals import *
#象棋游戏相关的全局定义变量

CHESSMAN_COLOR_RED    = 0   
CHESSMAN_COLOR_BLACK = 1

CHESSMAN_KIND_NONE   = -1  # 表示棋盘该位置没有棋子
CHESSMAN_KIND_JU       = 0
CHESSMAN_KIND_MA      = 1
CHESSMAN_KIND_XIANG  = 2
CHESSMAN_KIND_SHI      = 3
CHESSMAN_KIND_JIANG   = 4
CHESSMAN_KIND_PAO      = 5
CHESSMAN_KIND_BING     = 6     

# Easy to turn off message
def debugMsg(msg):
	print(msg)
	pass

def writeErrorLog(log):
	'''
	写错误日志
	'''
	file = open('error.log', 'a')
	file.write(log)
	file.close()

# 加载图片
def load_image(name, colorfilter=0xffffff):    
	try:
		image = pygame.image.load(name).convert_alpha()
		writeErrorLog('success to loadimage:'+ name)
	except pygame.error as message:
		print("Cannot load image:", name)
		writeErrorLog('Cannot load image:'+ name)
		print(message)
		raise(SystemExit, message)
		return None
	if colorfilter is not None:
		if colorfilter is -1:
			colorfilter = image.get_at((0,0))
		image.set_colorkey(colorfilter, RLEACCEL)
	return image, image.get_rect()
	

# 加载文字
def load_font(txt):
	# 创建一个字体对象，字体大小为20     
	font = pygame.font.SysFont('Arial', 20)
	# 生成文字
	text = font.render(txt, 1, (255, 0, 0))
	# 取得文字区域大小
	textpos = text.get_rect()
	
	return text, textpos

# Position wrapper
class Position:
	row = -1
	col = -1

	def __init__(self, row, col):
		self.row = row
		self.col = col
	def __eq__(self, other):
		if(isinstance(other, Position)):
			return self.equalTo(other)
		else:
			return False
	# Check if this position is in chinese chess board 
	def isInBoarder(self):
		if (self.row >= 0) and (self.row <= 9) and (self.col >= 0) and (self.col <= 8):
			return True
		return False

	# Converts position to string of the form "(x, y)"
	def str(self):
		r = "("
		return r + str(self.row) + ", " + str(self.col) + ")"

	# Converts to a two element list (row, col)
	def toList(self):
		return (self.row, self.col)

	def distance(self, other):
		return self.rowDist(other) + self.colDist(other)

	def rowDist(self, other):
		return abs(self.row - other.row)

	def colDist(self, other):
		return abs(self.col - other.col)

	def equalTo(self, other):
		return self.isSameRow(other) and self.isSameCol(other)

	def isSameRow(self, other):
		if other == None:
			return False
		return self.row == other.row

	def isSameCol(self, other):
		if other == None:
			return False
		return self.col == other.col

def posToLeftTop(pos):
	left = pos.col * 50 + 4
	top = pos.row * 50 + 15
	return (left, top)
