from PIL import Image, ImageTk
import numpy as np
import os, re, gc, sys
import logging
import zipfile

# Our own functions
from pixelart.textures import NameFilter

# Try to get cKDTree from scipy.
found_ckdtree = False
try:
    from scipy.spatial import cKDTree
    found_ckdtree = True
except ImportError:
    pass

# Dictionary of interpolation strings to 
# PIL interpolation enumeration values
interpval = dict(nearest=Image.NEAREST,
                 bilinear=Image.BILINEAR,
                 bicubic=Image.BICUBIC,
                 lanczos=Image.LANCZOS)

# Texture directories within jar file to
# search...
TEXTURE_DIR_GUESSES = [
        'assets/minecraft/textures/blocks'
]

class PixelartProcessor:

    def __init__(self, textures_path, image_path, output_path,
            colorspace='RGB', interp='bicubic', minkowski=2,
            image_scaling=None, texture_dimension=(16,16),
            logging_handler=None, ui_caller=None):

        self.textures_path = textures_path
        self.image_path = image_path
        self.output_path = output_path
        self.colorspace = colorspace
        self.interp = interpval[interp]
        self.minkowski = minkowski
        self.image_scaling = image_scaling
        self.texture_dimension = texture_dimension
        self.ui_caller = ui_caller
        
        # Set up logging.
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(1)
        if logging_handler is None:
            self.logger.addHandler(logging.NullHandler())
        else:
            self.logger.addHandler(logging_handler)

    def is_output_path_valid(self):

        # Make sure the output path is not None or a directory
        if self.output_path is None or os.path.isdir(self.output_path):
            self.logger.critical("Invalid output path!")
            return False
        try:
            Image.fromarray(np.array([[[0,0,0]]], 
                            dtype='uint8')).save(self.output_path)
            return True
        except ValueError as e:
            self.logger.critical("Invalid output format! (%s)" % e)
            return False

    def load_texture(self, fi, name):
        '''Load one texture into self.textures.
        fi is a file object which can be used by PIL.
        '''

        try:
            texture = Image.open(fi)
            # And if we can't read it, just silently fail.
        except ValueError:
            return False
        except OSError:
            return False
        except IOError:
            return False

        # Now we know this is a valid texture.
        # Check to make sure its shape matches the expected shape, if any.
        if self.texture_dimension is not None:
            if not texture.size == self.texture_dimension:
                return False
        
        # Resize to 1x1 using desired interpolation method, then
        # get the only pixel in the image to find the average color.
        # We also convert to the desired color space.
        self.colors[name] = np.array(texture.resize((1,1),
            resample=self.interp).convert(self.colorspace)\
                    .getpixel((0,0)))
        self.textures[name] = texture.convert('RGB')

        return True

    def load_textures(self):

        self.colors = {}
        self.textures = {}

        if self.textures_path is None:
            self.logger.critical("Invalid texture path!")
            return False

        namefilter = NameFilter()
        
        # If this is a directory, we assume
        # all the textures are in the same directory
        if os.path.isdir(self.textures_path):
            for fi in os.listdir(self.textures_path):

                name, ext = os.path.splitext(fi)
                if not namefilter.filter_file(name, ext):
                    continue
                with open(os.path.join(self.textures_path, fi),
                          mode='rb') as f:
                    self.load_texture(f, name)

        # If it's a file, try to open it as an archive.
        elif os.path.isfile(self.textures_path):
            # Guess this is a zip (jar) file
            head, tail = os.path.split(self.textures_path)
            name, ext = os.path.splitext(tail)

            # First check if it's a zip file
            if zipfile.is_zipfile(self.textures_path):

                # Now we're pretty sure this is a zip file.
                # We can guess the location of the textures
                with zipfile.ZipFile(self.textures_path, 'r') as fi:

                    for info in fi.infolist():
                        
                        # If it's a directory, we don't really want it...
                        if info.is_dir():
                            continue

                        # If it's not in our directory guesses, skip...
                        # We don't want to include items and entities.
                        ahead, atail = os.path.split(info.filename)
                        if ahead not in TEXTURE_DIR_GUESSES:
                            continue

                        # Filter textures using the NameFilter, just
                        # like with a normal file...
                        aname, aext = os.path.splitext(atail)
                        if not namefilter.filter_file(aname, aext):
                            continue

                        # Now that we're done with that,
                        # actually try to open the file.
                        with fi.open(info, mode='r') as texture_file:
                            # Add this as a texture
                            self.load_texture(texture_file, aname)

            # And our contingency plan is to fail!
            else:
                self.logger.critical("Unknown archive format %s!" % ext)
                return False


        if len(self.colors) == 0:
            self.logger.critical("No loadable textures found in %s!" % self.textures_path)
            return False

        self.logger.info("Loaded %d textures!" % len(self.colors))
        return True

    def load_image(self):

        self.logger.info("Loading input image %s" % self.image_path)

        if self.image_path is None or not os.path.isfile(self.image_path):
            self.logger.critical("Invalid image path!")
            return False

        self.image = None
        try:
            self.image = Image.open(self.image_path)
        except IOError as e:
            self.logger.critical("Couldn't load image! (%s)" % e)
            return False
        except ValueError as e:
            self.logger.critical("Unknown image format! (%s)" % e)
            return False

        # Scale if necessary
        if self.image_scaling is not None:
            self.logger.debug("Scaling input to %dx%d..." %
                    self.image_scaling)
            self.image = self.image.resize(self.image_scaling,
                    resample=self.interp).convert(self.colorspace)

        return True

    def find_nearest_neighbors(self):

        self.logger.info("Finding nearest neighbors...")

        # Find nearest neighbors here.
        vals = np.array(list(self.colors.values()))

        # Make a cKDTree if we have scipy
        if found_ckdtree:
            self.logger.debug("We have a cKDTree - this "
                              "will be quick!")
            kdtree = cKDTree(vals)
        else:
            self.logger.debug("No cKDTree found - this "
                              "step may take some time...")
            kdtree = None
        image = np.array(self.image)

        rows = image.shape[0]
        
        # We will put neighbors here when we find them
        # These will be the indices to the keys and values...
        neighbors = np.zeros(image.shape[0:2], dtype='intp')

        for i, row in enumerate(image):

            self.logger.log(5, 'Matching nearest neighbors... '
                               '(%d of %d complete)' % (i+1, rows))

            # If we have the kdtree, use it of course
            if kdtree:
                _, neigh = kdtree.query(row, k=1, p=self.minkowski)
            else:
                # Since we don't have the kdtree, we have to
                # brute force find the nearest neighbors...
                # But we don't have to actually find the norms.
                # For a bit of optimization, we don't do the
                # square root at the end.
                neigh = np.zeros(row.shape[0])
                for j, px in enumerate(row):
                    norm_p = np.zeros(vals.shape[0])
                    # TODO maybe we can use a map() here for speed
                    for k, cl in enumerate(vals):
                        norm_p[k] = (cl[0]-px[0])**self.minkowski
                        norm_p[k] += (cl[1]-px[1])**self.minkowski
                        norm_p[k] += (cl[2]-px[2])**self.minkowski
                    neigh[j] = np.argmin(norm_p)

            neighbors[i] = neigh.astype('intp')

        self.neighbors = neighbors
        return neighbors

    def generate_pixelart(self):

        self.logger.info("Creating output image...")

        # Creating the final image may take a lot of RAM!
        w, h = self.texture_dimension
        keys = np.array(list(self.colors.keys()))
        image = np.array(self.image)
        iw = image.shape[0]
        ih = image.shape[1]
        self.logger.debug("Allocating space for a %dx%d image..."\
                % (w*iw, h*ih))
        try:
            final = np.zeros((w*iw, h*ih, 3))
        except MemoryError:
            self.logger.critical("Ran out of memory while creating "
                                  "final image!")
            return False
        self.logger.debug("Pasting textures into final image...")
        
        for i, row in enumerate(keys[self.neighbors]):
            for j, key in enumerate(row):
                final[i*w:i*w+w, j*h:j*h+h] = np.array(self.textures[key].copy())
        final = final.astype('uint8')
        self.output = Image.fromarray(final)
        return self.output

    def generate_report(self):

        names = np.array(list(self.colors.keys()))
        names = names[self.neighbors]
        unique, counts = np.unique(names, return_counts=True)
        return dict(zip(unique, counts))

    def process(self):

        # Test output format
        if not self.is_output_path_valid():
            return False
        # Try to load textures (and filter)
        if not self.load_textures():
            return False
        # Try to load image (and scale)
        if not self.load_image():
            return False

        # We know now that these things are valid.
        # We also assume they won't change during the operation!
        
        # Perform nearest neighbor search
        self.find_nearest_neighbors()
        # Generate pixelart image
        if not self.generate_pixelart():
            return False
        # Save pixelart image
        self.output.save(self.output_path)

        self.logger.debug("Done!")
        # Generate report
        # and send it back to the caller. Not sure if this
        # is the right way of doing things.
        if self.ui_caller is not None:
            self.ui_caller.done_processing(self.generate_report())

        



