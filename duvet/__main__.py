'''
This is the main entry point for the Duvet GUI.
'''
from Tkinter import *
import sys

import argparse

from duvet import VERSION
from duvet.view import MainWindow


def main():
    parser = argparse.ArgumentParser(
        description='A GUI tool to visualize coverage data.',
        version=VERSION
    )

    # parser.add_argument(
    #     'filename',
    #     metavar='script.py',
    #     help='The script to debug.'
    # )
    # parser.add_argument(
    #     'args', nargs=argparse.REMAINDER,
    #     help='Arguments to pass to the script you are debugging.'
    # )

    options = parser.parse_args()

    # Set up the root Tk context
    root = Tk()

    # Construct a window debugging the nominated program
    view = MainWindow(root, options)

    # Load initial coverage data:
    success = view.load_coverage()
    if not success:
        sys.exit(1)

    # Run the main loop
    try:
        view.mainloop()
    except KeyboardInterrupt:
        view.on_quit()

if __name__ == '__main__':
    main()
