The Binary "Accelerator" Component (`ShaDyLib`)
===============================================

.. admonition:: Summary
	:class: tip

	Shady comes with an "accelerator"---a dynamic library that greatly improves its
	performance. The Shady Python package installation includes pre-built ``.dll``
	files for 32-bit Windows and 64-bit Windows, and a ``.dylib`` file for macOS 10.9+.
	If your platform is not supported by these included binaries, you can build the
	accelerator yourself, from our C++ sources.

Shady works by harnessing the graphics processor (GPU) to perform, in parallel, most
of the pixel-by-pixel operations entailed in signal generation, contrast modulation,
windowing, linearization and dithering.  For most stimulus arrangements, this leaves
relatively little for the CPU to do on each frame: it just has to issue the OpenGL
commands that clear the screen and then, for each stimulus in turn, transfer a small
set of variable values from CPU to GPU.  Nonetheless this may amount to a few hundred
separate operations per frame---we'll call these the "CPU housekeeping" operations
(and we'll consider them separate from the optional further computations that can be
performed between frames to :doc:`animate <MakingPropertiesDynamic>` stimuli).

The CPU housekeeping is performed by an "engine". The earliest versions of Shady
implemented the engine in pure Python. Some of the time, this worked fine, but it was
prone to sporadic frame skips.  So, we transitioned to using the "accelerator" which is
a binary engine compiled from C++ and packaged as a dynamic library called ShaDyLib.
Some binary builds of ShaDyLib are included with the Shady Python package: `.dll` files
for 32- and 64-bit Windows, and a `.dylib` file for 64-bit macOS 10.9 (Mavericks, 2013)
and up. These are used by default where possible.  To make the corresponding `.so` file
for Linux (or the `.dylib` for macOS versions between 10.4 through 10.8), you would
need to build it yourself from the C++ sources (see below).

The pure-Python engine is still included (as the `Shady.PyEngine` submodule) and it is
used automatically as a fallback when the accelerator is not available. But it is much
better to use the accelerator (and to attempt to compile the accelerator from source if
the dynamic library for your platform is not already part of Shady). The problem is that
Python, being a high-level dynamic interpreted language, is inefficient for performing
large numbers of simple operations. Relative to the equivalent operations compiled from
C++, Python not only requires extra time but, critically, adds a large amount of
*variability* to the time taken when running on a modern operating system that tends to
perform a lot of sporadic background tasks (the effect of these is especially noticeable
on Windows).  Hence the frequent sporadic frame skips when using the `PyEngine`, which
become much rarer when you use the accelerator.


Windowing and Rendering
-----------------------

These are two separate issues:

Windowing
	is about creating a window and an associated OpenGL context, synchronizing the
	double-buffer flipping with the display hardware's frame updates, and handling
	events such as keyboard and mouse input.
	
Rendering
	is about the OpenGL calls that comprise most of the frame-by-frame CPU
	housekeeping. Rendering is implemented in a windowing-independent way (i.e.
	without reference to the windowing environment or its particular implementation).

The `ShaDyLib` accelerator provides independent implementations of both windowing
(using a modified `GLFW <http://glfw.org>`_ C library) and rendering. Assuming you have the
accelerator, you have three options:

1. Use the accelerator for both windowing and rendering.  When the accelerator is
   available, this is the default option, and is highly recommended for performance
   reasons.

2. Use a different windowing environment (such as `pyglet`) and still use the
   accelerator for rendering. There is no great advantage to doing this, and there
   are disadvantages here and there (e.g. failure to take full advantage of Mac Retina
   screen resolution).

3. Do not use the accelerator at all. Fall back to the `PyEngine`, which requires a
   third-party package to expose the necessary OpenGL calls. Either `pyglet <https://pypi.org/project/pyglet/>`_  or
   `PyOpenGL <https://pypi.org/project/PyOpenGL/>`_ will work for this (`pyglet` is probably the better choice
   because, in the absence of the accelerator, you will also need it for windowing 
   anyway). As explained above, this option is not recommended if you can avoid it.

The `BackEnd()` function allows you to change the default windowing and rendering
implementations.


