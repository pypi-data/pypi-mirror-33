# -*- coding:utf-8 -*- 
# Date: 2018-03-30 15:38:38
# Author: dekiven

import os
import time

from DKVTools.Funcs import *
from TkToolsD.CommonWidgets import *
from TkToolsD.ImgView import *

if isPython3() :
	import tkinter as tk  
	from tkinter import ttk 
	from tkinter.font import Font
else :
	import Tkinter as tk  
	import  ttk
	from tkFont import Font	

#import sys 
#reload(sys)
#sys.setdefaultencoding('utf-8')
THIS_DIR = os.path.abspath(os.path.dirname(__file__))


class MultiFileChooser(ttk.Treeview) :
	'''MultiFileChooser
	'''
	# scrollbar orientation vertical
	BarDir_V = 0b0001
	# scrollbar orientation horizontal
	BarDir_H = 0b0010
	# scrollbar orientation both vertical and horizontal
	BarDir_B = 0b0011

	__keySetLeft = ('Left')
	__keySetRight = ('Right')
	__keySetUp = ('Up')
	__keySetDown = ('Down')
	def __init__(self, *args, **dArgs) :
		ttk.Treeview.__init__(self, *args, **dArgs) 

		self.scrollbarV = None
		self.scrollbarH = None

		self.rootPath = ''

		self.rowHeight = 20
		self.skipExts = ()
		self.choosenFiles = ()
		self.timeStamp = time.time()
		self.callback = None

		self.tagNames = ('f_normal', 'f_checked', 'd_normal', 'd_part', 'd_checked', )
		self.__imgs = {}
		self.items = {
			# name : [path, isDir, status]
		}
		self.files = {}
		self.dirs = {}

		self.img_normal = None
		self.img_checked = None
		self.img_part = None

		self.style = ttk.Style(self)

		handleToplevelQuit(self, self.__onDestroy)
		self.setRowHeight(self.rowHeight)

		self.__registEvents()

		# 设置canvas所在单元格(0, 0)可缩放
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		# 默认显示两个方向的滚动条
		self.setBarOrientation(self.BarDir_B)


	def __registEvents(self):
		self.bind('<<TreeviewSelect>>', self.__onSelected)
		self.bind('<<TreeviewOpen>>', self.__onOpen)
		self.bind('<<TreeviewClose>>', self.__onClose)

	def __releaseIcons(self) :
		for k in tuple(self.__imgs.keys()) :			
			self.__releaseIcon(k)

	def __releaseIcon(self, key) :
		i = self.__imgs.get(key)
		if i is not None:
			i.release()
			del i

	def __onSelected(self, event):
		item = self.selection()
		if len(item) == 1 :
			name = item[0]
			data = self.items.get(name)
			if data[1] :
				# dir
				self.__onDirClicked(name)
			else :
				self.__onFileClicked(name)
				# file

	def __onOpen(self, event):
		# item = self.selection()
		self.timeStamp = time.time()


	def __onClose(self, event):
		# item = self.selection()
		self.timeStamp = time.time()


	def __updateStyles(self) :
		height = self.rowHeight
		size = (height, height)
		self.__releaseIcons()

		font = Font()
		font = Font(size=str(2-height))
		self.style.configure('Treeview', rowheight=height)
		f = pathJoin(THIS_DIR, 'res/%s.png')
		for t in self.tagNames :
			img = GetImgTk(f%(t), size)
			self.__imgs[t] = img
			self.tag_configure(t, image=img, font = font)		

	def __onDestroy(self) :
		self.__releaseIcons()			

	def __onDirClicked(self, name):
		if time.time() - self.timeStamp < 0.5 :
			return
		data = self.items.get(name)
		if data :
			children = self.get_children(name)
			status = data[2]
			if status == 'd_normal' :
				status = 'checked'
			elif status == 'd_part' :	
				status = 'checked'
			elif status == 'd_checked' :
				status = 'normal'

			self.__changeItemStatus(name, status)

	def __onFileClicked(self, name):
		data = self.items.get(name)
		if data :
			status = data[2]
			if status == 'f_normal' :
				status = 'checked'
			elif status == 'f_checked' :
				status = 'normal'

			self.__changeItemStatus(name, status)

	def __changeItemStatus(self, name, status, skipCallback=False) :
		self.__changeTag(name, status)
		self.__updateParentStatus(name)
		if not skipCallback :
			self.__getChoosenFiles()

		self.update_idletasks()
		# natural = self.winfo_reqwidth()
		# natural = self.winfo_reqheight()
		# self.configure(scrollregion=self.bbox(''))

	def __changeTag(self, name, tag, forChild=True) :
		if name == '' :
			return
		t = 'd_'+tag
		if self.isDir(name) :
			names = self.get_children(name)
			if forChild :
				for n in names:
					self.__changeTag(n, tag)
		else :
			if tag == 'part' :
				return
			t= 'f_'+tag
		self.item(name, tag=[t,])
		self.items[name][2] = t

	def __updateParentStatus(self, name) :
		parent = self.parent(name)
		if parent != '' :
			data = self.items.get(parent)
			if data :
				children = self.get_children(parent)
				checked = None
				for c in children :
					# if not self.isDir(c) :
					s = self.items[c][2].split('_')[1]
					checked = checked or s
					if (checked is not None and checked != s) or checked == 'part':
						checked = 'part'
						break
				self.__changeTag(self.formatPath(parent), checked, False)
				self.__updateParentStatus(parent)

	def isDir(self, name) :
		data = self.items.get(name)
		if data :
			return data[1]

	def setRowHeight(self, height) :
		self.rowHeight = height
		self.__updateStyles()

	def setPath(self, path, skip=(), choosenFiles=[]) :
		if path is None :
			return
		if os.path.isdir(path) :
			if isinstance(skip, list) or isinstance(skip, tuple) :
				self.skipExts = skip
			else :
				self.skipExts = str(skip).split(',')
			self.clearItems()
			self.rootPath = path
			self.insertPath(path)
			self.setChoosenFiles(choosenFiles)


	def clearItems(self):
		[self.delete(i) for i in self.get_children('')]
		self.items = {}
		self.files = {}
		self.dirs = {}


	def insertPath(self, path, parent=''): 
		if parent == '' :
			self.heading('#0', text=path) 
		skip = self.skipExts
		for p in os.listdir(path) :	
			split = os.path.splitext(p)
			ext = split[1] == '' and split[0] or split[1]	
			# print(split, ext)
			if not ext in skip :
				abspath = os.path.join(path, p)
				abspath = self.formatPath(abspath)
				isDir = os.path.isdir(abspath)
				tag = isDir and 'd_normal' or 'f_normal'
				item = self.insert(parent, 'end', text=self.__getUtfStr(p), open=False, tags = [tag,])
				self.items[item] = [abspath, isDir, tag]
				appDic = isDir and self.dirs or self.files
				appDic[abspath] = item
				if isDir :
					self.insertPath(abspath, item)

	def getChoosenFiles(self) :
		return self.__getChoosenFiles(True)

	def setChoosenCallback(self, callback) :
		self.callback = callback

	def setChoosenFiles(self, files) :
		files = list(files)
		if self.rootPath != '' :
			for i in range(len(files)) :
				f = files[i]
				if not os.path.isabs(f) :
					f = pathJoin(self.rootPath, f)
					files[i] = self.formatPath(f)
				f = self.formatPath(f)
				item = self.files.get(f)
				if item and not self.isDir(item) :
					self.__changeItemStatus(item, 'checked', True)
			for f in set(self.files) - set(files) :
				item = self.files.get(f)
				if item and not self.isDir(item) :
					self.__changeItemStatus(item, 'normal', True)
		else :
			print(u'请先设置根目录再设置已选中的文件！')

	def formatPath(self, path) :
		return path.replace('\\', '/')

	def __getChoosenFiles(self, fresh=False) :
		files = []
		needCall = isFunc(self.callback)
		if (not needCall and fresh) or needCall :
			for f in (self.items.values()) :
				if not f[1] and f[2] == 'f_checked' :
					files.append(f[0])
			files.sort()
			self.choosenFiles = files
			if needCall and not fresh:
				self.callback(files)
		return self.choosenFiles

	def __getUtfStr(self, oriStr, decode='GB2312') :
		# TODO:部分不能正常转码
		# s = ''
		# if isFunc(oriStr.decode) :
		# 	try:
		# 		s = oriStr.decode(decode)
		# 	except Exception , e:
		# 		s = oriStr.decode('utf-8')
		# s = s.encode('utf-8')
		return oriStr


