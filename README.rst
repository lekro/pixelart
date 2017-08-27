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
- Install ``numpy``, ``scipy``, and ``Pillow``. 
- Use ``pip`` to install, e.g. ``pip install pixelart-helper``
- Use the command ``pixelart`` to launch the GUI.

-------
Windows
-------

- Install Python 3 with miniconda: https://conda.io/miniconda.html
- Go to the start menu and open the *Anaconda Prompt*
- Install ``numpy``, ``scipy``, and ``Pillow``, by executing the command
  ``conda install numpy scipy pillow``
- Use ``pip`` to install, with the command ``pip install pixelart-helper``
- To use the script, use the command ``pixelart``

====
Getting your Minecraft textures
====

- Obtain a copy of the latest minecraft jar and unzip it in a new
  directory (it will also give you a bunch of junk you don't really need)
- Inside the extracted data, you should find the actual minecraft textures
  in ``assets/minecraft/textures/blocks/``. You can select this directory
  in the GUI.

=============
Dependencies:
=============

- Python 3
- Tk
- numpy
- scipy
- pillow
