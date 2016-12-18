#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import glob, sys
from distutils.core   import setup
from py2exe import build_exe

class py2exe_MyPatch(build_exe.py2exe, object):
	def plat_prepare(self):
		super(py2exe_MyPatch, self).plat_prepare()
		self.dlls_in_exedir.extend(["tcl85.dll","tk85.dll"])


revision = "1.1.0.0"

if sys.platform == 'win32':
  # 检查命令行参数
  if len(sys.argv) == 1:
      sys.argv.append("py2exe_MyPatch")
      sys.argv.append("-q")
 
  setup(
	cmdclass={"py2exe_MyPatch" : py2exe_MyPatch},	
    platforms        = ['Windows'],
    version          = revision,
    description      = "Quantum Chinese chess",
    name             = "Quantum Chinese chess", 
    long_description = "Quantum Chinese chess",
    url              = "https://github.com/OppOops/QuantumChineseChess",     
    maintainer       = 'stuarts',
    maintainer_email = 'oppoops@gmail.com',
    zipfile          = None, # 不生成library.zip  
    windows = [
      {
        "script": "ChsChess.py",
        "icon_resources": [
          (0, "ChsChess.ico"),
         ]       
      }
    ],
    data_files = [('IMG', \
        [ \
        r'.\IMG\b_bing.png',  \
        r'.\IMG\b_jiang.png',  \
        r'.\IMG\b_ju.png',  \
        r'.\IMG\b_ma.png',  \
        r'.\IMG\b_pao.png',  \
        r'.\IMG\b_shi.png',  \
        r'.\IMG\b_xiang.png',  \
        r'.\IMG\curPos.png',  \
        r'.\IMG\curPos-blue.png',  \
        r'.\IMG\curPos-cyan.png',  \
        r'.\IMG\curPos-yellow.png',  \
		r'.\IMG\ground.png',  \
        r'.\IMG\r_bing.png',  \
        r'.\IMG\r_jiang.png',  \
        r'.\IMG\r_ju.png',  \
        r'.\IMG\r_ma.png',  \
        r'.\IMG\r_pao.png',  \
        r'.\IMG\r_shi.png',  \
        r'.\IMG\r_xiang.png',  \
		r'.\IMG\TurnIndicator.png',  \
        ]), \
		],
    options = {
      "py2exe_MyPatch":{
        "compressed"  : 1,
        "includes"    : ["sip", "Queue", "Tkinter", "pygubu.builder.tkstdwidgets",
                                              "pygubu.builder.ttkstdwidgets",
                                              "pygubu.builder.widgets.dialog",
                                              "pygubu.builder.widgets.editabletreeview",
                                              "pygubu.builder.widgets.scrollbarhelper",
                                              "pygubu.builder.widgets.scrolledframe",
                                              "pygubu.builder.widgets.tkscrollbarhelper",
                                              "pygubu.builder.widgets.tkscrolledframe",
                                              "pygubu.builder.widgets.pathchooserinput"],
        "optimize"    : 2,
        "excludes": ["readline"],
        "bundle_files": 1 # python, Qt等dll放入library
      },
    }
  )
