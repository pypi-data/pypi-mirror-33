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

#: Geometric transformations can lead to interpolation artifacts
"""
Illustrates the artifacts that may be created
(especially in unlinearized stimuli) when a texture
stimulus is rotated, scaled or translated by an
amount that has not been appropriately rounded.
"""#.
if __name__ == '__main__':

	import os
	import sys
	import numpy
	import Shady


	"""
	Create a World:
	"""#:
	cmdline = Shady.WorldConstructorCommandLine()
	cmdline.Option( 'gamma', -1, type=( int, float ), min=-1, doc="Gamma-correction parameter for some of the stimuli (-1 means sRGB)." )
	cmdline.Help().Finalize()
	w = Shady.World( bg=0.5, **cmdline.opts )
	
	"""
	Some gamma-corrected stimuli:
	"""#:
	size = min( w.width // 3 - 100, w.height // 2 - 100 )
	noise = numpy.random.uniform( size=[ size, size ] )
	xshift = size * 1.1
	yshift = ( w.height + size ) // 6
	
	s1 = w.Stimulus( noise, x=-xshift, y=-yshift, atmosphere=w )
	s2 = w.Stimulus( noise, x=0,       y=-yshift, atmosphere=w )
	s3 = w.Stimulus( noise, x=+xshift, y=-yshift, atmosphere=w )
	
	"""
	And some definitely-uncorrected stimuli:
	"""#:
	s4 = w.Stimulus( noise, x=-xshift, y=+yshift, gamma=1.0 )
	s5 = w.Stimulus( noise, x=0,       y=+yshift, atmosphere=s4 )
	s6 = w.Stimulus( noise, x=+xshift, y=+yshift, atmosphere=s4  )

	"""
	Now let's make the stimuli on the left rotate very slightly
	back and forth; the ones in the middle will shrink and grow
	very slightly; and the ones on the right will get translated
	diagonally back and forth by a sub-pixel amount. All of these
	transformations will create interpolation artifacts, which may
	be very noticeable in the unlinearized stimuli.
	"""#:
	freq = 0.5
	s4.envelopeRotation = s1.envelopeRotation = Shady.Oscillator( freq ) * 2
	s5.envelopeScaling  = s2.envelopeScaling  = Shady.Oscillator( freq ) * 0.02 + 1.0
	s6.envelopeOrigin   = s3.envelopeOrigin   = Shady.Oscillator( freq ) * 1.0
	# Unlike ordinary "repositioning" translations (due to the .envelopeTranslation
	# and .anchor properties), the translation values in .envelopeOrigin are not
	# rounded to the nearest pixel. Therefore .envelopeOrigin allows sub-pixel
	# translations, which cause interpolation artifacts.
	
	""#.
	@w.EventHandler( slot=1 )
	def eh( self, event ):
		if event.type == 'text' and event.text == '0': 
			s4.ResetClock()
			s5.ResetClock()
			s6.ResetClock()
			
	"""
	If the "gamma-corrected" stimuli are, in fact, not well
	gamma-corrected on your particular screen, then perhaps
	`gamma=-1` (i.e. the sRGB profile) was not the correct choice.
	You could always experiment with adjusting `w.gamma` by hand.
	Or adjust it using the mouse/touch-screen, with::
	"""#:
	
	Shady.Utilities.AdjustGamma( w )   # we don't frequently use this function
	                                   # which is why it is not in the top-level
	                                   # `Shady.` namespace. Normally we would
	                                   # use `Shady.FindGamma` which wraps it but
	                                   # which also renders a linearization pattern.
	
	""#>
	print( 'Press escape to close the window' )
	Shady.AutoFinish( w )