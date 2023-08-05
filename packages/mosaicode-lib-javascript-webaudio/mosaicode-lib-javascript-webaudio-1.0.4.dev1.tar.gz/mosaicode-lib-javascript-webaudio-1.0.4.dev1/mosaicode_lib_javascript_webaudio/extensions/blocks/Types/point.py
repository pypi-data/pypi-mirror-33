#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Point class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class Point(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = ""
        self.label = "Point"
        self.color = "150:50:150:150"
        self.group = "Types"
        self.ports = [{"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "name": "x",
                       "conn_type": "Input",
                       "label": "X"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "name": "y",
                       "conn_type": "Input",
                       "label": "Y"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "name": "z",
                       "conn_type": "Input",
                       "label": "Z"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.point",
                       "conn_type": "Output",
                       "name": "point_value",
                       "label": "Point Value"}
                      ]

        self.properties = [{"name": "x",
                            "label": "X",
                            "value": "0",
                            "type": MOSAICODE_FLOAT
                            },
                           {"name": "y",
                            "label": "Y",
                            "value": "0",
                            "type": MOSAICODE_FLOAT
                            },
                           {"name": "z",
                            "label": "Z",
                            "value": "0",
                            "type": MOSAICODE_FLOAT
                            }]

        self.codes["onload"] = """
load_point$id$();
        """

        self.codes["declaration"] = """
var $port[point_value]$ = [];

block_$id$_x = $prop[x]$;
block_$id$_y = $prop[y]$;
block_$id$_z = $prop[z]$;

var $port[x]$ = function(value){
    block_$id$_x = parseFloat(value);
    load_point$id$();
    return true;
    };

var $port[y]$ = function(value){
    block_$id$_y = parseFloat(value);
    load_point$id$();
    return true;
    }

var $port[z]$ = function(value){
    block_$id$_z = parseFloat(value);
    load_point$id$();
    return true;
    }

function load_point$id$(){
    for (var i = 0 ; i < $port[point_value]$.length ; i++)
        $port[point_value]$[i]([block_$id$_x, block_$id$_y, block_$id$_z]);
};

"""
