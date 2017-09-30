.. _`Usage`:

Usage
=====

Now that you've installed ``pixelart``, you need
to also tell it where your Minecraft jar is.
Currently, the script has only been tested on jars
from Minecraft 1.11.x and 1.12.x. Older versions
which put all the textures into one image are 
currently not supported.

You can also directly use a texture pack made for
one of these recent versions of Minecraft, instead
of finding the jar. However, this might mean (unless
you use the faithful pack) that viewers of your 
pixel art won't be able to view it with the right
colors!

Finding your Minecraft jar
--------------------------

This really depends on which launcher you use, and
the platform you are running on. If
using the default launcher, it should be in:

- ``%appdata%/.minecraft/versions/VERSION`` (Windows)
- ``~/.minecraft/versions/VERSION`` (Linux)

If you are using MultiMC, it should be in the
installation directory, or somewhere else if you are
using the AUR package.

Using the graphical interface
-----------------------------

Now that you've found the minecraft jar, you can
actually use the script. 

- Run ``pixelart-gui`` in the python prompt/shell,
  wherever you ran the ``pip`` command.
- Click *Select textures...* and pick your Minecraft
  jar file.
- Click *Select image to pixelart...* and pick
  the image you wish to convert.
- Optionally, scale the image by specifying scaling 
  values and pushing *Scale*. This will be the size
  of the image in blocks.
- Set any desired options by clicking *Options*.
  (the defaults are usually ok)
- Click *Start!* and enter the file name to save to.
- Wait until processing is complete. A block report
  will be shown when the script is done processing 
  the image. If you wish to keep this, currently 
  you must take a screenshot.
- Build your pixelart!

Using the command-line interface
--------------------------------

The ``pixelart`` package also provides an interface
usable in the system shell. Run ``pixelart -h`` to 
get the options. The same features are supported as
in the graphical version, except the block report
is saved to a file instead of being shown in the GUI.

