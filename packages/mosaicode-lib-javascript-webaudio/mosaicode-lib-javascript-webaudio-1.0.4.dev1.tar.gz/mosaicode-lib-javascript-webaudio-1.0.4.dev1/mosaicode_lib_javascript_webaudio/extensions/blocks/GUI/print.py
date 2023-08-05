#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Print class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class Print(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Print value"
        self.label = "Print"
        self.color = "50:150:250:150"
        self.group = "GUI"

        self.ports = [{"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "name": "float_value",
                       "conn_type": "Input",
                       "label": "Float Value"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.char",
                       "conn_type": "Input",
                       "name": "char_value",
                       "label": "Char Value"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.color",
                       "conn_type": "Input",
                       "name": "color_value",
                       "label": "Color Value"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.string",
                       "conn_type": "Input",
                       "name": "string_value",
                       "label": "String Value"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.point",
                       "conn_type": "Input",
                       "name": "point_value",
                       "label": "Point Value"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.bool",
                       "conn_type": "Input",
                       "name": "bool_value",
                       "label": "Bool Value"}
                      ]

        self.properties = [{"name": "label",
                            "label": "Label",
                            "value": "Label",
                            "type": MOSAICODE_STRING
                            }
                           ]

        self.codes["declaration"] = """
// $label$
var $port[float_value]$ = function(value){
    document.getElementById("block_$id$").innerHTML = value;
    return true;
    };

var $port[char_value]$ = function(value){
    document.getElementById("block_$id$").innerHTML = value;
    return true;
    };

var $port[color_value]$ = function(value){
    document.getElementById("block_$id$").innerHTML = value;
    return true;
    };

var $port[string_value]$ = function(value){
    document.getElementById("block_$id$").innerHTML = value;
    return true;
    };

var $port[point_value]$ = function(value){
    document.getElementById("block_$id$").innerHTML = "("+value+")";
    return true;
    };
    
var $port[bool_value]$ = function(value){
    document.getElementById("block_$id$").innerHTML = "("+value+")";
    return true;
    };    
"""
        self.codes["html"] = """
$prop[label]$ <span id="block_$id$"></span><br>
"""