Building the Accelerator from Source
------------------------------------

As we mentioned above, binaries are included in the Shady download, for 32-bit
Windows, 64-bit Windows, and for macOS 10.9+.  Therefore, we hope you will not
need to build the accelerator from source. However, if you need to do so for
any reason (for example to support Linux, or macOS 10.4-10.8) then it should
be relatively easy.  ("Should" is every engineer's most heavily loaded word.)

You can obtain the complete Shady source code from the master Mercurial repository
which is hosted at {repository}
::

	hg clone {repository}

(Or go there with a browser and clickety-clickety-download-unzippety if you must.)

Your working-copy of the repository will include a copy of the Shady package itself,
inside the `python` subdirectory. You can "install" this copy as your default Shady
package if you want: first change your working directory so that you're in the
root of the working-copy (i.e. the place that contains `setup.py`) and then call::

	python -m pip install -e .
	
The `-e` flag stands for "editable copy" and this type of "installation" does not
actually copy or move any files. Instead, it merely causes whichever Python
distribution you just invoked to make a permanent record of the location of the
appropriate directory, thereby ensuring that it is found when you say `import Shady`
in subsequent sessions.

Your working-copy of the repository will also include the `accel-src` directory tree
which contains the C++ sources for the accelerator.  To build these, you need to have
`CMake <http://cmake.org>`_ installed (version 3.7+) as well as a C++ compiler.  On
Windows, the compiler we use is Visual C++, installed as part of a free ("Express" or
"Community") edition of Visual Studio 2012 or later. On macOS, we use `gcc` installed
from the "XCode Command Line Tools" package (we don't need the full-blown XCode).

The script `accel-src/devel/build/go.cmd` can be run from a Windows Command Prompt or
from a `bash` command-line (e.g. from the "Terminal" app on macOS) and will run the
entire CMake + build process. If you're on Windows, and either your OS or your Python
distribution is 32-bit, then you need to explicitly say `go.cmd Win32`. Further
details are provided in the comments at the top of the `go.cmd` script.

The accelerator has two third-party depenencies: GLEW and GLFW.   GLEW is provided
as source. Binary builds of GLFW (slightly modified), are provided in the repository.
If for any reason you need to rebuild GLFW, see the instructions in
`accel-src/devel/glfw-3.2.1/build-notes.txt`

On Linux, we also found it necessary to install developer libraries and headers for the
following projects:  `X11 Xrandr Xi Xxf86vm Xcursor Xinerama`. We do not remember
much about the process of discovering these magic names, nor unfortunately what the
(equally magic, but maddeningly slightly different) `apt` package names were that
corresponded to each of them. Have you ever seen a wasp try to get out of a half-open
window?  That's us, building for Linux. But we do at least know that it's possible to
build a working accelerator, at least on a Ubuntu 14 VirtualBox. (Similarly, the wasp
will usually get out eventually.)

A successfully built shared library will end up in the `accel-src/release/` directory.
What do you do with it then? Well:

* If you are using the repository copy of the Shady Python package (i.e. you have
  performed `python -m pip install -e .` as described above, or you are working in the
  `python` directory next-door to `accel-src` when you start Python) then Shady will
  be smart enough, by default, to look for the accelerator in `../accel-src/release/`
  and to prefer it over any copy that it finds "bundled" in its own package directory.
  You can also explicitly control which version it prefers, by supplying either
  `acceleration='devel'` or `acceleration='bundled'` as a keyword argument, either to
  `Shady.BackEnd()` or to the `Shady.World()` constructor.

* You can verify which version of the accelerator is being loaded, by looking under
  `ShaDyLib` in the output of the `.ReportVersions()` method of an instantiated `World`,
  or failing that the global `Shady.ReportVersions()` function.

* Finally, maybe you would like to move the newly-built shared library into the "bundled"
  location within this, or within some other, Shady package directory? If so, you can run
  `python accel-src/devel/build/release.cmd --shady-package` .  This will copy all the
  material from `accel-src/release/` into the `accel` subdirectory of whichever Shady
  package is accessed by `import Shady`, in whichever Python distribution or virtual
  environment your `python` command invoked.
