#-*- encoding: utf-8 -*-
import socket
import sys

NETWORK_SUPPORT = 0 #是否提供网络支持

HOST = 'localhost' # 对方服务器地址

class ChessNetwork():
    '''
    提供网络支持，既是客户端，也是服务器,  p2p
    '''
    host = ''
    port = 64255    
        
    def sendChessMove(self, rowFrom, colFrom, rowTo, colTo):
        '''
        向对方服务器发送棋子移动信息
        '''      
        if NETWORK_SUPPORT == 0:
            return None
        msg = '%d,%d,%d,%d' % (rowFrom, colFrom, rowTo, colTo)        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, self.port))
            print('sendChessMove:')
            print(msg)
            s.send(msg)
            s.close()
        except :
            print('exception when sendChessMove')
        
    def getChessMove(self):
        '''
        从对方服务器获取棋子移动信息
        '''        
        if NETWORK_SUPPORT == 0:
            return None
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind((self.host,self.port))
        s.listen(1)

        print('getChessMove : accept')
        clientsock,clientaddr = s.accept()
        while 1:
            data = clientsock.recv(1024)
            if not data:
                break
            clientsock.close()
            listRet = data.split(',')
            for i in range(len(listRet)):
                listRet[i] = int(listRet[i])
            return listRet
                
        
if __name__ == '__main__':
    #测试
    net = ChessNetwork()
    if len(sys.argv)  > 1:
        #服务器
        print(net.getChessMove())
    else:
        #客户端
        net.sendChessMove(0, 0, 1, 1)
    
    
