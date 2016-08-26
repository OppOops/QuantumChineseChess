# QuantumChineseChess
  The basic rule of this game is same as [Chinese chess](https://en.wikipedia.org/wiki/Xiangqi). However, this new feature game is based 
  on quantum mechanics. Player can decide to divide a chess location as half probability with 2 move proceeding. The two divied chess share
  the relation of same feature as [superposition](https://en.wikipedia.org/wiki/Quantum_superposition). The undertermined chess will not able to know where it is until some **measure process** is done.
  
  The **measure process** happend when the chess is trying to capture or being capture. If the chess is truely on the location, the move will
  be valid. Also, if some chess is trying to go through the one is undetermined, that location will be measured too. The condtion probabilty 
  is sent back to other chess as information observed for board if the measure result show the location has nothing.
  
  Other important feature is based on **entanglement**. Entanglement is happending if two undertermine chess stick together. In this case, 
  two chess location are depends on each other. The move is valid only if the measure process find out the obstacle does not exist.
  
## Dependencies
* Python 2
* Pygame
* PyOpenGL
* Sip (Python package)
* py2exe (only requrired for Winodws environment without python)

## Execution

```
Python ChsChess.py
```


## build as exe file

```
Python setup.py
```
