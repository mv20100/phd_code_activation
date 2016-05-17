__all__ = [ ]

import os
import sys
import textwrap
import numpy as np
from numpy import ctypeslib
import ctypes
import ctypes.util
import ctypes.wintypes
import warnings

from uc480_tools_h import *
from ctypes.wintypes import BYTE
from ctypes.wintypes import WORD
from ctypes.wintypes import DWORD
from ctypes.wintypes import BOOL
AVI = ctypes.wintypes.HANDLE
from ctypes.wintypes import HDC
from ctypes.wintypes import HWND
from ctypes.wintypes import INT
c_char = ctypes.c_byte
c_char_p = ctypes.POINTER(ctypes.c_byte)
c_int_p = ctypes.POINTER(ctypes.c_int)
from ctypes import c_int
IS_CHAR = ctypes.c_byte 


if os.name=='nt':
    # UNTESTED: Please report results to http://code.google.com/p/pylibuc480/issues
    libname = 'uc480_tools'
    include_uc480_tools_h = os.environ['PROGRAMFILES']+'\\Thorlabs\\DCx Cameras\\Develop\\Include\\uc480_tools.h'
    lib = ctypes.util.find_library(libname)
    if lib is None:
		print 'uc480_tools.dll not found'


libuc480tools = ctypes.windll.LoadLibrary(lib)
if libuc480tools is not None:
	uc480_tools_h_name = 'uc480_tools_h'
	try:
		uc480_tools_h = "uc480_tools_h"
		#from uc480_tools_h import *
		#exec 'from %s import *' % (uc480_tools_h_name)
	except ImportError:
		uc480_tools_h = None
	if uc480_tools_h is None:
		assert os.path.isfile (include_uc480_tools_h), `include_uc480_tools_h`
		d = {}
		l = ['# This file is auto-generated. Do not edit!']
		error_map = {}
		f = open (include_uc480_tools_h, 'r')
		
		def is_number(s):
			try:
				float(s)
				return True
			except ValueError:
				return False
				
		for line in f.readlines():
			if not line.startswith('#define'): continue
			i = line.find('//')
			words = line[7:i].strip().split(None, 2)
			if len (words)!=2: continue
			name, value = words
			if value.startswith('0x'):
				exec '%s = %s' % (name, value)
				d[name] = eval(value)
				l.append('%s = %s' % (name, value))
			# elif name.startswith('DAQmxError') or name.startswith('DAQmxWarning'):
				# assert value[0]=='(' and value[-1]==')', `name, value`
				# value = int(value[1:-1])
				# error_map[value] = name[10:]
			# elif name.startswith('DAQmx_Val') or name[5:] in ['Success','_ReadWaitMode']:
				# d[name] = eval(value)
				# l.append('%s = %s' % (name, value))
			elif is_number(value):
				d[name] = eval(value)
				l.append('%s = %s' % (name, value))
			elif value.startswith('UC'):
				print value
				d[name] = unicode(value[3:-1])
				l.append('%s = unicode("%s")' % (name, value[3:-1]))
			elif d.has_key(value):
				d[name] = d[value]
				l.append('%s = %s' % (name, d[value]))
			else:
				d[name] = value
				l.append('%s = %s' % (name, value))
				pass
		l.append('error_map = %r' % (error_map))
		fn = os.path.join (os.path.dirname(os.path.abspath (__file__)), uc480_tools_h_name+'.py')
		print 'Generating %r' % (fn)
		f = open(fn, 'w')
		f.write ('\n'.join(l) + '\n')
		f.close()
		print 'Please upload generated file %r to http://code.google.com/p/pylibuc480/issues' % (fn)
	else:
		pass
		#d = uc480_h.__dict__
	
#	for name, value in d.items():
#		if name.startswith ('_'): continue
#		exec '%s = %r' % (name, value)