# ---------------------------------scrollbar begin-----------------------------------------
	# TODO:dekiven 将scrollbar相关抽象到一个基类当中
	def setBarOrientation(self, orientation):
		self.barOrient = orientation

		# 有竖直方向的滚动条
		scrollbar = self.scrollbarV

		if orientation & self.BarDir_V > 0:
			if scrollbar is None:
				scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
				scrollbar.configure(command=self.__yview)
				self.configure(yscrollcommand=scrollbar.set)
				self.scrollbarV = scrollbar
				scrollbar.grid(column=1, row=0,sticky=tk.N+tk.S)
			else :
				config = scrollbar.grid_info()
				# scrollbar.grid()
				scrollbar.grid(**config)
		elif scrollbar is not None:
			scrollbar.grid_remove()

		# 有水平方向的滚动条
		scrollbar = self.scrollbarH
		if orientation & self.BarDir_H > 0:
			if scrollbar is None:
				scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
				scrollbar.configure(command=self.__xview)
				self.configure(xscrollcommand=scrollbar.set)
				self.scrollbarH = scrollbar
				scrollbar.grid(column=0, row=1, sticky=tk.W+tk.E)
			else :
				config = scrollbar.grid_info()
				# scrollbar.grid()
				scrollbar.grid(**config)
		elif scrollbar is not None:
			scrollbar.grid_remove()

	def movetoPercentV(self, percent) :
		self.yview('moveto', str(percent/100.0))

	def movetoPercentH(self, percent) :
		self.xview('moveto', str(percent/100.0))

	def moveToTop(self) :
		self.movetoPercentV(0)

	def moveToBottom(self) :
		self.movetoPercentV(100)

	def movetToLeft(self) :
		self.movetoPercentH(0)

	def movetToRight(self) :
		self.movetoPercentH(100)

	def moveUpOneStep(self) :
		self.yview(tk.SCROLL, -1, tk.UNITS)

	def moveDownOneStep(self) :
		self.yview(tk.SCROLL, 1, tk.UNITS)

	def moveLeftOneStep(self) :
		self.xview(tk.SCROLL, -1, tk.UNITS)

	def moveRightOneStep(self) :
		self.xview(tk.SCROLL, 1, tk.UNITS)

	def __yview(self, *args, **dArgs) :
		# print('yview', args, dArgs)
		self.yview(*args, **dArgs)

	def __xview(self, *args, **dArgs) :
		# print('xview', args, dArgs)
		self.xview(*args, **dArgs)
