#-*- encoding: utf-8 -*-
import time
import datetime  # for datetime
import operator
import pygame
import Tkinter
from BoardStage import NetworkController
from ChessGlobal import *  # for class Position, load_image
from NetworkChs import *
from pygame.locals import *
from threading import Thread
from Queue import Queue
import pygubu
import random

class Option:
	hovered = False	
	def __init__(self, text, pos):
		self.text = text
		self.rect = self.get_rect(pos)
		self.hovered = False
	
	def check_pos(self, base_pos):
		pos = tuple(map(operator.sub, pygame.mouse.get_pos(), base_pos))
		return self.rect.collidepoint(pos)
		
	def check_hover(self, base_pos):
		if(self.check_pos(base_pos)):
			self.hovered = True
		else:
			self.hovered = False
	
	def get_rect(self, pos):
		render = self.get_text_render()
		rect   = render.get_rect()
		rect.topleft = pos
		return rect
	
	def get_text_render(self):
		menu_font = pygame.font.SysFont('Georgia', 24)
		return menu_font.render(self.text, True, self.get_color())
		
	def get_color(self):
		if self.hovered:
			return (255, 255, 255)
		else:
			return (255, 255, 102)
			
	def draw(self, window):
		window.blit(self.get_text_render(), self.rect)
			
			
class OptionList:	
	def draw(self, sf, window, pos):
		for option in self.list:
			option.check_hover(pos)
			option.draw(sf)
		window.blit(sf, pos)
	
	def transition(self, titleCnt, stageCnt, pos):
		pass

class MainList(OptionList):
	def __init__(self):
		self.list = [Option("New Game", (35, 30)), \
		   Option("Internet Game", (35, 100)), \
		   Option("Options", (35, 170)), \
		   Option("Exit", (35, 240))]
		   
	def transition(self, titleCnt, stageCnt, pos):
		result = [ idx for idx, opt in enumerate(self.list) if opt.check_pos(pos)]
		if len(result)==0:
			return None
		elif result == [0]:
			return True
		elif result==[1]:
			titleCnt.setMenu(InternetList())
			return None
		elif result==[2]:
			optionDig = OptionController(stageCnt)
			optionDig.main()
			titleCnt.setMenu(MainList())
			return None
		else:
			sys.exit()
			
class InternetList(OptionList):
	def __init__(self):
		self.list = [Option("Create Server", (35, 30)), \
		   Option("Connect to server", (35, 100)), \
		   Option("Return", (35, 170))]
		   
	def serverHandle(self, stageCnt):
		status, config = self.optionHandle(stageCnt, serverMode=True)
		if status == False:
			return None
		serverDig = ServerController(stageCnt)
		return serverDig.main(config)		   

	def clientHandle(self, stageCnt):
		clientDig = ClientController(stageCnt)
		return clientDig.main()
	
	def optionHandle(self, stageCnt, serverMode=False):
		optionDig = OptionController(stageCnt)
		return optionDig.main(serverMode)
			
	def transition(self, titleCnt, stageCnt, pos):
		result = [ idx for idx, opt in enumerate(self.list) if opt.check_pos(pos)]
		if len(result) == 0:
			return None
		elif result == [0]:
			return self.serverHandle(stageCnt)
		elif result==[1]:
			return self.clientHandle(stageCnt)
		elif result==[2]:
			titleCnt.setMenu(MainList())
			return None

		
