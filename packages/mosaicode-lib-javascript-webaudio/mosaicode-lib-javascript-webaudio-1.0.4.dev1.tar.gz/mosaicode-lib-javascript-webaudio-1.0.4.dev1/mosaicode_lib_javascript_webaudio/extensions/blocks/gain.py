#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Gain class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Gain(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Sound output"
        self.label = "Gain"
        self.color = "50:150:250:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                   "label":"Input",
                "conn_type":"Input",
                   "name":"input"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                   "label":"Gain",
                "conn_type":"Input",
                   "name":"gain"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "conn_type":"Input",
                 "label":"Gain Value",
                 "name":"gain_value"},
                 {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                 "name":"output",
                "conn_type":"Output",
                 "label":"Output"}]
        self.properties = [{"name": "gain",
                            "label": "Gain",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 32000,
                            "value": 1
                            }
                           ]

        self.group = "Sound"

        self.codes["declaration"] = """
// block_$id$ = $label$
var block_$id$ = context.createGain();
var $port[input]$ = block_$id$;
var $port[output]$ = block_$id$;
var $port[gain]$ = block_$id$.gain;
var $port[gain_value]$ = function(value){
    block_$id$.gain.value = value;
    };
"""

        self.codes["execution"] = "block_$id$.gain.value = $prop[gain]$;\n"
