# -*- coding: UTF-8 -*-
"""A module containing a visual representation of the connection

This is the "View" of the MVC world.
"""
import os
import pickle
from Tkinter import *
from tkFont import *
from ttk import *
import tkMessageBox
import webbrowser

from coverage.parser import CodeParser

from duvet import VERSION, NUM_VERSION
from duvet.widgets import nodify, CodeView, FileView


def filename_normalizer(base_path):
    """Generate a fuction that will normalize a full path into a
    display name, by removing a common prefix.

    In most situations, this will be removing the current working
    directory.
    """
    def _normalizer(filename):
        if filename.startswith(base_path) and filename[len(base_path)] == os.sep:
            return filename[len(base_path)+1:]
        else:
            return filename
    return _normalizer


class MainWindow(object):
    def __init__(self, root, options):
        '''
        -----------------------------------------------------
        | main button toolbar                               |
        -----------------------------------------------------
        |       < ma | in content area >                    |
        |            |                                      |
        | File list  | File name                            |
        |            |                                      |
        -----------------------------------------------------
        |     status bar area                               |
        -----------------------------------------------------

        '''

        # Obtain and expand the current working directory.
        base_path = os.path.abspath(os.getcwd())
        self.base_path = os.path.normcase(base_path)

        # Create a filename normalizer based on the CWD.
        self.filename_normalizer = filename_normalizer(self.base_path)

        # Set up dummy coverage data
        self.coverage_data = {'lines': {}, 'total_coverage': None}

        # Root window
        self.root = root
        self.root.title('Duvet')
        self.root.geometry('1024x768')

        # Prevent the menus from having the empty tearoff entry
        self.root.option_add('*tearOff', FALSE)
        # Catch the close button
        self.root.protocol("WM_DELETE_WINDOW", self.cmd_quit)
        # Catch the "quit" event.
        self.root.createcommand('exit', self.cmd_quit)

        # Setup the menu
        self._setup_menubar()

        # Set up the main content for the window.
        self._setup_button_toolbar()
        self._setup_main_content()
        self._setup_status_bar()

        # Now configure the weights for the root frame
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)

    ######################################################
    # Internal GUI layout methods.
    ######################################################

    def _setup_menubar(self):
        # Menubar
        self.menubar = Menu(self.root)

        # self.menu_Apple = Menu(self.menubar, name='Apple')
        # self.menubar.add_cascade(menu=self.menu_Apple)

        self.menu_file = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label='File')

        self.menu_help = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_help, label='Help')

        # self.menu_Apple.add_command(label='Test', command=self.cmd_dummy)

        # self.menu_file.add_command(label='New', command=self.cmd_dummy, accelerator="Command-N")
        # self.menu_file.add_command(label='Close', command=self.cmd_dummy)

        self.menu_help.add_command(label='Open Documentation', command=self.cmd_duvet_docs)
        self.menu_help.add_command(label='Open Duvet project page', command=self.cmd_duvet_page)
        self.menu_help.add_command(label='Open Duvet on GitHub', command=self.cmd_duvet_github)
        self.menu_help.add_command(label='Open BeeWare project page', command=self.cmd_beeware_page)

        # last step - configure the menubar
        self.root['menu'] = self.menubar

    def _setup_button_toolbar(self):
        '''
        The button toolbar runs as a horizontal area at the top of the GUI.
        It is a persistent GUI component
        '''

        # Main toolbar
        self.toolbar = Frame(self.root)
        self.toolbar.grid(column=0, row=0, sticky=(W, E))

        # Buttons on the toolbar
        self.refresh_button = Button(self.toolbar, text='Refresh', command=self.cmd_refresh)
        self.refresh_button.grid(column=0, row=0)

        # Coverage summary for currently selected file.
        self.coverage_total_summary = StringVar()
        self.coverage_total_summary_label = Label(self.toolbar, textvariable=self.coverage_total_summary, anchor=E, padding=(5, 0, 5, 0), font=('Helvetica','20'))
        self.coverage_total_summary_label.grid(column=1, row=0, sticky=(W, E))

        self.toolbar.columnconfigure(0, weight=0)
        self.toolbar.columnconfigure(1, weight=1)
        self.toolbar.rowconfigure(0, weight=0)

    def _setup_main_content(self):
        '''
        Sets up the main content area. It is a persistent GUI component
        '''

        # Main content area
        self.content = PanedWindow(self.root, orient=HORIZONTAL)
        self.content.grid(column=0, row=1, sticky=(N, S, E, W))

        # Create the tree/control area on the left frame
        self._setup_left_frame()
        self._setup_project_file_tree()
        self._setup_global_file_tree()

        # Create the output/viewer area on the right frame
        self._setup_code_area()

        # Set up weights for the left frame's content
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.content.pane(0, weight=1)
        self.content.pane(1, weight=4)

    def _setup_left_frame(self):
        '''
        The left frame mostly consists of the tree widget
        '''

        # The left-hand side frame on the main content area
        # The tabs for the two trees
        self.tree_notebook = Notebook(self.content, padding=(0, 5, 0, 5))
        self.content.add(self.tree_notebook)

    def _setup_project_file_tree(self):

        self.project_file_tree_frame = Frame(self.content)
        self.project_file_tree_frame.grid(column=0, row=0, sticky=(N, S, E, W))
        self.tree_notebook.add(self.project_file_tree_frame, text='Project')

        self.project_file_tree = FileView(self.project_file_tree_frame, normalizer=self.filename_normalizer, root=self.base_path)
        self.project_file_tree.grid(column=0, row=0, sticky=(N, S, E, W))

        # # The tree's vertical scrollbar
        self.project_file_tree_scrollbar = Scrollbar(self.project_file_tree_frame, orient=VERTICAL)
        self.project_file_tree_scrollbar.grid(column=1, row=0, sticky=(N, S))

        # # Tie the scrollbar to the text views, and the text views
        # # to each other.
        self.project_file_tree.config(yscrollcommand=self.project_file_tree_scrollbar.set)
        self.project_file_tree_scrollbar.config(command=self.project_file_tree.yview)

        # Setup weights for the "project_file_tree" tree
        self.project_file_tree_frame.columnconfigure(0, weight=1)
        self.project_file_tree_frame.columnconfigure(1, weight=0)
        self.project_file_tree_frame.rowconfigure(0, weight=1)

        # Handlers for GUI events
        self.project_file_tree.bind('<<TreeviewSelect>>', self.on_file_selected)

    def _setup_global_file_tree(self):

        self.global_file_tree_frame = Frame(self.content)
        self.global_file_tree_frame.grid(column=0, row=0, sticky=(N, S, E, W))
        self.tree_notebook.add(self.global_file_tree_frame, text='Global')

        self.global_file_tree = FileView(self.global_file_tree_frame, normalizer=self.filename_normalizer)
        self.global_file_tree.grid(column=0, row=0, sticky=(N, S, E, W))

        # # The tree's vertical scrollbar
        self.global_file_tree_scrollbar = Scrollbar(self.global_file_tree_frame, orient=VERTICAL)
        self.global_file_tree_scrollbar.grid(column=1, row=0, sticky=(N, S))

        # # Tie the scrollbar to the text views, and the text views
        # # to each other.
        self.global_file_tree.config(yscrollcommand=self.global_file_tree_scrollbar.set)
        self.global_file_tree_scrollbar.config(command=self.global_file_tree.yview)

        # Setup weights for the "global_file_tree" tree
        self.global_file_tree_frame.columnconfigure(0, weight=1)
        self.global_file_tree_frame.columnconfigure(1, weight=0)
        self.global_file_tree_frame.rowconfigure(0, weight=1)

        # Handlers for GUI events
        self.global_file_tree.bind('<<TreeviewSelect>>', self.on_file_selected)

    def _setup_code_area(self):
        self.code_frame = Frame(self.content)
        self.code_frame.grid(column=1, row=0, sticky=(N, S, E, W))

        # Label for current file
        self.current_file = StringVar()
        self.current_file_label = Label(self.code_frame, textvariable=self.current_file)
        self.current_file_label.grid(column=0, row=0, sticky=(W, E))

        # Code display area
        self.code = CodeView(self.code_frame)
        self.code.grid(column=0, row=1, sticky=(N, S, E, W))

        # Set up weights for the code frame's content
        self.code_frame.columnconfigure(0, weight=1)
        self.code_frame.rowconfigure(0, weight=0)
        self.code_frame.rowconfigure(1, weight=1)

        self.content.add(self.code_frame)

    def _setup_status_bar(self):
        # Status bar
        self.statusbar = Frame(self.root)
        self.statusbar.grid(column=0, row=2, sticky=(W, E))

        # Coverage summary for currently selected file.
        self.coverage_file_summary = StringVar()
        self.coverage_file_summary_label = Label(self.statusbar, textvariable=self.coverage_file_summary)
        self.coverage_file_summary_label.grid(column=0, row=0, sticky=(W, E))
        self.coverage_file_summary.set('No file selected')

        # Main window resize handle
        self.grip = Sizegrip(self.statusbar)
        self.grip.grid(column=1, row=0, sticky=(S, E))

        # Set up weights for status bar frame
        self.statusbar.columnconfigure(0, weight=1)
        self.statusbar.columnconfigure(1, weight=0)
        self.statusbar.rowconfigure(0, weight=0)

    ######################################################
    # Utility methods for controlling content
    ######################################################

    def show_file(self, filename, line=None, breakpoints=None):
        """Show the content of the nominated file.

        If specified, line is the current line number to highlight. If the
        line isn't currently visible, the window will be scrolled until it is.

        breakpoints is a list of line numbers that have current breakpoints.

        If refresh is true, the file will be reloaded and redrawn.
        """
        # Set the filename label for the current file
        self.current_file.set(self.filename_normalizer(filename))

        # Update the code view; this means changing the displayed file
        # if necessary, and updating the current line.
        if filename != self.code.filename:
            self.code.filename = filename

            missing = self.coverage_data['missing'].get(os.path.normcase(filename), [])
            executed = self.coverage_data['lines'].get(os.path.normcase(filename), [])

            n_executed = len(executed)
            n_missing = len(missing)

            self.code.highlight_missing(missing)

            self.coverage_file_summary.set('%s/%s lines executed' % (n_executed, n_executed + n_missing))

        self.code.line = line

    def load_coverage(self):
        "Load and display coverage data"
        # Store the old list of files that have coverage data.
        # We do this so we can identify stale data on the tree.
        old_files = set(self.coverage_data['lines'].keys())
        old_total_coverage = self.coverage_data['total_coverage']

        loaded = False
        retry = True
        while not loaded and retry:
            try:
                # Load the new coverage data
                with open('.coverage', 'rb') as datafile:
                    self.coverage_data = pickle.load(datafile)
                    self.coverage_data['missing'] = {}

                    n_total_executed = 0
                    n_total_missing = 0
                    # Update the coverage display of every file mentioned in the file.
                    for filename, executed in self.coverage_data['lines'].items():
                        filename = os.path.normcase(filename)
                        node = nodify(filename)
                        dirname, basename = os.path.split(filename)

                        # If the normalized version of the filename is the same as the
                        # filename, then the file *isn't* under the project root.
                        if filename == self.filename_normalizer(filename):
                            file_tree = self.global_file_tree
                        else:
                            file_tree = self.project_file_tree

                        # Make sure the file exists on the tree.
                        file_tree.insert_filename(dirname, basename)

                        # file_tree.set(node, 'branch_coverage', str(len(lines)))

                        # Compute the coverage percentage
                        parser = CodeParser(filename=filename)
                        statements, excluded = parser.parse_source()
                        exec1 = parser.first_lines(executed)
                        missing = sorted(set(statements) - set(exec1))
                        self.coverage_data['missing'][filename] = missing
                        n_executed = len(executed)
                        n_missing = len(missing)

                        n_total_executed = n_total_executed + n_executed
                        n_total_missing = n_total_missing + n_missing

                        # Update the column summary
                        try:
                            coverage = round(float(n_executed) / (float(n_executed) + float(n_missing)) * 100, 1)
                        except ZeroDivisionError:
                            # If no lines were executed or missing, report as 0.0% coverage.
                            coverage = 0.0
                        file_tree.set(node, 'coverage', coverage)

                        # Set the color of the tree node based on coverage
                        if coverage < 70.0:
                            file_tree.item(node, tags=['file', 'code', 'bad'])
                        elif coverage < 80.0:
                            file_tree.item(node, tags=['file', 'code', 'poor'])
                        elif coverage < 90.0:
                            file_tree.item(node, tags=['file', 'code', 'ok'])
                        elif coverage < 99.9:
                            file_tree.item(node, tags=['file', 'code', 'good'])
                        else:
                            file_tree.item(node, tags=['file', 'code', 'perfect'])

                        # We've updated the file, so we know it isn't stale.
                        try:
                            old_files.remove(filename)
                        except KeyError:
                            # File wasn't loaded before; ignore this.
                            pass

                        # Clear out any stale coverage data
                        for filename in old_files:
                            node = nodify(filename)
                            if file_tree.exists(node):
                                file_tree.set(node, 'coverage', '')
                                file_tree.item(node, tags=['file', 'code'])

                    # Compute the overall coverage
                    try:
                        total_coverage = round(float(n_total_executed) / (float(n_total_executed) + float(n_total_missing)) * 100, 1)
                    except ZeroDivisionError:
                        # If no lines were executed or missing, report as 0.0% coverage.
                        total_coverage = 0.0
                    self.coverage_data['total_coverage'] = total_coverage

                    coverage_text = u'%.1f%%' % self.coverage_data['total_coverage'],

                    # Update the text with up/down arrows to reflect change
                    if old_total_coverage is not None:
                        if total_coverage > old_total_coverage:
                            coverage_text = coverage_text + u' ⬆'
                        elif total_coverage < old_total_coverage:
                            coverage_text = coverage_text + u' ⬇'

                    self.coverage_total_summary.set(coverage_text)

                    # Set the color based on coverage level.
                    if total_coverage < 70.0:
                        self.coverage_total_summary_label.configure(foreground='red')
                    elif total_coverage < 80.0:
                        self.coverage_total_summary_label.configure(foreground='orange')
                    elif total_coverage < 90.0:
                        self.coverage_total_summary_label.configure(foreground='blue')
                    elif total_coverage < 99.9:
                        self.coverage_total_summary_label.configure(foreground='cyan')
                    else:
                        self.coverage_total_summary_label.configure(foreground='green')

                    # Refresh the file display
                    current_file = self.code._filename
                    if current_file:
                        self.code._filename = None
                        self.show_file(current_file)

                    loaded = True
            except (IOError, EOFError):
                retry = tkMessageBox.askretrycancel(
                    message="Couldn't find coverage data file. Have you generated coverage data? Is the .coverage in your current working directory",
                    title='No coverage data found'
                )
            except Exception, e:
                retry = tkMessageBox.askretrycancel(
                    message="Couldn't load coverage data -- data file may be corrupted (Error was: %s)" % e,
                    title='Problem loading coverage data'
                )

        if not loaded and not retry:
            self.root.quit()

        return loaded

    ######################################################
    # TK Main loop
    ######################################################

    def mainloop(self):
        self.root.mainloop()

    ######################################################
    # TK Command handlers
    ######################################################

    def cmd_quit(self):
        "Quit the program"
        self.root.quit()

    def cmd_refresh(self, event=None):
        "Refresh the coverage data"
        self.load_coverage()

    def cmd_duvet_page(self):
        "Show the Duvet project page"
        webbrowser.open_new('http://pybee.org/duvet')

    def cmd_duvet_github(self):
        "Show the Duvet GitHub repo"
        webbrowser.open_new('http://github.com/pybee/duvet')

    def cmd_duvet_docs(self):
        "Show the Duvet documentation"
        # If this is a formal release, show the docs for that
        # version. otherwise, just show the head docs.
        if len(NUM_VERSION) == 3:
            webbrowser.open_new('http://duvet.readthedocs.org/en/v%s/' % VERSION)
        else:
            webbrowser.open_new('http://duvet.readthedocs.org/')

    def cmd_beeware_page(self):
        "Show the BeeWare project page"
        webbrowser.open_new('http://pybee.org/')

    ######################################################
    # Handlers for GUI actions
    ######################################################

    def on_file_selected(self, event):
        "When a file is selected, highlight the file and line"
        if event.widget.selection():
            filename = event.widget.selection()[0]

            # Display the file in the code view
            if os.path.isfile(filename):
                self.show_file(filename=filename)