# ===================================scrollbar end===============================================

def __main() :

	path = os.getcwd()
	testCall = True

	m = MultiFileChooser()
	m.pack(expand=YES,fill=BOTH)
	# m.setPath(path, '.manifest', ['D:/Python27/lib/site-packages/TkToolsD/__init__.py', 'D:/Python27/lib/site-packages/TkToolsD/res/d_checked.png', 'D:/Python27/lib/site-packages/TkToolsD/res/d_normal.png', 'D:/Python27/lib/site-packages/TkToolsD/res/f_checked.png', 'D:/Python27/lib/site-packages/TkToolsD/res/f_normal.png'])
	# m.setPath(path, '.manifest', ['__init__.py', 'res/d_checked.png', 'res/d_normal.png', 'res/f_checked.png', 'res/f_normal.png'])
	m.setPath(path, '.manifest', [])
	# m.setChoosenFiles(['D:/Python27/lib/site-packages/TkToolsD/CommonWidgets.py',])
	m.setChoosenFiles(['CommonWidgets.py',])
	if testCall :
		def callbcak (files) :
			print(files)

		m.setChoosenCallbcak(callbcak)
	else :
		def cmd () :
			print(m.getChoosenFiles())
		tk.Button(text='test', command=cmd).pack()

	m.mainloop()
	

if __name__ == '__main__':
	__main()

