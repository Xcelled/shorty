from threading import Thread

from Xlib import X,threaded
from Xlib.display import Display
from Xlib.ext import xinput
from Xlib.protocol.request import GrabKey, UngrabKey
from shared import *

def toNativeModifiers(flags):
	''' Converts the standard modifier flags to X's '''
	map = zip(
		[Modifiers.Shift, Modifiers.Control, Modifiers.Alt, Modifiers.Meta],
		[X.ShiftMask  , X.ControlMask  , X.Mod1Mask , X.Mod4Mask  ]
		)

	native = 0
	for mod, n in map:
		if flags & mod: native |= n
	#endfor

	return native
#enddef

class X11Shorty:
	''' X11 Variant of shortcut manager '''
	def __init__(self):
		self.display = Display()
		self.root = self.display.screen().root

		self.ignored = [0, X.LockMask, X.Mod2Mask, X.LockMask | X.Mod2Mask]
	#enddef

	def __del__(self):
		self.display.close()
	#enddef

	def _listenerLoop(self):
		self.root.xinput_select_events([(xinput.AllDevices, xinput.KeyPressMask)])
		while True:
			event = self.display.next_event()
			if event.type == X.KeyPress:
				#handle
				pass
			#endif
		#endwhile
	#enddef

	def _grabKey(self, keycode, modifiers, window):
		GrabKey(self.display.display, owner_events=True, grab_window=window,
				modifiers=modifiers, key=keycode,
				pointer_mode = X.GrabModeAsync, keyboard_mode=X.GrabModeAsync)

		return True # TODO: error handling?
	#enddef

	def _ungrabKey(self, keycode, modifiers, window):
		UngrabKey(self.display.display, grab_window=window,	modifiers=modifiers, key=keycode)

		return True # TODO: error handling?
	#enddef

	def registerShortcut(self, key, modifiers, callback):
		# X has a stupid system where even the numlock counts as
		# a modifier. So have to register multiple hotkeys, one for
		# each combination of modifiers we don't care about
		
		nativeKey = toNativeKeycode(key)
		nativeMod = toNativeModifiers(modifiers)

		for i in self.ignored:
			if not self._grabKey(nativeKey, nativeMod | i, self.root): return False
		#endfor

		return True
	#enddef

	def unregisterShortcut(self, key, modifiers):
		nativeKey = toNativeKeycode(key)
		nativeMod = toNativeModifiers(modifiers)

		for i in self.ignored:
			self._ungrabKey(nativeKey, nativeMod | i, self.root)
		#endfor
	#enddef
#endclass