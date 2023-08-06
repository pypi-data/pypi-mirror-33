"""Container capable of hiding its child.

Example:
    >>> import tkinter as tk
    >>> import tkinter.ttk as ttk
    >>> import witkets as wtk
    >>> root = tk.Tk()
    >>> expander = wtk.Expander(root, text='Test')
    >>> label = ttk.Label(expander.frame, text='Expanded content')
    >>> label.pack()
    >>> expander.pack()
    >>> root.mainloop()

XML Example:

    >>> import tkinter as tk
    >>> import witkets as wtk
    >>> UI = '''
    ... <root>
    ...     <expander wid='expander1' text='Test 2 (XML)'>
    ...         <label wid='lbl1' text='Contents' />
    ...         <geometry>
    ...             <pack for='lbl1' />
    ...         </geometry>
    ...     </expander>
    ...     <geometry>
    ...         <pack for='expander1' />
    ...     </geometry>
    ... </root>
    ... '''
    >>> root = tk.Tk()
    >>> builder = wtk.TkBuilder(root)
    >>> builder.build_from_string(UI)
    >>> root.mainloop()

"""

import tkinter as tk
import tkinter.ttk as ttk
import pkgutil as pkg


class Expander(ttk.Frame):
    """Container capable of hiding its child

       Options:
           - text --- The text to be shown in the button
           - expanded --- Whether the child should be shown (defaults to True)

       Property:
           - button --- The inner Button widget
           - frame --- The inner Frame widget

       Forms of access:
           >>> from witkets import Expander
           >>> expander = Expander(text='Advanced Options')
           >>> expander['expanded'] = False
           >>> expander.config(text='Basic Options')

        XML Approach:
        
        .. code-block:: xml
        
            <root>
                <expander wid='expander1' text='Expand or fold'>
                    <label wid='lbl1' text='Contents' />
                    <geometry>
                        <pack for='lbl1' />
                    </geometry>
                </expander>
                <geometry>
                    <pack for='expander1' />
                </geometry>
            </root>
    """

    def __init__(self, master=None, text='', expanded=True, **kw):
        """Constructor
           - text --- Label text
           - content --- The widget to be expanded or collapsed
           - expanded --- Whether the child should be shown
        """
        tk.Frame.__init__(self, master, **kw)
        arrow_right_data = pkg.get_data('witkets', 'data/xbm/arrow-right-16.xbm')
        self._arrow_right = tk.BitmapImage(data=arrow_right_data)
        arrow_down_data = pkg.get_data('witkets', 'data/xbm/arrow-down-16.xbm')
        self._arrow_down = tk.BitmapImage(data=arrow_down_data)
        self._button = ttk.Button(self, text=text, image=self._arrow_down, 
                                  compound=tk.LEFT)
        self._button['style'] = 'Expander.TButton'
        self._button.pack(fill=tk.X)
        self._button['command'] = self._on_toggle
        self._frame = ttk.Frame(self)
        self._expanded = expanded
        if expanded:
            self._button['image'] = self._arrow_down
            self._frame.pack()
        else:
            self._button['image'] = self._arrow_right

    def _update(self):
        if self._expanded:
            self._button['image'] = self._arrow_down
            self._frame.pack()
        else:
            self._button['image'] = self._arrow_right
            self._frame.pack_forget()

    def _on_toggle(self):
        self._expanded = not self._expanded
        self._update()

    @property
    def button(self):
        return self._button

    @property
    def frame(self):
        return self._frame

    def __setitem__(self, key, val):
        if key == 'text':
            self._button['text'] = val
        elif key == 'expanded':
            self._expanded = val
            self._update()
        else:
            Frame.__setitem__(self, key, val)

    def __getitem__(self, key):
        if key == 'text':
            return self._button['text']
        elif key == 'expanded':
            return self.expanded
        return Frame.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        for key in ('text', 'expanded'):
            if key in kw:
                self.__setitem__(key, kw[key])
                kw.pop(key, False)
        ttk.Frame.config(self, **kw)
        self._update()

if __name__ == '__main__':
    import doctest
    doctest.testmod()