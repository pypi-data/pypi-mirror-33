#!/usr/bin/env python3

import sys
import ast
import xml.etree.ElementTree as ElementTree
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
from copy import copy
import witkets as wtk
from witkets.helpers.special_handlers import special_handlers

_widget_classes = [
    # TK Base and TTK Overriden Widgets
    ttk.Button, tk.Canvas, ttk.Checkbutton, ttk.Entry, ttk.Frame, ttk.Label,
    ttk.LabelFrame, tk.Listbox, tk.Menu, tk.Message, ttk.Menubutton,
    ttk.PanedWindow, ttk.Radiobutton, ttk.Scale, ttk.Scrollbar,
    tk.scrolledtext.ScrolledText, tk.Spinbox, tk.Text,
    # TTK Exclusive
    ttk.Combobox, ttk.Notebook, ttk.Progressbar, ttk.Separator, ttk.Sizegrip,
    ttk.Treeview,
    # Witkets
    wtk.AccelLabel, wtk.CardLayout, wtk.ColorButton, wtk.Expander,
    wtk.FileChooserEntry, wtk.Gauge, wtk.ImageButton, wtk.ImageMap, wtk.LED,
    wtk.LEDBar, wtk.LinkButton, wtk.LogicSwitch, wtk.NumericLabel, wtk.Plot,
    wtk.Scope, wtk.PyText, wtk.PyScrolledText, wtk.Ribbon, wtk.Spinner,
    wtk.Spin, wtk.Tank, wtk.ThemedLabelFrame,
    wtk.Thermometer, wtk.TimeEntry, wtk.Toolbar, wtk.ToggleButton
]

