#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core   import setup
import sys

# 产品版本
revision = "1.0.0.0"

if sys.platform == 'win32':
  # 检查命令行参数
  if len(sys.argv) == 1:
      sys.argv.append("py2exe")
      sys.argv.append("-q")
 
  from py2exe import build_exe    
  setup(
    platforms        = ['Windows'],
    version          = revision,
    description      = "Chinese chess",
    name             = "Chinese chess", 
    long_description = "Chinese chess",
    url              = "www.cnblogs.com/stuarts",     
    maintainer       = 'stuarts',
    maintainer_email = 'stuarts740@gmail.com',
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
        ] \
        )],
    options = {
      "py2exe":{
        "compressed"  : 1,
        "includes"    : ["sip"],
        "optimize"    : 2,
        "excludes": ["readline"],
        "bundle_files": 1 # python, Qt等dll放入library
      },
    }
  )
