import tkinter as tk
from tkinter.filedialog import askdirectory
import tkinter.scrolledtext as ScrolledText
from subprocess import call
import logging
import time
import threading
import os
import sys
import pkg_resources

from quantorxs.main import run
from quantorxs import logger as main_logger

logger = logging.getLogger(__name__)


class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


def main():
    def process_spectra(*args, **kwargs):
        results_directory = T.get("1.0", 'end-1c')
        fig_format = formats[v.get()][0].lower()
        logger.info("Data directory: %s" % directory.get())
        logger.info("Results directory: %s" %
                    os.path.join(directory.get(), results_directory))
        logger.info("Figure format: %s" % fig_format)
        logger.info("Demo mode %s" % demo.get())
        logger.info("Starting data analysis")
        try:
            run(
                spectra_folder_path=directory.get(),
                results_directory=results_directory,
                fig_format=fig_format,
                demo=demo.get())
        except Exception as e:
            logger.info("Unfortunately something went wrong.")
            logger.exception("message")
            sys.exit()
        logger.info("All done!")
        sys.exit()

    def update_directory():
        directory.set(askdirectory())

    root = tk.Tk()
    # Set the window's icon
    iconpath = pkg_resources.resource_filename(
        "quantorxs", os.path.join("data", "images", "quantorxs_logo.gif"))
    imgicon = tk.PhotoImage(file=iconpath)
    root.tk.call('wm', 'iconphoto', root._w, imgicon)
    root.title("QUANTORXS GUI")
    demo = tk.BooleanVar()
    directory = tk.StringVar("")
    results_directory_label = tk.Label(root, text="Results directory")
    results_directory_label.grid(row=1, column=0)
    T = tk.Text(root, height=1, width=30)
    T.insert(tk.END, "QUANTORXS results")
    T.grid(row=1, column=1)
    tk.Checkbutton(root, text="Demo", variable=demo).grid(row=2, sticky=tk.W)

    directory_button = tk.Button(root,
                                 text="Choose data directory",
                                 # fg="red",
                                 command=update_directory,
                                 )
    directory_button.grid(row=0, sticky=tk.W)
    directory_txt = tk.Label(root, textvariable=directory)
    directory_txt.grid(row=0, column=1)
    quit_button = tk.Button(root,
                            text="QUIT",
                            # fg="red",
                            command=quit)
    # quit_button.pack(side="left")

    def create_and_start_new_procession_thread():
        threading.Thread(target=process_spectra, args=[]).start()
    run_button = tk.Button(
        root,
        text="RUN",
        command=create_and_start_new_procession_thread)

    v = tk.IntVar()
    v.set(1)  # initializing the choice, i.e. Python

    formats = [
        ("SVG", 1),
        ("PDF", 2),
        ("PNG", 3),
    ]

    def ShowChoice():
        print(v.get())

    tk.Label(root,
             text="Choose the figures format",
             justify=tk.LEFT,
             padx=20).grid(row=3)
    i = 4
    for val, format_ in enumerate(formats):
        tk.Radiobutton(root,
                       text=format_,
                       padx=20,
                       variable=v,
                       command=ShowChoice,
                       value=val).grid(row=i)
        i += 1

    run_button.grid(row=i + 1, column=0, sticky=tk.W)
    quit_button.grid(row=i + 1, column=1, sticky=tk.W)

    # Add text widget to display logging info
    st = ScrolledText.ScrolledText(root, state='disabled')
    st.configure(font='TkFixedFont')
    st.grid(column=0, row=i + 2, sticky='w', columnspan=4)

    # Create textLogger
    text_handler = TextHandler(st)

    # Logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s')

    # Add the handler to logger
    main_logger.addHandler(text_handler)

    root.mainloop()