class ServerController:
	def __init__(self, stage):
		self.stage = stage
		self.message = Queue()
		self.infoFlag = False #wait app binding to address
		self.cancelFlag = False #cacel event
		self.doneFlag = False #connected event
		
	def main(self, config):
		net = NetworkController(self.stage)
		self.thread = net.setServer(self.net_bind_finished, self.net_connected, self.message)
		clock = pygame.time.Clock()
		while self.message.empty(): #block until bind finished
			clock.tick(20)
		self.set_info() #set bind info
		self.createDialog(self.address) #show waiting dialog to user
		if(self.cancelFlag == True):
			return None
		else:
			net.determinTurn(config)
			self.stage.setNetwork(net)
			return self.stage
	
	def set_info(self):
		address, conn = self.message.get()
		self.address = Address(address[0], address[1])
		self.conn = conn
		self.infoFlag = True
	
	def cancel(self):
		if self.infoFlag == True:
			self.thread.stop()
			self.infoFlag = False
			self.cancelFlag = True
			self.doneFlag = True
		self.dig.close()
	
	def net_bind_finished(self, address, conn, queue):
		queue.put((address, conn))
		
	def net_connected(self, queue):
		print 'invoked'
		queue.put(True)
	
	def createDialog(self, address):
		uiFile  = 'server.ui'
		binding = {'cancel_event': self.cancel}
		self.dig = Dialog(uiFile, binding)
		self.dig.protocol("WM_DELETE_WINDOW", self.cancel)
		self.dig.setVar('ip_address',address.ip)
		self.dig.setVar('port_number',address.port)
		self.message.put(self.dig.getRemoteQueue()) # put queue to network thread
		self.dig.show()

class ClientController:
	def __init__(self, stage):
		self.stage = stage
		self.message = Queue()
		self.infoFlag = False #wait app binding to address
		self.cancelFlag = False #cacel event
		self.doneFlag = False #connected event
	
	def main(self):
		self.createDialog()
		if(self.cancelFlag == False):
			net = NetworkController(self.stage)
			status, msg = net.setClient(self.address)
			if status == True:
				net.determinTurn()
				self.stage.setNetwork(net)
				return self.stage
			else:
				m = MessageBox('Connection Error: ' + msg, 'Warning')
				m.show()
		return None
	
	def connect(self):
		ip = self.dig.getVar('ip_address')
		port = self.dig.getVar('port_number')
		self.address = Address(ip, port)
		self.dig.close()
		
	def cancel(self):
		self.cancelFlag = True
		self.dig.close()
		
	def createDialog(self):
		uiFile  = 'client.ui'
		binding = {'cancel_event': self.cancel, 'connect_event': self.connect}
		self.dig = Dialog(uiFile, binding)
		self.dig.show()
	
class OptionController:
	def __init__(self, stage):
		self.stage = stage
		self.result = None
		self.cancelFlag = False
	
	def main(self, serverMode=False):
		self.createDialog(serverMode)
		return (not self.cancelFlag), self.result
	
	def __trick(self, result):
		if(result['colorOrder']==3):
			result['colorOrder'] = random.randint(1, 2)
		return result
	
	def ok(self):
		result = self.dig.getVars(('colorOrder', 'showProb', 'showEnt'))
		result = self.__trick(result)
		self.stage.setConfig(result)
		self.result = result
		self.dig.close()
		
	def cancel(self):
		self.cancelFlag = True
		self.dig.close()
		
	def createDialog(self, serverMode):
		if(serverMode):
			uiFile  = 'config_server.ui'
		else:
			uiFile  = 'config_single.ui'
		binding = {'cancel_event': self.cancel, 'ok_event': self.ok}
		self.dig = Dialog(uiFile, binding)
		self.dig.protocol("WM_DELETE_WINDOW", self.cancel)
		self.dig.show()

	
class DialogHookController(Thread):
	def __init__(self, dialog, message, endAll, remote):	
		Thread.__init__(self)
		self.dialog = dialog
		self.message = message
		self.endAll  = endAll
		self.remote = remote
		
	def checkRStop(self):
		if self.remote.empty() == False:
			return True
		else:
			return False
			
	def __close(self, msg):
		self.dialog.quit()
		self.endAll.put(msg)
					
	def stop(self):
		self.message.put(False)
		
	def hook(self):
		try:
			if(self.message.empty())==False:
				return False
			if(pygame.display.get_active())==True and self.dialog.focus_get()==None:
				self.dialog.focus_force()
			return True
		except:
			return False

	def run(self):
		clock = pygame.time.Clock()
		while self.hook():
			clock.tick()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.__close('end')
					return
			if(self.checkRStop()):
				self.__close('remote')
				return
		trash = self.message.get()
		
