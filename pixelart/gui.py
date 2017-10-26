from PIL import Image, ImageTk
import logging
import os, re, gc
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
from threading import Thread

# Import our own functions
from pixelart.processing import PixelartProcessor


PATH_FORMATS = [str, bytes, os.PathLike, int]

INTERP_DESCRIPTIONS = dict(
        nearest='take the closest pixel (worst)',
        bilinear='interpolate along lines',
        bicubic='fit to cubic curves (default)',
        lanczos='use a truncated sinc'
)

CSPACE_DESCRIPTIONS = dict(
        RGB='red, green, blue (default)',
        YCbCr='luma, chroma (color video)',
        HSV='hue, saturation, brightness'
)

class BlockReportDialog(tk.Toplevel):

    def __init__(self, parent, textures, cols=3):
        '''textures: dict of str -> (TkImage, int)'''

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.title("Block report")
        self.parent = parent
        
        body = tk.Frame(self)
        
        self.grab_set()

        self.labels = []
        for i, name in enumerate(sorted(textures.keys())):
            pic, count = textures[name]
            label = tk.Label(body,
                    image=pic,
                    text=' %dx %s' % (count, name),
                    compound='left')
            label.grid(row=int(i/cols),
                    column=int(i%cols),
                    sticky='w')
            self.labels.append(label)

        bottom_frame = tk.Frame(self)
        self.bind("<Escape>", self.done)
        self.bind("<Return>", self.done)
        self.protocol("WM_DELETE_WINDOW", self.done)

        done_button = tk.Button(bottom_frame, text='Done',
                command=self.done)
        done_button.pack(side='right')
        body.pack(padx=5, pady=5, side='top')
        bottom_frame.pack(side='bottom')


    def done(self, event=None):
        self.parent.focus_set()
        self.destroy()

class OptionsDialog(tk.Toplevel):

    def __init__(self, parent, options):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.title("Options")
        self.parent = parent

        body = tk.Frame(self)
        self.grab_set()
        self.options = options

        # Now actually create fields for settings
        # For Minkowski p-norm...
        self.norm_var = tk.StringVar()
        self.norm_var.set(str(options['p']))
        self.norm_var.trace('w', self.validate_norm)
        self.norm_label = tk.Label(body, text='Minkowski p-norm, p=')
        self.norm_input = tk.Entry(body, width=10, textvariable=self.norm_var)
        self.norm_status = tk.Label(body)
        self.norm_label.grid(row=0, column=0, sticky='w')
        self.norm_input.grid(row=0, column=1, sticky='w')
        self.norm_status.grid(row=0, column=2, sticky='w')

        # For color space...
        self.cspace_var = tk.StringVar()
        self.cspace_var.set(options['colorspace'])
        self.cspace_var.trace('w', self.validate_option_menus)
        self.cspace_label = tk.Label(body, text='Color matching space:')
        self.cspace_input = tk.OptionMenu(body, self.cspace_var, 'RGB', 'YCbCr', 'HSV')
        self.cspace_status = tk.Label(body)
        self.cspace_label.grid(row=1, column=0, sticky='w')
        self.cspace_input.grid(row=1, column=1, sticky='w')
        self.cspace_status.grid(row=1, column=2, sticky='w')

        # For interpolation
        self.interp_var = tk.StringVar()
        self.interp_var.set(options['interp'])
        self.interp_var.trace('w', self.validate_option_menus)
        self.interp_label = tk.Label(body, text='Interpolation method:')
        self.interp_input = tk.OptionMenu(body, self.interp_var, 'nearest', 'bilinear',
                                     'bicubic', 'lanczos')
        self.interp_status = tk.Label(body)
        self.interp_label.grid(row=2, column=0, sticky='w')
        self.interp_input.grid(row=2, column=1, sticky='w')
        self.interp_status.grid(row=2, column=2, sticky='w')

        self.invalid_options = set()

        bottom_frame = tk.Frame(self)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.set_button = tk.Button(bottom_frame, text='Set',
                command=self.apply_options)
        cancel_button = tk.Button(bottom_frame, text='Cancel',
                command=self.cancel)
        cancel_button.pack(side='right')
        dummy_label = tk.Label(bottom_frame)
        dummy_label.pack(side='left', fill='x', expand=1)
        self.set_button.pack(side='right')
        bottom_frame.pack(side='bottom')
        body.pack(padx=5, pady=5, side='top')

        # Validate initial values
        self.validate_norm()
        self.validate_option_menus()
        self.check_options()

    def validate_norm(self, *args):
        val = self.norm_var.get()
        try:
            val = float(val)
            self.invalid_options.discard('p')
            self.norm_status['fg'] = 'black'
            if val == 2.0:
                self.norm_status['text'] = 'Euclidean (default)'
            elif val == 1.0:
                self.norm_status['text'] = 'Manhattan'
            else:
                self.norm_status['text'] = 'p=%.1f'%val

        except:
            # We can't convert this into a float. That means it must be invalid!
            self.norm_status['fg'] = 'red'
            self.norm_status['text'] = 'Must be a number'
            self.invalid_options.add('p')
        self.check_options()

    def validate_option_menus(self, *args):

        # Interpolation
        interp = self.interp_var.get()
        self.interp_status['text'] = INTERP_DESCRIPTIONS[interp]

        # Color space
        cspace = self.cspace_var.get()
        self.cspace_status['text'] = CSPACE_DESCRIPTIONS[cspace]


    def check_options(self):
        if len(self.invalid_options) > 0:
            self.set_button['state'] = 'disabled'
        else:
            self.set_button['state'] = 'active'

    def apply_options(self, event=None):
        # Set options in parent, then leave
        self.options['colorspace'] = self.cspace_var.get()
        self.options['interp'] = self.interp_var.get()
        self.options['p'] = float(self.norm_var.get())
        self.parent.options = self.options
        self.cancel()

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()


