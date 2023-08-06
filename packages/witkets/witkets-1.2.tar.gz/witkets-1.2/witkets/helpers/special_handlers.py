import tkinter.ttk as ttk
import witkets.helpers.attribute_parsers as ap
import ast

special_handlers = {
    ttk.Frame: {
        'takefocus': ap.parse_bool,
        'padding': ap.parse_allpadding
    },
    'pack': {
        'padx': ap.parse_axispadding,
        'pady': ap.parse_axispadding,
        'expand': ap.parse_bool
    },
    'grid': {
        'padx': ap.parse_axispadding,
        'pady': ap.parse_axispadding
    },
    'tab': {
        'padding': ap.parse_allpadding 
    },
}