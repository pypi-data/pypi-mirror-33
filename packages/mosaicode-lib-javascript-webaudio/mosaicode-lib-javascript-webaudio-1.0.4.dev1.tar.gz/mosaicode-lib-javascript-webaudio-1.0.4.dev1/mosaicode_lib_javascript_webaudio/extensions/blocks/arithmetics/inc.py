#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the FloatValue class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Inc(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Increment"
        self.label = "Increment"
        self.color = "150:150:250:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Float",
                "conn_type":"Output",
                "name":"float"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Count",
                "conn_type":"Input",
                "name":"count"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "conn_type":"Input",
                "label":"Value",
                "name":"value"}
            ]
        self.group = "Interface"

        self.properties = [{"name": "value",
                            "label": "Value",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 20000,
                            "step": 1,
                            "value": 1
                            },
                           {"name": "step",
                            "label": "Step",
                            "type": MOSAICODE_FLOAT,
                            "lower": -20000,
                            "upper": 20000,
                            "step": 1,
                            "value": 1
                            }
                           ]

        self.codes["declaration"] = """
// block_$id$ = $label$
var block_$id$_value = $prop[value]$;
var block_$id$_step = $prop[step]$;
var $port[float]$ = [];

var $port[count]$ = function(value){
    block_$id$_value += block_$id$_step;
    for (var i = 0; i < $port[float]$.length ; i++){
        $port[float]$[i](block_$id$_value);
    }
    return true;
    };

var $port[value]$ = function(value){
    block_$id$_value = value;
    return true;
    };

"""
