from PIL import Image
import numpy as np
from scipy.spatial import KDTree
import os, re, gc
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
from threading import Thread

NO_TEXTURES_MESSAGE = 'No textures loaded!'
NO_INPUT_MESSAGE = 'No input image!'
PIL_FORMATS = (("PIL images", 
    "*.png;*.jpg;*.jpeg;*.bmp;*.eps;*.gif;*.ico;*.pcx;*.tiff;*.psd"),)
IGNORE_REGEX_SOURCES = ['sapling.*', 'wheat_stage.*', '.*grass.*', 'water.*', 'redstone_dust.*', 'repeater.*',
                 'dragon_egg', 'cake.*', 'fern', '.*_stage_.*', 'flower.*', 'shulker.*', 'door.*',
                 'enchanting.*', 'double_plant.*', '.*_layer_.*', 'deadbush', 'vine', 'hopper.*', 'portal',
                 'anvil.*', 'daylight.*', 'comparator.*', 'trip.*', 'farmland.*', 'grass_side', 'mycelium_side',
                 'podzol_side', 'leaves.*', 'reeds', '.*pane.*', '.*_stem.*', 'endframe_.*', 'mushroom_red',
                 'mushroom_brown', 'web', 'tnt_top', 'cactus.*', 'lava.*', 'chorus_plant', '.*torch_.*', 'chorus_.*',
                 'pumpkin_top', 'pumpkin_bottom', 'lever', 'rail_.*', 'jukebox_top', 'trapdoor', 'stone_slab_top',
                 'ladder', 'iron_bars', 'brewing_stand', 'crafting_table_.*', 'bookshelf', 'glazed_terracotta_brown',
                 'redstone_lamp_on', 'furnace_front_on', 'quartz_ore', 'cauldron.*', 'debug.*', 'glass', 'end_rod',
                 'structure_block.*', 'mycelium.*', 'grass.*', 'itemframe.*', 'furnace_top',
                 'iron_trapdoor']
PATH_FORMATS = [str, bytes, os.PathLike, int]

