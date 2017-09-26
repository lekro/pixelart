from PIL import Image, ImageTk
import numpy as np
import os, re, gc, sys
import logging

# Try to get cKDTree from scipy.
found_ckdtree = False
try:
    from scipy.spatial import cKDTree
    found_ckdtree = True
except ImportError:
    pass

class PixelartProcessor:

    def __init__(self, textures_path, image_path, output_path,
            colorspace='RGB', interp='lanczos', minkowski=2,
            image_scaling=None, texture_dimension=None,
            logging_handler=None):

        self.textures_path = textures_path
        self.image_path = image_path
        self.output_path = output_path
        self.colorspace = colorspace
        self.interp = interp
        self.minkowski = minkowski
        self.image_scaling = image_scaling
        self.texture_dimension = texture_dimension
        
        # Set up logging.
        self.logger = logging.getLogger(__name__)
        if logging_handler is None:
            self.logger.addHandler(logging.NullHandler())
        else:
            self.logger.addHandler(logging_handler)

    def process(self):

        # Test output format
        if not is_output_path_valid():
            return False
        # Try to load textures
        if not load_textures():
            return False
        # Try to load image
        if not load_image():
            return False

        # We know now that these things are valid.
        # We also assume they won't change during the operation!

        # Filter textures (we can have the class user supply a function)
        # Find colors of all textures
        
        # Scale image
        # Perform nearest neighbor search
        # Generate pixelart image
        # Save pixelart image
        # Generate report
        # Return report



