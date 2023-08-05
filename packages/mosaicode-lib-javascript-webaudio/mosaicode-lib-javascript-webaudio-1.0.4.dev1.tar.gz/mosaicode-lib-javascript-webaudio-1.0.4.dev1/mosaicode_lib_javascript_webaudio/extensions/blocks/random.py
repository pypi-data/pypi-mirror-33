#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the FloatValue class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Random(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Random"
        self.label = "Random"
        self.color = "150:150:250:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Float",
                "conn_type":"Output",
                "name":"float"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Generate",
                "conn_type":"Input",
                "name":"generate"}
            ]
        self.group = "Interface"

        self.properties = [{"name": "min",
                            "label": "Min",
                            "type": MOSAICODE_FLOAT,
                            "lower": -20000,
                            "upper": 20000,
                            "step": 1,
                            "value": 1
                            },
                           {"name": "max",
                            "label": "Max",
                            "type": MOSAICODE_FLOAT,
                            "lower": -20000,
                            "upper": 20000,
                            "step": 1,
                            "value": 100
                            }
                           ]

        self.codes["declaration"] = """
// block_$id$ = $label$
var block_$id$_min = $prop[min]$;
var block_$id$_max = $prop[max]$;
var $port[float]$ = [];

var $port[generate]$ = function(value){
    value = Math.floor((Math.random() * (block_$id$_max - block_$id$_min)) + block_$id$_min);
    for (var i = 0; i < $port[float]$.length ; i++){
        $port[float]$[i](value);
    }
    return true;
    };

"""
