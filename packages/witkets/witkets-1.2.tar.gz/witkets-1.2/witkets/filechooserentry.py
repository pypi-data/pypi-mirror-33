"""File chooser for open, save as and path select operations.

Example:
    >>> import tkinter as tk
    >>> import tkinter.ttk as ttk
    >>> import witkets as wtk
    >>> root = tk.Tk()
    >>> ttk.Label(root, text='Open, save as and select folder: ').pack()
    >>> chooser = wtk.FileChooserEntry(root)
    >>> chooser['format'] = [('Bitmap', '*.bmp'), ('PDF', '*.pdf')]
    >>> chooser2 = wtk.FileChooserEntry(root, buttontext='Escolher')
    >>> chooser2['action'] = wtk.FileChooserAction.SAVE
    >>> chooser2['dialogtitle'] = 'Salvar como...'
    >>> chooser3 = wtk.FileChooserEntry(root, 
    ...     action=wtk.FileChooserAction.SELECT_FOLDER)
    >>> chooser3.config(buttontext='Choisir...', 
    ...     dialogtitle='Je veux un dossier')
    >>> chooser.pack()
    >>> chooser2.pack()
    >>> chooser3.pack()
    >>> root.mainloop()
"""

from enum import Enum
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename


class FileChooserAction(Enum):
    """File chooser actions (OPEN, SAVE or SELECT_FOLDER)"""
    OPEN = 'open'
    SAVE = 'save'
    SELECT_FOLDER = 'select-folder'


class FileChooserEntry(ttk.Frame):
    """File chooser for open, save as and path select operations.
    
       The chosen path can be accessed either through the :code:`get` method or
       by a Tk StringVar via the *textvariable* option.
       
       Options:
         - textvariable --- Tk StringVar used to stock the filepath
         - buttontext --- Choose button text
         - dialogtitle --- Dialog window title
         - action --- FileChooserAction (OPEN, SAVE or SELECT_FOLDER)
         - format --- File Formats (applies only to OPEN or SAVE actions)
            * if omitted, defaults to [('All files', '*.*')]
         - All :code:`Frame` widget options
         
       Properties:
         - button --- The "Choose" button
         - entry --- The entry displaying the selected filename

    """

    def __init__(self, master, textvariable=None, buttontext='Choose...',
                 dialogtitle='Choose...', action=FileChooserAction.OPEN, **kw):
        if 'format' in kw:
            self._format = kw['format']
            kw.pop('format', False)
        else:
            self._format = [('All files', '*.*')]
        ttk.Frame.__init__(self, master, **kw)
        # Variables
        self._var_entry = tk.StringVar()
        self._var = textvariable if textvariable else tk.StringVar(value='')
        self._dialogtitle = dialogtitle
        self._action = action
        # Widgets
        self._entry = ttk.Entry(self, state='readonly')
        self._entry['state'] = 'readonly'
        self._entry['textvariable'] = self._var_entry
        self._entry['width'] = 30
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self._button = ttk.Button(self, text=buttontext)
        self._button['command'] = self._choose
        self._button.pack(side=tk.LEFT)
        self._var.trace('w', self._update)

    @property
    def button(self):
        return self._button

    @property
    def entry(self):
        return self._entry

    def get(self):
        """Gets the current selected file path"""
        return self._var.get()

    def _choose(self):
        """Choose button callback"""
        enum_ = FileChooserAction
        if self._action in (enum_.OPEN, enum_.OPEN.value):
            path = askopenfilename(parent=self, filetypes=self._format,
                                   title=self._dialogtitle)
        elif self._action in (enum_.SAVE, enum_.SAVE.value):
            path = asksaveasfilename(parent=self, filetypes=self._format,
                                     title=self._dialogtitle)
        else:
            path = askdirectory(parent=self, title=self._dialogtitle)
        self._var.set(path)
        self._update()

    def _update(self, event=None, *args):
        """Update label"""
        lbl = self._var.get()
        width = self._entry['width']
        lbl = lbl if len(lbl) < width else '...' + lbl[-(width - 4):]
        self._entry['state'] = 'normal'
        self._var_entry.set(lbl)
        self._entry['state'] = 'disabled'

    def __setitem__(self, key, val):
        if key == 'textvariable':
            self._var = val
            self._var.trace('w', self._update)
        elif key == 'buttontext':
            self._button['text'] = val
        elif key in ('format', 'dialogtitle', 'action'):
            self.__setattr__('_' + key, val)
        else:
            ttk.Frame.__setitem__(self, key, val)

    def __getitem__(self, key):
        if key == 'textvariable':
            return self._var
        elif key == 'buttontext':
            return self._button['text']
        elif key in ('format', 'dialogtitle', 'action'):
            return self.__getattr__('_' + key)
        else:
            return ttk.Frame.__getitem__(self, key)

    def config(self, **kw):
        """Tk standard config method"""
        if 'textvariable' in kw:
            self._var = kw['textvariable']
            kw.pop('textvariable', False)
        if 'buttontext' in kw:
            self._button['text'] = kw['buttontext']
            kw.pop('buttontext', False)
        base_kw = {}
        for key in kw:
            if key in ('format', 'dialogtitle', 'action'):
                self.__setattr__('_' + key, kw[key])
            else:
                base_kw[key] = kw[key]
        ttk.Frame.config(self, **base_kw)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
