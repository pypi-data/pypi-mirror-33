#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk


class ThemedLabelFrame(ttk.LabelFrame):
    """A frame with a title label, both themed
        
       Options (all have default values):
          - title --- The text of the title label
          - labelstyle --- The style applied to the title label 
          - framestyle --- The style applied to the frame
        
       Forms of access:
          >>> from witkets import ThemedLabelFrame
          >>> frm = ThemedLabelFrame(title='Test')  # initializer
          >>> frm['title'] = 'Test 2'               # dict-like
          >>> frm.config(title = 'Test 3')          # config method
    """

    def __init__(self, master=None, title=' ',
                 labelstyle='ThemedLabelFrame.TLabel',
                 framestyle='ThemedLabelFrame.TFrame', **kw):
        self._varTitle = tk.StringVar()
        self._varTitle.set(title)
        self._lblTitle = ttk.Label(master, textvariable=self._varTitle)
        self._lblTitle['style'] = labelstyle
        ttk.LabelFrame.__init__(self, master, labelwidget=self._lblTitle, **kw)
        self['style'] = framestyle

    def __setitem__(self, key, val):
        if key == 'title':
            self._varTitle.set(val)
        elif key == 'labelstyle':
            self._lblTitle['style'] = val
        elif key == 'framestyle':
            self['style'] = val
        else:
            ttk.LabelFrame.__setitem__(self, key, val)

    def config(self, **kw):
        """Standard Tk config method"""
        for key in kw:
            if key in ('title', 'labelstyle', 'framestyle'):
                if key == 'title':
                    self._varTitle.set(val)
                elif key == 'labelstyle':
                    self._lblTitle['style'] = val
                elif key == 'framestyle':
                    self['style'] = val
            kw.pop(key, False)
        ttk.LabelFrame.config(self, **kw)


if __name__ == '__main__':
    root = tk.Tk()
    # Configuring styles
    import witkets as wtk

    s = wtk.Style()
    s.theme_use('clam')
    wtk.Style.set_default_fonts()
    s.apply_default()
    # Creating themed labelframe
    frm = wtk.ThemedLabelFrame(root)
    frm['title'] = 'Test'
    btn = ttk.Button(frm, text='tests')
    btn.pack()
    frm.pack(padx=15, pady=15)
    root.mainloop()