# def CHK(return_code, funcname, *args):
    # """
    # Return ``return_code`` while handle any warnings and errors from
    # calling a libuc480 function ``funcname`` with arguments
    # ``args``.
    # """
    # if return_code==0: # call was succesful
        # pass
    # else:
        # buf_size = default_buf_size
        # while buf_size < 1000000:
            # buf = ctypes.create_string_buffer('\000' * buf_size)
            # try:
                # r = libuc480.DAQmxGetErrorString(return_code, ctypes.byref(buf), buf_size)
            # except RuntimeError, msg:
                # if 'Buffer is too small to fit the string' in str(msg):
                    # buf_size *= 2
                # else:
                    # raise
            # else:
                # break
        # if r:
            # if return_code < 0:
                # raise RuntimeError('%s%s failed with error %s=%d: %s'%\
                                       # (funcname, args, error_map[return_code], return_code, repr(buf.value)))
            # else:
                # warning = error_map.get(return_code, return_code)
                # sys.stderr.write('%s%s warning: %s\n' % (funcname, args, warning))                
        # else:
            # text = '\n  '.join(['']+textwrap.wrap(buf.value, 80)+['-'*10])
            # if return_code < 0:
                # raise RuntimeError('%s%s:%s' % (funcname,args, text))
            # else:
                # sys.stderr.write('%s%s warning:%s\n' % (funcname, args, text))
    # return return_code
	
def CALL(name, *args):
	"""
	Calls libuc480 function "name" and arguments "args".
	"""
	funcname = 'isavi_' + name
#	print name
	func = getattr(libuc480tools, funcname)
	new_args = []
	for a in args:		
		if isinstance (a, unicode):
			print name, 'argument',a, 'is unicode'
			new_args.append (str (a))
		else:
			new_args.append (a)
	# print new_args
	r = func(*new_args)
	# print r
  # r = CHK(r, funcname, *new_args)
	return r

		
class aviCapture():
	def __init__(self,camera):
		self.id = ctypes.c_int(10)
		CALL('InitAVI',ctypes.byref(self.id),camera)
		print "InitAVI ID: "+str(self.id.value)
		return None

	def SetImageSize(self,cMode,width,height,posX,posY,lineOffset):
		return CALL('SetImageSize',self.id,
					ctypes.c_int(cMode),
					ctypes.c_int(width),
					ctypes.c_int(height),
					ctypes.c_int(posX),
					ctypes.c_int(posY),
					ctypes.c_int(lineOffset))
	
	def SetImageQuality(self,iQuality):
		return CALL('SetImageQuality',self.id,ctypes.c_int(iQuality))
	
	def OpenAVI(self,filename):
		fname = ctypes.c_char_p(filename)
		return CALL('OpenAVI',self.id,fname)

	def SetFrameRate(self,fps):
		return CALL('SetFrameRate',self.id,ctypes.c_double(fps))
	
	def StartAVI(self):
		return CALL('StartAVI',self.id)

	def AddFrame(self, pcImageMem):
		return CALL('AddFrame',self.id,pcImageMem)

	def StopAVI(self):
		return CALL('StopAVI',self.id)
		
	def CloseAVI(self):
		return CALL('CloseAVI',self.id)

	def ExitAVI(self):
		return CALL('ExitAVI',self.id)
		
	def GetAVIFileName(self):
		fileName = c_char_p()
		CALL('GetAVIFileName',self.id,ctypes.byref(fileName))
		return fileName
	
	def GetAVISize(self):
		size = ctypes.c_float()
		CALL('GetAVISize',self.id,ctypes.byref(size))
		return size

	def GetnCompressedFrames(self):
		number = ctypes.c_ulong()
		CALL('GetnCompressedFrames',self.id,ctypes.byref(number))
		return number		

	def GetnLostFrames(self):
		number = ctypes.c_ulong()
		CALL('GetnLostFrames',self.id,ctypes.byref(number))
		return number	

	def ResetFrameCounters(self):
		return CALL('ResetFrameCounters',self.id)
		
	