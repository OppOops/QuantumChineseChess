# QuantumChineseChess
  The basic rule of this game is same as [Chinese chess](https://en.wikipedia.org/wiki/Xiangqi). However, this new feature game is based 
  on quantum mechanics. Player can decide to divide a chess location as half probability with 2 move proceeding. The two divied chess share
  the relation of same feature as [superposition](https://en.wikipedia.org/wiki/Quantum_superposition). The undertermined chess will not able to know where it is until some **measure process** is done.
  
  The **measure process** happend when the chess is trying to capture or being capture. If the chess is truely on the location, the move will
  be valid. Also, if some chess is trying to go through the one is undetermined, that location will be measured too. The condtion probabilty 
  is sent back to other chess as information observed for board if the measure result show the location has nothing.
  
  Other important feature is based on **entanglement**. Entanglement is happending if two undertermine chess stick together. In this case, 
  two chess location are depends on each other. The move is valid only if the measure process find out the obstacle does not exist.
  
  For our social fan page, please checkout https://www.facebook.com/149258692216707/
  
## Dependencies
* Python 2
* Pygame
* PyOpenGL
* Sip (python package)
* py2exe (only requrired for Winodws environment without python)

## Current Features
* Simple Player Game, Internet Game, GUI menu
* Superposition, Entanglement for moveable chess
* Probability simulation process

## Execution

```
python ChsChess.py
```

## Build as exe file

```
python setup.py
```
Note:

(1) 'py2exe' needs to install from http://sourceforge.net/project/showfiles.php?group_id=15583 
	The above link is provided by https://pypi.python.org/pypi/py2exe/
	
(2) Sip in python 2 should compile from source code https://www.riverbankcomputing.com/software/sip/download/ 
	and configure it with some C++ compiler, and apply MAKEFILE command 'make', 'make install' to install package
	your machine. For futher detail, please see http://pyqt.sourceforge.net/Docs/sip4/installation.html
	