class DialogController:
	def __init__(self, guiApp):
		self.message = Queue()
		self.endAll  = Queue()
		self.remote = Queue()
		self.thread = DialogHookController(guiApp, self.message, self.endAll, self.remote)
		self.dialog = guiApp
		self.stopFlag = False
	
	def close(self):
		self.thread.stop()
		self.stopFlag = True
		self.dialog.destroy()
	
	def run(self):
		self.thread.start()
		self.dialog.mainloop()
		if not self.endAll.empty():
			msg = self.endAll.get()
			if(msg == 'end'):
				sys.exit()
			else:
				self.dialog.destroy()
				return
		elif not(self.stopFlag):
			self.thread.stop()
			
class Dialog(Tkinter.Tk):
	__path = 'IMG/'
	
	def __init__(self, UIfile, binding, title="Settings"):
		Tkinter.Tk.__init__(self)
		self.title(title)
		self.resizable(width=Tkinter.FALSE, height=Tkinter.FALSE)
		builder = pygubu.Builder()
		builder.add_from_file(self.__path + UIfile)
		mainwindow = builder.get_object('Frame', self)
		builder.connect_callbacks(binding)
		self.builder = builder
		self.dc = DialogController(self)
	
	def show(self):
		self.dc.run()
	
	def getRemoteQueue(self):
		return self.dc.remote
	
	def getVars(self, names):
		result = dict()
		for n in names:
			result[n] = self.getVar(n)
		return result
	
	def getVar(self, name):
		try:
			return self.builder.get_variable(name).get()
		except:
			return None
	
	def setVar(self, name, value):
		try:
			var = self.builder.get_variable(name)
			var.set(value)
			return True
		except Exception:
			return False
	
	def close(self):
		self.dc.close()
		
class MessageBox:	
	def __init__(self, message, title):
		self.dig = Dialog('message_box.ui', {'ok_event':self.ok }, title)
		self.dig.setVar('error_msg', message)
		
	def show(self):
		self.dig.show()
	
	def ok(self):
		self.dig.close()
		
class TitleController:
	def __init__(self, window):
		self.win = window
		img = load_image("./IMG/ground.png")
		alpha = 160
		img[0].fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
		self.gim = img[0]
	
	def redraw(self):
		self.win.fill((0,0,0))
		self.win.blit(self.gim, (0, 0))
		optionBox = pygame.Surface((260,300))   # per-pixel alpha
		optionBox.set_alpha(204)
		optionBox.fill((55,55,55))
		self.win.blit(optionBox, (100,100))
		
	def setMenu(self, state):
		self.menuBox = state
	
	def connect(self):
		print 'set!!'
		print self.dig.getVars(('colorOrder', 'showProb', 'showEnt'))
		self.dig.close()
		
	def cancel(self):
		self.dig.close()
		
	def openDia(self):
		uiFile  = 'config_single.ui'
		binding = {'cancel_event': self.cancel, 'ok_event': self.connect}
		self.dig = Dialog(uiFile, binding)
		self.dig.show()
	
	def main(self, controller):
		self.redraw()
		self.menuBox = MainList()
		fps = 30
		clock = pygame.time.Clock()
		while True:
			clock.tick(fps)
			for event in pygame.event.get():
				if event.type == pygame.QUIT: #如果关闭窗口就退出
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN: #鼠标控制
					if self.menuBox.transition(self, controller, (100,100)) != None:
						return
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:# 如果按下Esc键也退出
						sys.exit()
					elif event.key == pygame.K_F1:
						self.openDia()
			self.redraw()
			sf = pygame.Surface((260,300),SRCALPHA)
			self.menuBox.draw(sf, self.win, (100,100))
			pygame.display.update()
			
	