class Application(tk.Frame):

    def __init__(self, master=None):

        super().__init__(master)
        self.pack(fill='both', expand=1)

        self.texture_dir = None
        self.image_path = None
        self.create_widgets()
        self.set_status()
        self.thread = None

    def create_widgets(self):

        # First create a description label

        # Status bar
        self.statusbar = tk.Label(self, relief='sunken', text='Not ready',
                anchor='w', fg='red')
        self.statusbar.pack(side='bottom', fill='x', expand=1)

        # Center buttons and part where things happen
        self.cont = tk.Frame(self)
        self.cont.pack(side='top', fill='both', expand=1)

        self.texture_button = tk.Button(self.cont,
                text='Select textures directory...',
                command=self.pick_texture_dir)
        self.texture_button.grid(row=0,column=0)

        self.texture_status = tk.Label(self.cont,
                text=NO_TEXTURES_MESSAGE,
                fg='red')
        self.texture_status.grid(row=0,column=1)

        self.input_button = tk.Button(self.cont,
                text='Select image to pixelart...',
                command=self.pick_image)
        self.input_button.grid(row=1, column=0)

        self.input_status = tk.Label(self.cont, 
                text=NO_INPUT_MESSAGE,
                fg='red')
        self.input_status.grid(row=1, column=1)

        self.quit_button = tk.Button(self, text='Quit', fg='red',
                command=self.exit_now)
        self.quit_button.pack(side='right', padx=5, pady=5)

        # Start button
        self.start_button = tk.Button(self, text='Start!', fg='green',
                state='disabled', command=self.process_thread)
        self.start_button.pack(side='right', padx=5, pady=5)

    def process_thread(self):

        self.stop_processing = False
        self.thread = Thread(target=self.process, daemon=True)
        self.thread.start()

    def exit_now(self):

        root.destroy()
        sys.exit()

    def process(self):

        out_path = filedialog.asksaveasfilename()
        if out_path is None or not os.path.isfile(out_path):
            return

        self.statusbar['fg'] = 'black'
        self.statusbar['text'] = 'Creating KDTree for nearest neighbors matching...'

        vals = np.array(list(self.colors.values()))
        keys = np.array(list(self.colors.keys()))

        kdtree = KDTree(vals)
        image = np.array(self.image)[...,0:3]

        rows = image.shape[0]

        neighbors = np.zeros(image.shape[0:2])
        for i, row in enumerate(image):
            _, neigh = kdtree.query(row, k=1)
            neighbors[i] = neigh.astype('uint8')
            self.statusbar['text'] = 'Finding nearest neighbors (%d of %d complete)...' % (i+1, rows)

            if self.stop_processing is True:
                return

        self.statusbar['text'] = 'Creating final image... this may take a lot of RAM.'
        neighbors = neighbors.astype('uint8')

        w = self.texture_width
        h = self.texture_height
        final = np.zeros((image.shape[0] * w, image.shape[1] * h, 3))

        for i, row in enumerate(keys[neighbors]):
            for j, key in enumerate(row):
                final[i*w:i*w+w, j*h:j*h+h] = np.array(self.pics[key])
        final = final.astype('uint8')
        output = Image.fromarray(final)
        output.save(out_path)

        self.statusbar['text'] = 'Image generation successful!'

    def get_status(self):
        return self.texture_dir is None or self.image_path is None
    def set_status(self):
        if self.get_status():
            self.statusbar['text'] = 'Not ready: load textures and image!'
            self.statusbar['fg'] = 'red'
            self.start_button['state'] = 'disabled'
        else:
            self.statusbar['text'] = 'Ready to pixelart!'
            self.statusbar['fg'] = 'green'
            self.start_button['state'] = 'normal'

    def pick_texture_dir(self):

        self.texture_dir = None

        self.texture_dir = filedialog.askdirectory()
        if self.texture_dir is None or type(self.texture_dir) not in PATH_FORMATS or \
                not os.path.isdir(self.texture_dir):
            self.texture_dir = None
            self.set_status()
            return

        self.colors = {}
        self.pics = {}
        self.texture_width = None
        self.texture_height = None

        for fi in os.listdir(self.texture_dir):

            # Minecraft textures are png files
            if not fi.endswith(".png"):
                continue
            name = fi[:-4]

            # Ignore textures which match any ignore regexes
            skip = False
            for regex in ignore_regexes:
                if regex.match(name) is not None: 
                    skip = True
                    break
            if skip:
                continue

            # Now we can open the image
            p = Image.open(os.path.join(self.texture_dir, fi))\
                    .convert('RGB')

            # Require regular texture dimensions
            if self.texture_width is None:
                self.texture_width = p.width
                self.texture_height = p.height
            elif p.width is not self.texture_width:
                continue
            elif p.height is not self.texture_height:
                continue

            # Resize the image to 1x1 using bicubic interpolation
            # Then get the only pixel in the image, only RGB
            # (ignoring alpha)
            self.colors[name] = np.array(p.resize((1, 1),
                resample=Image.BICUBIC).getpixel((0, 0)))[0:3]
            self.pics[name] = p

        if len(self.colors) > 0:
            self.texture_status['text'] = '%d %dx%d textures loaded' % \
                    (len(self.colors), self.texture_width, 
                            self.texture_height)
            self.texture_status['fg'] = 'green'
        else:
            self.texture_status['text'] = NO_TEXTURES_MESSAGE
            self.texture_status['fg'] = 'red'
            self.texture_dir = None
            self.set_status()

        self.set_status()

    def pick_image(self):

        self.image_path = None
        self.image_path = filedialog.askopenfilename()

        if self.image_path is None or type(self.image_path) not in PATH_FORMATS or \
                not os.path.isfile(self.image_path):
                
            self.image_failure()
            return

        self.image = None
        try:
            self.image = Image.open(self.image_path)
        except IOError:
            self.image_failure(message="Couldn't load image!")
            return

        self.input_status['text'] = "Loaded %sx%s image" %\
                (self.image.width, self.image.height)
        self.input_status['fg'] = 'green'

        self.set_status()

    def image_failure(self, message=None):
        
        if message is None:
            self.input_status['text'] = NO_INPUT_MESSAGE
        else:
            self.input_status['text'] = message
        self.input_status['fg'] = 'red'
        self.image_path = None

        self.set_status()

def main():

    ignore_regexes = [re.compile(x) for x in IGNORE_REGEX_SOURCES]
    root = tk.Tk()
    root.wm_title("kapurai's pixelart helper")
    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()


