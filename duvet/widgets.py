import os.path
from ttk import *

from tkreadonly import ReadOnlyCode


class CodeView(ReadOnlyCode):
    def __init__(self, *args, **kwargs):
        ReadOnlyCode.__init__(self, *args, **kwargs)

    def highlight_missing(self, missing_lines):
        for line in missing_lines:
            self.code.tag_add('current_line',
                '%s.0' % line,
                '%s.0' % (line + 1)
            )

class FileView(Treeview):
    def __init__(self, *args, **kwargs):
        # Only a single stack frame can be selected at a time.
        kwargs['selectmode'] = 'browse'
        self.normalizer = kwargs.pop('normalizer')
        self.root = kwargs.pop('root')
        Treeview.__init__(self, *args, **kwargs)

        # self['columns'] = ('coverage', 'branch_coverage')
        self['columns'] = ('coverage',)
        self.column('coverage', width=50, anchor='center')
        # self.column('branch_coverage', width=50, anchor='center')
        self.heading('#0', text='File')
        self.heading('coverage', text='Cov')
        # self.heading('branch_coverage', text='BCov')

        # Set up styles for line numbers
        self.tag_configure('bad', foreground='red')        # 0-70%
        self.tag_configure('poor', foreground='orange')    # 70-80%
        self.tag_configure('ok', foreground='blue')        # 80-90%
        self.tag_configure('good', foreground='cyan')      # 90-100%
        self.tag_configure('perfect', foreground='green')  # 100%

        self.tag_configure('directory', foreground='#999')
        self.tag_configure('non_code', foreground='gray')

        # Populate the file view
        os.path.walk(self.root, self._visitor, None)

    def _visitor(self, data, dirname, filesindir):
        prune = []
        self.insert_dirname(dirname)
        for filename in filesindir:
            if os.path.isdir(os.path.join(dirname, filename)):
                if filename in ('.git', '.hg', '_build') or filename.endswith('.egg-info'):
                    prune.append(filename)
            else:
                name, ext = os.path.splitext(filename)
                if not (ext in ('.pyc',) or filename.startswith('.')):
                    root, ext = os.path.splitext(filename)
                    if ext == '.py':
                        self.insert_filename(dirname, filename, ext)
                    else:
                        prune.append(filename)
                else:
                    prune.append(filename)

        for filename in prune:
            filesindir.remove(filename)

    def insert_dirname(self, dirname):
        "Ensure that a specific directory exists in the breakpoint tree"
        if not self.exists(dirname):
            # First, establish the index at which to insert this child.
            # Do this by getting a list of children, sorting the list by name
            # and then finding how many would sort less than the label for
            # this node.
            files = sorted(self.get_children(''), reverse=False)
            index = len([item for item in files if item > dirname])

            nodename = self._nodify(dirname)
            if nodename == self.root:
                # If this is the CWD, display at the root of the tree.
                base, path = nodename.rsplit('/', 1)
                base = ''
            else:
                base, path = nodename.rsplit('/', 1)
            # Now insert a new node at the index that was found.
            self.insert(
                base, index, nodename,
                text=path,
                open=True,
                tags=['directory']
            )

    def insert_filename(self, dirname, filename, ext):
        "Ensure that a specific filename exists in the breakpoint tree"
        if not self.exists(filename):
            # First, establish the index at which to insert this child.
            # Do this by getting a list of children, sorting the list by name
            # and then finding how many would sort less than the label for
            # this node.
            files = sorted(self.get_children(''), reverse=False)
            index = len([item for item in files if item > filename])

            # Now insert a new node at the index that was found.
            self.insert(
                self._nodify(dirname), index, self._nodify(os.path.join(dirname, filename)),
                text=self.normalizer(filename),
                open=True,
                tags=['file'] + ['code'] if ext == '.py' else ['non_code']
            )

    def _nodify(self, node):
        "Escape any problem characters in a node name"
        return node.replace('\\', '/')

    def selection_set(self, node):
        """Node names on the file tree are the filename.

        On Windows, this requires escaping, because backslashes
        in object IDs filenames cause problems with Tk.
        """
        Treeview.selection_set(self, self._nodify(node))
