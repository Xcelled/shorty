import ctypes, os
from shared import *

xlib = ctypes.cdll.LoadLibrary('libX11.so')

class X11:
	''' X11 stuff '''

	# Keyboard modifiers
	ShiftMask = (1<<0)
	LockMask = (1<<1)
	ControlMask = (1<<2)
	Mod1Mask = (1<<3) # alt
	Mod2Mask = (1<<4) # num lock
	Mod3Mask = (1<<5) # scroll lock
	Mod4Mask = (1<<6) # Meta
	Mod5Mask = (1<<7) # 3rd level shift
	AnyModifier	= (1<<15)

	GrabModeAsync = 1
	KeyPressMask = 1

	class xcb_generic_event_t(ctypes.Structure):
		_fields_ = (
			('response_type', ctypes.c_ubyte),
			('pad0', ctypes.c_ubyte),
			('sequence', ctypes.c_ushort),
			('pad', ctypes.c_uint*7),
			('full_sequence', ctypes.c_uint),
		)
	#endclass

	class xcb_key_press_event_t(ctypes.Structure):
		_fields_ = (
			('response_type', ctypes.c_ubyte),
			('detail', ctypes.c_ubyte),
			('sequence', ctypes.c_ushort),
			('time', ctypes.c_uint),
			('root', ctypes.c_uint),
			('event', ctypes.c_uint),
			('child', ctypes.c_uint),
			('root_x', ctypes.c_short),
			('root_y', ctypes.c_short),
			('event_x', ctypes.c_short),
			('event_y', ctypes.c_short),
			('state', ctypes.c_ushort),
			('same_screen', ctypes.c_ubyte),
			('pad0', ctypes.c_ubyte),
		)
#endclass

def toNativeModifiers(flags):
	''' Converts the standard modifier flags to X11's '''
	map = zip(
		[Modifiers.Shift, Modifiers.Control, Modifiers.Alt, Modifiers.Meta],
		[X11.ShiftMask  , X11.ControlMask  , X11.Mod1Mask , X11.Mod4Mask  ]
		)

	native = 0
	for mod, n in map:
		if flags & mod: native |= n
	#endfor

	return native
#enddef

def toNativeKeycode(key):
	return key
#enddef

class X11Shorty:
	''' X11 Variant of shortcut manager '''
	def __init__(self):
		self.display = xlib.XOpenDisplay(os.environ['DISPLAY'])
		self.ignored = [0, X11.LockMask, X11.Mod2Mask, X11.LockMask | X11.Mod2Mask]
		self.root = xlib.XDefaultRootWindow(self.display)
	#enddef

	def __del__(self):
		XCloseDisplay(self.display)
	#enddef

	def _listenerLoop(self):
		xlib.XSelectInput(self.display, self.root, X11.KeyPressMask)

		while True:
			xlib.XNextEvent(self.display)


	def _grabKey(self, keycode, modifiers, window):
		xlib.XGrabKey(self.display, keycode, modifiers, window, True, GrabModeAsync, GrabModeAsync)

		return True # TODO: error handling
	#enddef

	def _ungrabKey(self, keycode, modifiers, window):
		xlib.XUngrabKey(self.display, keycode, modifiers, window)

		return True # TODO: error handling
	#enddef

	def registerShortcut(self, key, modifiers):
		# X has a stupid system where even the numlock counts as
		# a modifier. So have to register multiple hotkeys, one for
		# each combination of modifiers we don't care about
		
		nativeKey = toNativeKeycode(key)
		nativeMod = toNativeModifiers(modifiers)
		win = self._rootWindow()

		for i in self.ignored:
			if not self._grabKey(nativeKey, nativeMod | i, win): return False
		#endfor

		return True
	#enddef

	def unregisterShortcut(self, key, modifiers):
		nativeKey = toNativeKeycode(key)
		nativeMod = toNativeModifiers(modifiers)
		win = self._rootWindow()

		for i in self.ignored:
			self._ungrabKey(nativeKey, nativeMod | i, win)
		#endfor
	#enddef
#endclass