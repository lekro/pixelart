from PIL import Image, ImageTk
import logging
import os, re, gc
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
from threading import Thread
from processing import PixelartProcessor


PATH_FORMATS = [str, bytes, os.PathLike, int]

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

class StatusBarLoggingHandler(logging.Handler):

    def __init__(self, statusbar):
        '''Instantiate a new StatusBarLoggingHandler.

        statusbar is a tkinter label to which we can
        write text and change its color.
        '''

        super().__init__()
        self.statusbar = statusbar

    def emit(self, record):

        statusbar['text'] = record.getMessage()
        if record.level == logging.CRITICAL:
            statusbar['fg'] = 'red'
        else:
            statusbar['bg'] = 'black'


class Application(tk.Frame):

    def __init__(self, master=None, ignore=None):

        # Create options dict for arbitrary options...
        self.options = {}

        super().__init__(master)
        self.pack(fill='both', expand=1)

        self.ignore_regexes = ignore
        if self.ignore_regexes is None:
            self.ignore_regexes = []

        self.textures_ready = False
        self.input_ready = False
        self.create_widgets()
        self.logger = StatusBarLoggingHandler(self.statusbar)
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

        self.texture_button = tk.Button(self.cont,
                text='Select textures directory...',
                command=self.pick_texture_dir)
        self.texture_button.grid(row=0,column=0)

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

    def set_scaling(self, event=None):

        x = self.scaling_x.get()
        y = self.scaling_y.get()

        try:
            x = int(x)
            y = int(y)
        except:
            self.scaling_status['text'] = 'Invalid scaling values!'
            self.scaling_status['fg'] = 'red'
            return

        self.options['input_scaling'] = (x, y)

        self.scaling_status['text'] = 'Will scale to %dx%d' % (x, y)
        self.scaling_status['fg'] = 'green'


    def process_thread(self):

        # Ask for output file
        out_path = filedialog.asksaveasfilename()
        if out_path is None or os.path.isdir(out_path):
            return

        # Create processor
        processor = PixelartProcessor(self.texture_path, self.input_path,
                                      out_path,
                                      image_scaling=self.options['input_scaling'],
                                      logging_handler=self.logger,
                                      logging_level=logging.DEBUG)
        self.stop_processing = False
        self.thread = Thread(target=processor.process, daemon=True)
        self.thread.start()

    def exit_now(self):

        self.master.destroy()
        sys.exit()

    def show_block_report(self, counts):
        '''counts: map of str -> int'''

        report_pics = {}
        for name in counts.keys():
            report_pics[name] = (
                    ImageTk.PhotoImage(self.pics[name].copy()),
                    counts[name]
            )

        BlockReportDialog(self, report_pics)

    def get_status(self):
        return self.textures_ready and self.input_ready
    def update_status(self):
        if self.get_status():
            self.statusbar['text'] = 'Not ready: load textures and image!'
            self.statusbar['fg'] = 'red'
            self.start_button['state'] = 'disabled'
        else:
            self.statusbar['text'] = 'Ready to pixelart!'
            self.statusbar['fg'] = 'green'
            self.start_button['state'] = 'normal'

    def pick_texture_dir(self):

        texture_dir = None

        texture_dir = filedialog.askdirectory()
        if texture_dir is None or type(texture_dir) not in PATH_FORMATS or \
                not os.path.isdir(texture_dir):
            self.texture_status['text'] = 'Invalid texture directory!'
            self.texture_status['fg'] = 'red'
            self.textures_ready = False
            self.update_status()
            return False
        self.options['texture_path'] = texture_dir
        self.texture_status['fg'] = 'black'
        self.texture_status['text'] = texture_dir
        self.textures_ready = True
        self.update_status()
        return True

    def pick_image(self):

        input_path = None
        input_path = filedialog.askopenfilename()

        if input_path is None or type(input_path) not in PATH_FORMATS or \
                not os.path.isfile(input_path):
                
            self.input_status['text'] = 'Invalid input file!'
            self.input_status['fg'] = 'red'
            self.input_ready = False
            self.update_status()
            return False
        self.options['input_path'] = input_path
        self.input_status['fg'] = 'black'
        self.input_status['text'] = input_path
        self.input_ready = True
        self.update_status()
        return True

def main():

    root = tk.Tk()
    root.wm_title("kapurai's pixelart helper")
    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()


