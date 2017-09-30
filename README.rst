***************
pixelart-helper
***************

A simple pixel art helper for Minecraft, written in Python,
with a simple ``tkinter`` GUI.

==========================
Installation instructions:
==========================

-----
Linux
-----

- Install Python 3
- Install ``numpy`` and ``Pillow``. 
- Use ``pip`` to install, e.g. ``pip install pixelart``
- Use the command ``pixelart`` to launch the GUI.

-------
Windows
-------

- Install Python 3 with miniconda: https://conda.io/miniconda.html
- Go to the start menu and open the *Anaconda Prompt*
- Install ``numpy`` and ``Pillow``, by executing the command
  ``conda install numpy pillow``
- Use ``pip`` to install, with the command ``pip install pixelart``
- To use the script, use the command ``pixelart``

=====
Usage
=====

* Before using ``pixelart``, make sure you have two things:

  - **Textures**: You can open your minecraft jar or texturepack
    zip directly, or you can extract the textures and show 
    ``pixelart-helper`` where they are.

  - **Input image**: This is the image you want to convert. It should
    be in some format ``Pillow`` understands.

* To use the graphical user interface, use the command ``pixelart-gui``.
  To pass arguments like any other shell program, use the command
  ``pixelart``. If you require help with the latter, use ``pixelart -h``.

===============================
Getting your Minecraft textures
===============================

* Obtain a copy of the latest minecraft jar and unzip it in a new
  directory (it will also give you a bunch of junk you don't really need)

  - On Windows, this should be inside ``%appdata%/.minecraft/versions``.

  - On Linux, I'm guessing it's under ``~/.minecraft/versions``.

  - If using MultiMC, it may be inside the MultiMC versions directory
    instead.
* Inside the extracted data, you should find the actual minecraft textures
  in ``assets/minecraft/textures/blocks/``. You can select this directory
  in the GUI.

=============
Dependencies:
=============

- Python 3
- Tk
- numpy
- pillow
- scipy *(optional, for faster nearest neighbors matching)*