class StatusBarLoggingHandler(logging.Handler):

    def __init__(self, statusbar):
        '''Instantiate a new StatusBarLoggingHandler.

        statusbar is a tkinter label to which we can
        write text and change its color.
        '''

        super().__init__()
        self.statusbar = statusbar

    def emit(self, record):

        self.statusbar['text'] = record.getMessage()
        if record.levelno == logging.CRITICAL:
            self.statusbar['fg'] = 'red'
        else:
            self.statusbar['fg'] = 'green'


class Application(tk.Frame):

    def __init__(self, master=None, ignore=None):

        # Create options dict for arbitrary options...
        self.options = dict(input_scaling=None,
                            p=2.0,
                            interp='bicubic',
                            colorspace='RGB')

        super().__init__(master)
        self.pack(fill='both', expand=1)

        self.ignore_regexes = ignore
        if self.ignore_regexes is None:
            self.ignore_regexes = []

        self.textures_ready = False
        self.input_ready = False
        self.create_widgets()
        self.handler = StatusBarLoggingHandler(self.statusbar)
        self.handler.setLevel(5)
        self.update_status()
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

        self.texture_frame = tk.Frame(self.cont)
        self.texture_frame.grid(row=0, column=0)

        self.texture_dir_button = tk.Button(self.texture_frame,
                text='Select textures folder...',
                command=self.pick_texture_dir)
        self.texture_dir_button.grid(row=0,column=0)

        self.texture_zip_button = tk.Button(self.texture_frame,
                text='Select textures zip/jar...',
                command=self.pick_texture_zip)
        self.texture_zip_button.grid(row=1,column=0)

        self.texture_status = tk.Label(self.cont,
                text='No textures selected!',
                fg='red')
        self.texture_status.grid(row=0,column=1)

        self.input_button = tk.Button(self.cont,
                text='Select image to pixelart...',
                command=self.pick_image)
        self.input_button.grid(row=1, column=0)

        self.input_status = tk.Label(self.cont, 
                text='No input image!',
                fg='red')
        self.input_status.grid(row=1, column=1)

        self.scaling_frame = tk.Frame(self.cont)
        self.scaling_frame.grid(row=2, column=0)

        self.scaling_x = tk.Entry(self.scaling_frame)
        self.scaling_x.bind('<Return>', self.set_scaling)
        self.scaling_x.config(width=5)
        self.scaling_x.pack(side='left')

        self.scaling_by = tk.Label(self.scaling_frame, text='x')
        self.scaling_by.pack(side='left')

        self.scaling_y = tk.Entry(self.scaling_frame)
        self.scaling_y.bind('<Return>', self.set_scaling)
        self.scaling_y.config(width=5)
        self.scaling_y.pack(side='left')

        self.scaling_button = tk.Button(self.scaling_frame, text='Scale',
                command=self.set_scaling)
        self.scaling_button.pack(side='right')

        self.scaling_status = tk.Label(self.cont, text='')
        self.scaling_status.grid(row=2, column=1)

        self.quit_button = tk.Button(self, text='Quit', fg='red',
                command=self.exit_now)
        self.quit_button.pack(side='right', padx=5, pady=5)

        # Start button
        self.start_button = tk.Button(self, text='Start!', fg='green',
                state='disabled', command=self.process_thread)
        self.start_button.pack(side='right', padx=5, pady=5)

        # Options button
        self.options_button = tk.Button(self, text='Options', fg='black',
                command=self.show_options)
        self.options_button.pack(side='right', padx=5, pady=5)

    def show_options(self):
        OptionsDialog(self, self.options)

    def set_scaling(self, event=None):

        x = self.scaling_x.get()
        y = self.scaling_y.get()

        try:
            x = int(x)
            y = int(y)
        except:
            self.scaling_status['text'] = 'Invalid scaling values!'
            self.scaling_status['fg'] = 'red'
            self.options['input_scaling'] = None
            return

        self.options['input_scaling'] = (x, y)

        self.scaling_status['text'] = 'Will scale to %dx%d' % (x, y)
        self.scaling_status['fg'] = 'green'


    def process_thread(self):

        # Ask for output file
        out_path = filedialog.asksaveasfilename()
        if out_path is None or os.path.isdir(out_path):
            return

        # Prevent the user from touching the start button
        self.start_button['state'] = 'disabled'

        # Create processor
        self.processor = PixelartProcessor(self.options['texture_path'], 
                                      self.options['input_path'],
                                      out_path,
                                      image_scaling=self.options['input_scaling'],
                                      logging_handler=self.handler,
                                      ui_caller=self)
        # We can't stop threads except by stopping the entire program.
        # That's ok for us, the user can stop the program if needed.
        self.thread = Thread(target=self.processor.process, daemon=True)
        self.thread.start()

    def done_processing(self, block_report):
        self.show_block_report(block_report)
        self.start_button['state'] = 'active'

    def exit_now(self):

        self.master.destroy()
        sys.exit()

    def show_block_report(self, counts):
        '''counts: map of str -> int'''

        report_pics = {}
        for name in counts.keys():
            report_pics[name] = (
                    ImageTk.PhotoImage(
                        self.processor.textures[name].copy()),
                    counts[name]
            )

        BlockReportDialog(self, report_pics)

    def get_status(self):
        return self.textures_ready and self.input_ready
    def update_status(self):
        if not self.get_status():
            self.statusbar['text'] = 'Not ready: load textures and image!'
            self.statusbar['fg'] = 'red'
            self.start_button['state'] = 'disabled'
        else:
            self.statusbar['text'] = 'Ready to pixelart!'
            self.statusbar['fg'] = 'green'
            self.start_button['state'] = 'normal'

    def pick_texture_dir(self):

        texture_selection = None

        texture_selection = filedialog.askdirectory(
                parent=self.master)
        if texture_selection is None or type(texture_selection) not in PATH_FORMATS:
            self.texture_status['text'] = 'Invalid texture directory!'
            self.texture_status['fg'] = 'red'
            self.textures_ready = False
            self.update_status()
            return
        self.options['texture_path'] = texture_selection
        self.texture_status['fg'] = 'green'
        self.texture_status['text'] = texture_selection
        self.textures_ready = True
        self.update_status()

    def pick_texture_zip(self):

        texture_selection = None

        texture_selection = filedialog.askopenfilename(
                parent=self.master,
                filetypes=(('zip files', '*.zip *.jar'),
                           ('all files', '*.*')))
        if texture_selection is None or type(texture_selection) not in PATH_FORMATS:
            self.texture_status['text'] = 'Invalid texture directory!'
            self.texture_status['fg'] = 'red'
            self.textures_ready = False
            self.update_status()
            return
        self.options['texture_path'] = texture_selection
        self.texture_status['fg'] = 'green'
        self.texture_status['text'] = texture_selection
        self.textures_ready = True
        self.update_status()

    def pick_image(self):

        input_path = None
        input_path = filedialog.askopenfilename()

        if input_path is None or type(input_path) not in PATH_FORMATS or \
                not os.path.isfile(input_path):
                
            self.input_status['text'] = 'Invalid input file!'
            self.input_status['fg'] = 'red'
            self.input_ready = False
            self.update_status()
            return
        self.options['input_path'] = input_path
        self.input_status['fg'] = 'green'
        self.input_status['text'] = input_path
        self.input_ready = True
        self.update_status()

def main():

    root = tk.Tk()
    root.wm_title("kapurai's pixelart helper")
    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()


