#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the KeyboardInput class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Keyboard(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Keyboard"
        self.label = "Keyboard"
        self.color = "50:150:250:150"
        self.group = "Input Device"

        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Float Output",
                "conn_type":"Output",
                "name":"float_output"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.char",
                "label":"Char Output",
                "conn_type":"Output",
                "name":"char_output"}
            ]

        self.codes["function"] = """
var keyboard_char_output = [];
var keyboard_float_output = [];
document.onkeypress = function(evt){
    evt = evt || window.event;

    var value = evt.keyCode || evt.which;
    for (var i = 0; i < keyboard_float_output.length ; i++)
        for (var j = 0; j < keyboard_float_output[i].length ; j++)
                keyboard_float_output[i][j](value);

    value = String.fromCharCode(value);
    for (var i = 0; i < keyboard_char_output.length ; i++)
        for (var j = 0; j < keyboard_char_output[i].length ; j++)
                keyboard_char_output[i][j](value);
};
"""

        self.codes["declaration"] = """
// block_$id$ = KeyBoard Input
var $port[char_output]$ = [];
var $port[float_output]$ = [];
keyboard_char_output.push($port[char_output]$);
keyboard_float_output.push($port[float_output]$);
"""

