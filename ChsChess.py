#-*- encoding: utf-8 -*-
import sys, string, os
import pygame
import time
from pygame.locals import *
from ChessGlobal import *
from ChessBoard import *
from TitleMenu import *
from BoardStage import *
from NetworkChs import *
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,100)

#初始化
pygame.init()
# 设置窗口大小 图片大小是460*532 ，
window = pygame.display.set_mode((460, 590)) 
# 设置窗口标题
pygame.display.set_caption('Quantum Chinese Chess')


ground_img, rc = load_image("./IMG/ground.png")
circle_img, rc = load_image("./IMG/TurnIndicator.png", 0xffffff)
curPos, rc = load_image("./IMG/curPos.png", 0xffffff)
chessbord = ChessBoard(ground_img, circle_img)
controller = StageController(chessbord, curPos)
title = TitleController(window)
title.main(controller)

#当前光标位置
top = 15
left = 4
gap = 50
curRow = 0
curCol = 0

chessbord.draw(window)
window.blit(curPos, (left, top))
bInit = 1


fps = 30
clock = pygame.time.Clock()
while True:
	clock.tick(fps)
	leftMouseButton = False
	moveResult = 0
	for event in pygame.event.get():
		if event.type == pygame.QUIT: #如果关闭窗口就退出
			sys.exit()
		elif event.type == pygame.MOUSEBUTTONDOWN: #鼠标控制
			leftMouseButton = pygame.mouse.get_pressed()[0]
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:# 如果按下Esc键也退出
				sys.exit()
			keyname = pygame.key.get_pressed()
			if keyname[pygame.K_LCTRL]:
				chessbord.showProb = not (chessbord.showProb)
				
			if keyname[pygame.K_u]:
				controller.undo(window)
			
			if keyname[pygame.K_LEFT]:
				curCol -= 1
				left -= gap
				if left <= 4:
					left = 4
					curCol = 0
			if keyname[pygame.K_RIGHT]:
				left += gap
				curCol += 1
				if left >= 400:
					left = 400
					curCol = 8

			if keyname[pygame.K_UP]:
				top -= gap
				curRow -= 1
				if top <= 15:
					top = 15
					curRow = 0

			if keyname[pygame.K_DOWN]:
				top += gap
				curRow += 1
				if top >= 465:
					top = 465
					curRow = 9   
	controller.act(leftMouseButton, window)
	pygame.display.update()
	# 更新显示
		#if 1 == moveResult:
		#	net = ChessNetwork()
		#	arrMove = net.getChessMove()
		#	if arrMove != None:
		#		chessbord.moveFrom = 1
		#		chessbord.moveChess(Position(arrMove[0], arrMove[1]))
		#		chessbord.moveChess(Position(arrMove[2], arrMove[3]))
		#		chessbord.moveFrom = 0
		#		moveResult = 0
			
		
		#if len(sys.argv) > 1 and 1 == bInit :
		#	#chessbord. curStepColor = CHESSMAN_COLOR_BLACK
		#	net = ChessNetwork()
		#	arrMove = net.getChessMove()
		#	if arrMove != None:
		#		chessbord.moveFrom = 1
		#		chessbord.moveChess(Position(arrMove[0], arrMove[1]))
		#		chessbord.moveChess(Position(arrMove[2], arrMove[3]))
		#		chessbord.moveFrom = 0
		#		bInit = 0
	


# Check following for pygame text input:
# http://www.pygame.org/pcr/inputbox/			
			
			
