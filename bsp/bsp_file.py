#!/usr/bin/env python3
# coding=utf-8
import json
import binascii
import os

def bsp_file_search(path,kind):
	#result = [filename for t in os.walk(path) for filename in t[2] if s in os.path.splitext(filename)[0]]
    result = []
    for t in os.walk(path): #返回的是root,dirs,files
        for filename in t[2]: #t[2]指的就是files
            if kind in os.path.splitext(filename)[1]: #test.txt [0]为test [1]为.txt 文件名和扩展名
                result.append(filename)

    result.sort()
    return result

