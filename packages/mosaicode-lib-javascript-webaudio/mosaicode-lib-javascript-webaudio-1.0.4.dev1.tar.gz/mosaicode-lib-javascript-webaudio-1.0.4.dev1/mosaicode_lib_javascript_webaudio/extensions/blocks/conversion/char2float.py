#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Char2Float class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Char2Float(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Char to Float"
        self.label = "Char 2 Float"
        self.color = "200:200:25:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.char",
                "label":"Char Input",
                "conn_type":"Input",
                "name":"char_input"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Float Output",
                "conn_type":"Output",
                "name":"float_output"}
            ]
        self.properties = [{"name": "float",
                            "label": "Output float",
                                     "type": MOSAICODE_FLOAT,
                                     "lower": 0,
                                     "upper": 20000,
                                     "step": 1,
                                     "value": 60
                            },
                           {"name": "char",
                            "label": "Input Char",
                            "type": MOSAICODE_STRING,
                            "value": "a"
                            }
                           ]
        self.group = "Conversion"

        self.codes["declaration"] = """
// block_$id$ = Char 2 Float
var $port[float_output]$ = [];
var $port[char_input]$ = function(value){
    if (value != '$prop[char]$')
        return true;
    for (var i = 0; i < $port[float_output]$.length ; i++){
        $port[float_output]$[i]($prop[float]$);
    }
    return true;
    };
"""
