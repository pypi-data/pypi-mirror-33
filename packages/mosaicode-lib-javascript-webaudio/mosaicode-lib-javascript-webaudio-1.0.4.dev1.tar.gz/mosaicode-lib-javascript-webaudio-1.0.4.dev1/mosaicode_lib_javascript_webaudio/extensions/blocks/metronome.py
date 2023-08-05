#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the FloatValue class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Metronome(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Metronome"
        self.label = "Metronome"
        self.color = "150:150:250:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Float",
                "conn_type":"Output",
                "name":"float"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Start",
                "conn_type":"Input",
                "name":"start"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "conn_type":"Input",
                "label":"Stop",
                "name":"stop"}
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
                           {"name": "time",
                            "label": "Time (ms)",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 20000,
                            "step": 1,
                            "value": 1000
                            }
                           ]

        self.codes["declaration"] = """
// block_$id$ = Float Value
var block_$id$_timeout;
var block_$id$_value = $prop[value]$;
var block_$id$_time = $prop[time]$;
var $port[float]$ = [];

var $port[start]$ = function(value){
    timeout_$id$_value();
    return true;
    };

var $port[stop]$ = function(value){
    if (value > 0) {
    clearTimeout(block_$id$_timeout);
    }
    return true;
    };

"""
        self.codes["execution"] = """
function timeout_$id$_value(){
    for (var i = 0; i < $port[float]$.length ; i++){
        $port[float]$[i](block_$id$_value);
    }
    block_$id$_timeout = setTimeout(timeout_$id$_value, block_$id$_time);
};
"""
        self.codes["onload"] = """"""