class TkBuilder:
    def __init__(self, master):
        """Initializer
        
            :param master:
                Tk root container where interface is going to be built
        """
        self._tree = None
        self._root = None
        self._master = master
        self.nodes = {}
        self.tkstyle = None
        self.theme = None
        self._tag2tk = {cls.__name__.lower(): cls for cls in _widget_classes}
        self._containers = ['root', 'frame', 'labelframe', 'expander',
                            'themedlabelframe', 'cardlayout', 'notebook']
        self.add_tag('tkbutton', tk.Button)

    def add_tag(self, tag, cls, container=False):
        """Maps a tag to a class
        
            :param tag:
                XML tag name
            :type tag:
                str
            :param cls:
                Class to be instantiated when *tag* is found
            :type cls:
                Any widget class
            :param container:
                Whether this Tk widget is a container of other widgets
        """
        self._tag2tk[tag] = cls
        if container:
            self._containers.append(tag)

    def _handle_widget(self, widget_node, parent):
        """Handles individual widgets tags"""
        try:
            wid = widget_node.attrib.pop('wid')
        except KeyError:
            print('Required key "wid" not found in %s' % widget_node.tag, sys.stderr)
            return
        # Creating widget        
        tk_class = self._tag2tk[widget_node.tag]
        if parent == self._root:
            parent_widget = self._master
        else:
            parent_id = parent.attrib['wid']
            parent_widget = self.nodes[parent_id]
        # Expander container
        if parent.tag == 'expander':
            parent_widget = parent_widget.frame
        self.nodes[wid] = tk_class(parent_widget)
        #print(wid, parent, tk_class, parent_widget)
        # Mapping attributes
        self._handle_attributes(self.nodes[wid], widget_node.tag,
                                widget_node.attrib)

    def _handle_attributes(self, widget, tagname, attribs):
        """Handles attributes, except TkBuilder related"""
        attribs = self._get_attribs_values(widget, tagname, attribs)
        for key, val in attribs.items():
            if key.startswith('{editor-}'):  # skipping editor namespace
                continue
            try:
                widget[key] = val  # @FIXME fails for Bool (still?)
            except KeyError:
                print('[warning] Invalid key "%s"' % key)

    @staticmethod
    def _get_attribs_values(widget, tagname, attribs):
        cls = widget.__class__
        if tagname in special_handlers:
            handlers = special_handlers[tagname]
        elif cls in special_handlers:
            handlers = special_handlers[cls]
        else:
            return attribs # no special attributes for this widget
        for a in attribs:
            if a in handlers:
                attribs[a] = handlers[a](attribs[a])
        return attribs

    def _handle_container(self, container, parent):
        """Handles containers (<root>, <frame> and user-defined containers)"""
        attribs = copy(container.attrib)
        if container.tag != 'root':
            if container.tag not in self._tag2tk:
                print('Tag not supported: %s' % container.tag, file=sys.stderr)
                return
            if 'wid' not in attribs:
                print('Required key "wid" not found in %s' % container.tag,
                      file=sys.stderr)
                return
            wid = attribs.pop('wid')
            tk_class = self._tag2tk[container.tag]
            if parent != self._root:
                parent_id = parent.attrib['wid']
                parent_widget = self.nodes[parent_id]
            else:
                parent_widget = self._master
            self.nodes[wid] = tk_class(parent_widget)
            self._handle_attributes(self.nodes[wid], container.tag, attribs)
        else:
            attribs = container.attrib
            self._handle_attributes(self._master, 'root', attribs)
        # Container children
        for child in container:
            if child.tag in self._containers:
                self._handle_container(child, container)
            elif child.tag == 'geometry':
                self._handle_geometry(child)
            elif child.tag == 'style':
                self._handle_stylesheet(child)
            elif child.tag == 'grid-configure':
                self._handle_grid_configure(self.nodes[wid], child)
            elif child.tag in self._tag2tk.keys():
                self._handle_widget(child, container)
            else:
                print('Invalid tag: %s!' % child.tag, sys.stderr)

    def _handle_geometry(self, geometry):
        """Handles the special <geometry> tag"""
        for child in geometry:
            if child.tag not in ('pack', 'grid', 'place', 'card', 'tab'):
                print('Invalid geometry instruction %s' % child.tag, sys.stderr)
                # @TODO emit error
                continue
            attribs = copy(child.attrib)
            # Getting widget ID
            try:
                wid = attribs.pop('for')
            except KeyError:
                # @TODO emit error
                print('[geom] Required key "for" not found in %s' % child.tag,
                      file=sys.stderr)
                continue
            # Calling appropriate geometry method
            # FIXME add support for padx and pady tuples (workaround already added)
            if wid not in self.nodes:
                print(self.nodes)
            attribs = self._get_attribs_values(self.nodes[wid], child.tag, attribs)
            if child.tag == 'pack':
                self.nodes[wid].pack(**attribs)
            elif child.tag == 'grid':
                self.nodes[wid].grid(**attribs)
            elif child.tag == 'place':
                self.nodes[wid].place(**attribs)
            elif child.tag == 'card':
                name = attribs['name'] if 'name' in attribs else None 
                self.nodes[wid].master.add(self.nodes[wid], name=name)
            elif child.tag == 'tab':
                self.nodes[wid].master.add(self.nodes[wid], **attribs)

    def _handle_stylesheet(self, style):
        """Handles the special <style> tag"""
        self.tkstyle = wtk.Style()
        if 'defaultfonts' in style.attrib and \
                style.attrib['defaultfonts'] != '0':
            wtk.Style.set_default_fonts()
        if 'applydefault' in style.attrib and \
                style.attrib['applydefault'] != '0':
            self.tkstyle.apply_default()
        if 'fromfile' in style.attrib:
            self.tkstyle.apply_from_file(style.attrib['fromfile'])
        else:
            self.tkstyle.apply_from_string(style.text)

    def _handle_grid_configure(self, parent_widget, child):
        for config_item in child:
            index = config_item.attrib.pop('index')
            if config_item.tag == 'row':
                parent_widget.grid_rowconfigure(int(index), **config_item.attrib)
            elif config_item.tag == 'column':
                parent_widget.grid_columnconfigure(int(index), **config_item.attrib)


    def _parse_tree(self):
        """Parses XML and builds interface"""
        if self._root.tag != 'root':
            msg = 'Invalid root tag! Expecting "root", but found %s'
            print(msg % self._root.tag, sys.stderr)
            return False
        self._handle_container(self._root, self._master)
        return True

    def build_from_file(self, filepath):
        """Build user interface from XML file"""
        self._tree = ElementTree.parse(filepath)
        self._root = self._tree.getroot()
        self._parse_tree()

    def build_from_string(self, contents):
        """Build user interface from XML string"""
        self._root = ElementTree.fromstring(contents)
        self._parse_tree()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
