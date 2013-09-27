import os.path
from ttk import *

from tkreadonly import ReadOnlyCode


def nodify(node):
    "Escape any problem characters in a node name"
    return node.replace('\\', '/')


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
        self.root = kwargs.pop('root', None)
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
        if self.root:
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
        if not self.exists(nodify(dirname)):
            nodename = nodify(dirname)
            parent, child = os.path.split(dirname)
            if self.root:
                # We're displaying a subtree.
                if nodename == nodify(self.root):
                    # If this is the CWD, display at the root of the tree.
                    path = nodify(child)
                    base = ''
                else:
                    self.insert_dirname(parent)
                    base = nodify(parent)
                    path = nodify(child)
            else:
                # Check for the "root" on both unix and Windows
                if child == '':
                    path = nodify(parent)
                    base = ''
                else:
                    self.insert_dirname(parent)
                    base = nodify(parent)
                    path = nodify(child)

            # Establish the index at which to insert this child.
            # Do this by getting a list of children, sorting the list by name
            # and then finding how many would sort less than the label for
            # this node.
            files = sorted(self.get_children(base), reverse=False)
            index = len([item for item in files if item < nodify(dirname)])

            # Now insert a new node at the index that was found.
            self.insert(
                base, index, nodename,
                text=path,
                open=True,
                tags=['directory']
            )

    def insert_filename(self, dirname, filename, ext='.py'):
        "Ensure that a specific filename exists in the breakpoint tree"
        full_filename = os.path.join(dirname, filename)
        if not self.exists(nodify(full_filename)):
            # If self.root is defined, we're only displaying files under that root.
            # If the normalized version of the filename is the same as the
            # filename, then the file *isn't* under the root. Don't bother trying
            # to add the file.
            # Alternatively, if self.root is *not* defined, *only* add the file if
            # if isn't under the project root.
            if full_filename == self.normalizer(full_filename):
                if self.root:
                    return
                self.insert_dirname(dirname)
            else:
                if self.root is None:
                    return

            # Establish the index at which to insert this child.
            # Do this by getting a list of children, sorting the list by name
            # and then finding how many would sort less than the label for
            # this node.
            files = sorted(self.get_children(nodify(dirname)), reverse=False)
            index = len([item for item in files if item < nodify(full_filename)])
            # Now insert a new node at the index that was found.
            self.insert(
                nodify(dirname), index, nodify(os.path.join(dirname, filename)),
                text=filename,
                open=True,
                tags=['file'] + ['code'] if ext == '.py' else ['non_code']
            )


    def selection_set(self, node):
        """Node names on the file tree are the filename.

        On Windows, this requires escaping, because backslashes
        in object IDs filenames cause problems with Tk.
        """
        Treeview.selection_set(self, nodify(node))
