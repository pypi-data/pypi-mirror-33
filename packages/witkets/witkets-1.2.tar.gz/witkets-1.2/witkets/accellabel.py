"""A label which displays an accelerator key on the right of the text.

Example:
    >>> import tkinter as tk
    >>> import witkets as wtk
    >>> root = tk.Tk()
    >>> a = wtk.AccelLabel(root, label='Copy', accel='CTRL+C')
    >>> a.pack(expand=1, fill=tk.X, padx=20, pady=20)
    >>> root.mainloop()

"""

import tkinter as tk
import tkinter.ttk as ttk


class AccelLabel(ttk.Frame):
    """A label which displays an accelerator key on the right of the text.
    
    Options:
        - master --- Parent widget
        - label --- Label text
        - accel --- Accelerator text
        - kw --- :class:`Frame` widget options

    Properties:
        - label --- Main label widget
        - accel --- Label containing the accelerator string
    """

    def __init__(self, master=None, label='', accel='', **kw):
        """Initializer"""
        ttk.Frame.__init__(self, master, **kw)
        self._label = ttk.Label(self, text=label)
        self._label['justify'] = tk.LEFT
        self._label.pack(side=tk.LEFT, padx=(0, 30), expand=1, fill=tk.X)
        self._accel = ttk.Label(self, text=accel)
        self._accel['justify'] = tk.RIGHT
        self._accel.pack(side=tk.RIGHT, fill=tk.X)

    @property
    def label(self):
        return self._label

    @property
    def accel(self):
        return self._accel


if __name__ == '__main__':
    import doctest
    doctest.testmod()