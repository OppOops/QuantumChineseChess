#-*- encoding: utf-8 -*-
import datetime  # for datetime
from ChessGlobal import *  # for class Position, load_image
from Chessman import * # for class ChessmanJiang
from NetworkChs import *
from Queue import Queue

class NetworkController:
	def __init__(self, stageCnt):
		self.stage = stageCnt
		self.p2p   = P2Pconnection()
		self.flag  = Queue()
		self.turn  = True
		self.char  = None
		
	def setClient(self, address):
		self.char = 'client'
		return self.p2p.connect(address)
		
	def setServer(self, infoCallBack, proccedCallBack, queue):
		self.char = 'server'
		try:
			return self.p2p.accept(info_callback = infoCallBack, \
								   connected_callback = proccedCallBack, \
								   queue = queue, \
								   stopHandle = self.p2p.stopHandle)
		except:
			return None
	
	def setTurn(self, color):
		if color == 1:
			print 'First ', self.char
			self.turn = True
		else:
			print 'Second ', self.char
			self.p2p.recv(self.flag)
			self.turn = False
	
	def determinTurn(self, config=None):
		if(self.char == 'client'):
			message = Queue()
			thread = self.p2p.recv(queue=message)
			thread.join()
			color = message.get()
			self.stage.setConfig({'colorOrder':color})
			self.setTurn(color)
		else:
			color = config['colorOrder']
			if(color==1):
				color = 2
			else:
				color = 1
			self.p2p.send(color)
			self.setTurn(config['colorOrder'])
	
	def wait(self): #If Turn == False, wait oppent
		if not self.flag.empty():
			result = self.flag.get()
			self.stage.setBoard(result)
			self.turn  = True
		return self.turn == False
		
	def act(self, rec):
		self.p2p.send(rec)
		self.p2p.recv(self.flag)
		self.turn = False

class StageController:
	def __init__(self, chessBoard, cursorImg):
		self.chessboard = chessBoard
		self.curImg     = cursorImg
		self.boardStage = BoardStageSelect(self, chessBoard, Position(-1, -1))
		self.__defaultStage = BoardStageSelect(self, chessBoard, Position(-1, -1))
		self.record     = PreviousBoardRecord()
		self.net        = None
	
	def setConfig(self, config):
		self.chessboard.rotateColor(config.get('colorOrder', 1))
		if (config.get('colorOrder', 1)==2):
			self.boardStage.setWait(True)
		for key, value in config.iteritems():
			setattr(self.chessboard, key, value)
			
	def setNetwork(self, controller):
		self.net = controller
	
	def setStage(self, stage):
		if (self.net != None) and (self.net.wait()):
			stage.setWait(True)
		self.boardStage = stage
	
	def getMousePos(self):
		(xPos, yPos) = pygame.mouse.get_pos()
		curRow = (yPos - 15) / 50
		curCol = (xPos - 4) / 50
		return Position(curRow, curCol)
	
	def act(self, mouseClick, window):
		if (self.net!=None):
			self.net.wait()
		if (mouseClick) == False:
			self.draw(None, window)
			return
		Pos = self.getMousePos()
		if not Pos.isInBoarder():
			return
		rec = self.chessboard.condition.copyBoard()
		if(self.boardStage.actChess(Pos, self)): #True if board has changed
			self.record.push(rec)
			if(self.net != None):
				self.boardStage.setWait(True)
				self.net.act(self.chessboard.condition.serialize())
		self.draw(posToLeftTop(Pos), window)
		
	def undo(self, window):
		if(self.net != None ):
			return
		if(self.record.undo(self.chessboard)):
			self.boardStage = BoardStageSelect(self, self.chessboard, Position(-1, -1))
			self.draw(posToLeftTop(Position(0,0)), window)
	
	def setBoard(self, state):
		if(state.get('serialized', False)):
			state = self.chessboard.condition.deSerialize(state)
			self.boardStage = self.__defaultStage
			self.boardStage.setWait(False)
		self.chessboard._board       = state['board']
		self.chessboard.curStepColor = state['color']
		self.chessboard.mgr          = state['manager']
	
	def draw(self, CurPos, window):
		self.chessboard.draw(window)
		self.boardStage.draw(window)
		if CurPos != None:
			window.blit(self.curImg, CurPos)
			
	
class PreviousBoardRecord:
	def __init__(self):
		self.rep = []
	def push(self, previos):
		self.rep.append(previos)
	def undo(self, chessBoard):
		if self.rep == []:
			return False
		state = self.rep.pop()
		chessBoard._board       = state['board']
		chessBoard.curStepColor = state['color']
		chessBoard.mgr          = state['manager']
		return True

class BoardStageInterface:
	_chessBoard = None
	_pos = None
	_wait = False
	
	def __init__(self, controller, chessBoard, pos):
		self._controller = controller
		self._chessBoard = chessBoard
		self._condtion = chessBoard.condition
		self._pos = pos

	# Depending on the stage to do proper move.
	# Return True if change stage successfully, False otherwise.
	
	def actChess(self, pos, controller):
		raise NotImplementedError("Please Implement this method")

	# Draw on the window (with respect to the status of current stage)
	def draw(self, window):
		raise NotImplementedError("Please Implement this method")

	# Get reference of current position
	def getPos(self):
		return self._pos
		
	def setWait(self, status):
		self._wait = status
		if(status==True):
			self._chessBoard.setTip(None, self._wait)
		else:
			self._chessBoard.setTip('Your Turn', self._wait)


