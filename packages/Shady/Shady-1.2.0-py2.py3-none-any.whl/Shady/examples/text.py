#!/usr/bin/env python
# $BEGIN_SHADY_LICENSE$
# 
# This file is part of the Shady project, a Python framework for
# real-time manipulation of psychophysical stimuli for vision science.
# 
# Copyright (C) 2017-18  Jeremy Hill, Scott Mooney
# 
# Shady is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# $END_SHADY_LICENSE$

#: How to manipulate text stimuli
"""
This demo provides a keyboard-interactive exploration of
Shady's text-rendering capabilities.

It requires third-party packages:  `numpy`, `pillow` and
will fail without them.  Also, `matplotlib` is needed to
access the system's fonts: without it, you will only be
able to render in the "monaco" font.

NB: changing the string content, or font style, of a
    text Stimulus causes the image to be re-rendered on
    the CPU and then transferred from CPU to GPU. This
    is less efficient than Shady normally aims to be,
    and can impact performance, so it's best to ensure
	it does not happen frequently in timing-critical
	applications (see the `showcase` demo for more
	details).
"""#.
if __name__ == '__main__':

	"""
	Enable text rendering by explicitly importing `Shady.Text`
	"""#:

	import Shady
	import Shady.Text  # necessary to enable text/font-handling functionality

	"""
	Parse command-line options and create a `World`:
	"""#:
	cmdline = Shady.WorldConstructorCommandLine( width=750, top=50 )
	cmdline.Help().Finalize()

	w = Shady.World( **cmdline.opts )

	"""
	Now we'll set up a list of test texts, a list of fonts,
	and a general-purpose function for cycling through them.
	"""#:
	TEXTS = [ Shady.Text.TEST, Shady.Text.TEST_UNICODE ]
	FONTS = list( Shady.Text.FONTS )
	def Cycle( lst, backwards=False ):
		if backwards: lst.insert( 0, lst.pop( -1 ) )
		else: lst.append( lst.pop( 0 ) )
		return lst[ -1 ]
	firstSampleText = Cycle( TEXTS )

	"""
	Creating a text stimulus is as easy as:
	"""#:
	sample = w.Stimulus( text=firstSampleText )
	
	"""
	We assigned a string to the `.text` property. In fact,
	that's a shorthand: what it implicitly does is ensure
	creation of an appropriate text-handling object in
	`sample.text`, and then set *its* property
	`sample.text.string` equal to the desired string.
	
	The `.text` property of a `Stimulus` supports dynamic
	assignment. Let's demonstrate by creating an informative
	caption below our text sample:
	"""#:
	def ReportFont( t ):
		if not sample.text: return ''
		warning = '' if sample.text.font_found else '\nnot available'
		return '%s (%s)%s' % ( sample.text.font, sample.text.style, warning )
	
	caption = w.Stimulus(
		text = ReportFont, 
		xy = lambda t: sample.Place( 0, -1 ) - [ 0, 30 ], # wherever the sample goes or however it grows,
		anchor = ( 0, 1 ),                                # the top edge of the caption will remain 30
		                                                  # pixels below the sample's bottom edge
	)
	caption.text.align = 'center'

	"""
	Let's set up an event-handler to allow exploration of
	various text properties using keystroke commands:
	"""#:
	@w.EventHandler
	def KeyboardControl( world, event ):
		if event.type == 'key_press':
			# Detect event.type in [ 'key_press', 'key_release' ] and examine event.key:
			# - event.key allows easy case-insensitive matching (it's always lower case);
			# - non-printing keystrokes (e.g. 'escape', 'up', 'down') are reported;
			# - have to be careful what you assume about international keyboard layouts
			#   e.g. the condition `event.key == '8' and 'shift' in event.modifiers`
			#   guarantees the '*' symbol on English layouts but not on many others;
			# - event is not auto-repeated when the key is held down.
			command = event.key
			if   command in [ 'q', 'escape' ]: world.Close()
			elif command in [ 'up'   ]: sample.text.linespacing *= 1.1
			elif command in [ 'down' ]: sample.text.linespacing /= 1.1

		if event.type == 'text':
			# Detect a event.type == 'text' and examine event.text:
			# - case sensitive;
			# - non-printing keystrokes cannot be detected;
			# - independent of keyboard layout (you get whatever symbol the user intended to type);
			# - events are re-issued on auto-repeat when the key is held down.
			command = event.text.lower()
			if   command in [ 'c' ]: sample.text.align = 'center'
			elif command in [ 'l' ]: sample.text.align = 'left'
			elif command in [ 'r' ]: sample.text.align = 'right'
			elif command in [ 'm' ]: sample.text.font = 'monaco'
			elif command in [ 'd' ]: sample.text.font = [ 'arial unicode', 'devanagari', 'nirmala' ] # whichever matches first
			elif command in [ 'f' ] and FONTS: sample.text.font = Cycle( FONTS, 'shift' in event.modifiers )
			elif command in [ 'b' ]: sample.text.bold = not sample.text.bold
			elif command in [ 'i' ]: sample.text.italic = not sample.text.italic
			elif command in [ 't' ]: sample.text = Cycle( TEXTS )  # this is a shorthand - could also say sample.text.string = Cycle( TEXTS )
			elif command in [ '-' ]:      sample.text.size /= 1.1   # .size is an alias for .lineHeightInPixels, so these lines will fail if
			elif command in [ '+', '=' ]: sample.text.size *= 1.1   # text size has most recently been controlled via .emWidthInPixels instead
			elif command in [ 'g' ]: sample.text.blockbg = None if sample.text.blockbg else ( 0, 0.7, 0 )
			elif command in [ 'y' ]: sample.text.bg = None if sample.text.bg else ( 0.7, 0.7, 0 )
			elif command in [ '[', ']' ]:
				direction = -1 if command in [ '[' ] else +1
				value = sample.text.border  # could be a scalar (proportion of line height) or tuple of absolute pixel widths (horizontal, vertical)
				try: len( value )
				except: sample.text.border = max( 0, value + direction * 0.1 )
				else:   sample.text.border = [ max( 0, pixels + direction * 10 ) for pixels in value ]
	"""
	That was quite a lot to take in.  So, let's render a legend
	that summarizes the possible keystrokes:
	"""#:
	
	instructions = """
  L / C / R   left / center / right alignment
F / shift+F   cycle through system fonts
      B / I   toggle .text.bold / .text.italic where possible
          M   set .text.font = 'monaco'  (our default font)
          T   toggle between English and Sanskrit demo texts
          D   try to find a Devanagari font, for the Sanskrit 
      - / +   increase / decrease .text.size
      [ / ]   increase / decrease .text.border
  up / down   increase / decrease .text.linespacing
          Y   toggle yellow .text.bg
          G   toggle green  .text.blockbg
 Q / escape   close window
"""

	legend = w.Stimulus(
		text = instructions.strip( '\n' ),
		anchor = ( -1, 1 ),    # Place the top-left corner of this stimulus...
		xy = w.Place( -1, 1 ), # ...in the top-left corner of the world.
		text_size = 20,        # This is a construction-time shortcut, equivalent to setting
		                       # `legend.text.size = 20` *after* the Stimulus is created
	)
	""#>
	print( instructions )
	Shady.AutoFinish( w )
