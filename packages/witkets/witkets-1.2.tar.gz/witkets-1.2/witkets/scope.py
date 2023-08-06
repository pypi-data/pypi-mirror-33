#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *
from witkets import Plot


# TODO: Add minimum and maximum scale

class Scope(Frame):
    """Single-channel Signal Scope
       
       Convenient way to create a plot with both scrollbars and reasonable
       default options, if plot is going to be used as an oscilloscope.
       
       Options:
         - plot_width, plot_height --- Plot dimensions
         - All :code:`Frame` widget options
       
       Attributes:
         - plot --- The associated :code:`witkets.plot.Plot` object
         - hscroll and vscroll --- Scrollbar objects
    """

    def __init__(self, master=None, plot_width=330, plot_height=220, **kw):
        plot_keys = {}
        for key in kw:
            if key.startswith('plot_'):
                plotkey = key.replace('plot_', '')
                plot_keys[plotkey] = kw[plotkey]
                kw.pop(key, False)
        Frame.__init__(self, master, **kw)
        self.plot = Plot(self, width=plot_width, height=plot_height, **plot_keys)
        self._style = None  # style attribute isn't stored properly
        # Plot and scrollbars
        self.hscroll = Scrollbar(self, orient='horizontal')
        self.hscroll.config(command=self.plot.xview)
        self.vscroll = Scrollbar(self, orient='vertical')
        self.vscroll.config(command=self.plot.yview)
        self.plot.config(xscrollcommand=self.hscroll.set)
        self.plot.config(yscrollcommand=self.vscroll.set)
        self.plot.redraw()
        self.vscroll.grid(row=0, column=0, sticky='ns')
        self.plot.grid(row=0, column=1, sticky='nsew')
        self.hscroll.grid(row=1, column=1, sticky='we')
        # Mouse-wheel zoom and pan
        self.plot.bind("<MouseWheel>", self._on_mouse_wheel)
        self.plot.bind("<Button-4>", self._on_mouse_wheel)
        self.plot.bind("<Button-5>", self._on_mouse_wheel)

    def __setitem__(self, key, val):
        if key.startswith('plot_'):
            plotkey = key.replace('plot_', '')
            self.plot[plotkey] = val
            self.plot.redraw()
        elif key == 'style':
            self._style = val
            Frame.__setitem__(self, 'style', val)
        else:
            Frame.__setitem__(self, key, val)

    def __getitem__(self, key):
        if key.startswith('plot_'):
            plotkey = key.replace('plot_', '')
            return self.plot[plotkey]
        elif key == 'style':
            return self._style
        else:
            Frame.__getitem__(self, key)

    def config(self, **kw):
        """Tk standard config method"""
        base_kw = {}
        for key in kw:
            if key.startswith('plot_'):
                plotkey = key.replace('plot_', '')
                self.plot[plotkey] = kw[key]
            else:
                base_kw[key] = kw[key]
        Frame.config(self, **base_kw)

    def _on_mouse_wheel(self, event):
        """Mouse wheel events"""
        shift = event.state & 1
        control = event.state & 4
        alt = event.state & 8
        # show event values!! use key modifiers properly
        # 'delta', 'height', 'keycode', 'keysym', 'keysym_num', 'num',
        # 'send_event', 'serial', 'state', 'time', 'type', 'widget', 'width',
        # 'x', 'x_root', 'y', 'y_root'
        if event.delta != 0:  # Windows
            pass
        elif event.num == 4:  # Linux
            if control and (not shift) and (not alt):
                self.plot['xscale'] *= 1.2
                self.plot['yscale'] *= 1.2
            elif shift and (not control) and (not alt):
                self.plot.xview('scroll', -1, 'units')
            elif alt and (not control) and (not shift):
                self.plot['yoffset'] -= 10
            elif control and shift and (not alt):
                self.plot['yscale'] *= 1.2
            else:
                self.plot.yview('scroll', -1, 'units')
        elif event.num == 5:
            if control and (not shift) and (not alt):
                self.plot['xscale'] /= 1.2
                self.plot['yscale'] /= 1.2
            elif shift and (not control) and (not alt):
                self.plot.xview('scroll', 1, 'units')
            elif alt and (not control) and (not shift):
                self.plot['yoffset'] += 10
            elif control and shift and (not alt):
                self.plot['yscale'] /= 1.2
            else:
                self.plot.yview('scroll', 1, 'units')
        self.plot.redraw()


if __name__ == '__main__':
    root = Tk()
    scope = Scope(root, plot_width=500)
    scope['plot_width'] = 400
    scope.pack()
    root.mainloop()