class BoardStageSelect(BoardStageInterface):
	# Selecting the piece on the given position
	
	def actChess(self, target, controller):
		#無法連續選擇顏色相同的棋子
		if self._condtion.moveChessColorJudge(target) == 0:
			return False
		#選中棋子，準備移動
		chessman = self._condtion.getChessman(target)
		if chessman != None:
			self._chessBoard.setTip(chessman.printInfo(), self._wait)
			controller.setStage(BoardStageClassical(controller, self._chessBoard, target))
			return False
		return False

	def draw(self, window):
		pass


class BoardStageClassical(BoardStageInterface):
	# Moving the selected piece to the given position
	
	def actChess(self, target, controller):
		source = self._pos
		chessman = self._chessBoard.getChessman(source)
		chessmanTo = self._chessBoard.getChessman(target)
		assert chessman != None

		if chessman.isSameColor(chessmanTo):
			if not(target == source):
				self._chessBoard.setTip(chessmanTo.printInfo(), self._wait)
				self._pos = target
			elif chessman.crossRiverLimit():
				return False
			elif target == source and self._wait == False:
				controller.setStage(BoardStageQuantum(controller, self._chessBoard, source))
			return False
			
		if chessman.ChessMoveJudge(target) != 1:
			return False
		if self._wait == True:
			return False
		#成功走棋
		tipText = 'last move: %s, %s' %  (chessman.printInfo(), target.str())
		# Move and change color
		self._chessBoard.setTip(tipText)
		self._chessBoard.sendChessMove(self._pos, target)
		controller.setStage(BoardStageSelect(controller, self._chessBoard, Position(-1, -1)))
		return True

	# Draw all possible moves of the selected piece
	def draw(self, window):
		mgr		 = self._chessBoard.mgr
		chessman = self._chessBoard.getChessman(self._pos)
		assert chessman != None
		for r in range(0, 10):
			for c in range(0, 9):
				pos = Position(r, c)
				chessmanTo = self._chessBoard.getChessman(pos)
				if chessman.isSameColor(chessmanTo):
					continue
				if chessman.ChessMoveJudge(pos) == 1:
					img, rc = load_image("./IMG/curPos-blue.png", 0xffffff)
					window.blit(img, posToLeftTop(pos))
		for pos in chessman.getSupLocationList(mgr):
			img, rc = load_image("./IMG/curPos-yellow.png", 0xffffff)
			window.blit(img, posToLeftTop(pos))


class BoardStageQuantum(BoardStageInterface):
	# Quantum move must be one middle step and one final step
	_midPos = None
	# Moving the selected piece to the given position
	def actChess(self, target, controller):
		chessman = self._chessBoard.getChessman(self._pos)
		chessmanTo = self._chessBoard.getChessman(target)
		assert chessman != None
		# The target cannot be the same color
		# TODO: add entanglement here
		if chessman.isSameColor(chessmanTo):
			self._chessBoard.setTip(chessmanTo.printInfo())
			controller.setStage(BoardStageClassical(controller, self._chessBoard, target))
			return False
			
		if self._midPos:
			chessman.move(self._midPos)
		
		if chessman.ChessMoveJudge(target) != 1: 
			return False # Move is not Accepted by rule
		elif chessmanTo != None:
			return False # Quantum move cannot capture
			
		if not self._midPos:
			self._midPos = target
			return False
		#成功走棋
		self._chessBoard.setTip('last Q move: %s, %s' %  (chessman.printInfo(), target.str()))
		self._chessBoard.sendChessMoveQuantum(self._pos, self._midPos, target)
		controller.setStage(BoardStageSelect(controller, self._chessBoard, Position(-1, -1)))
		return True

	# Draw all possible moves of the selected piece, also the mid move
	def draw(self, window):
		mgr		 = self._chessBoard.mgr
		chessman = self._chessBoard.getChessman(self._pos)
		assert chessman != None
		imgFile = "./IMG/curPos-cyan.png"
		if None != self._midPos:
			chessman.move(self._midPos)
			imgFile = "./IMG/curPos-blue.png"
		for r in range(0, 10):
			for c in range(0, 9):
				pos = Position(r, c)
				chessmanTo = self._chessBoard.getChessman(pos)
				if chessman.isSameColor(chessmanTo):
					continue
				# Quantum move cannot capture
				if chessmanTo != None:
					continue
				if chessman.ChessMoveJudge(pos) == 1:
					img, rc = load_image(imgFile, 0xffffff)
					window.blit(img, posToLeftTop(pos))
		for pos in chessman.getSupLocationList(mgr):
			img, rc = load_image("./IMG/curPos-yellow.png", 0xffffff)
			window.blit(img, posToLeftTop(pos))
