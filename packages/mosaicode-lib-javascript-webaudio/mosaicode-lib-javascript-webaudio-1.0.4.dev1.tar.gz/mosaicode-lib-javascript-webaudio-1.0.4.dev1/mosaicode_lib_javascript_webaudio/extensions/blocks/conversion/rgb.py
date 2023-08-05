#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Print class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class RGB(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Creates RGB Color"
        self.label = "RGB"
        self.color = "50:150:0:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "name":"r",
                "conn_type":"Input",
                "label":"Red"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "name":"g",
                "conn_type":"Input",
                "label":"Green"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "name":"b",
                "conn_type":"Input",
                "label":"Blue"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.color",
                "name":"result",
                "conn_type":"Output",
                "label":"Color"}
                ]
        self.group = "Conversion"

        self.properties = []

        self.codes["declaration"] = """
// $label$
var r$id$ = '00';
var g$id$ = '00';
var b$id$ = '00';
var $port[result]$ = [];

function update_backgroud_color$id$(){
    result = '#' + r$id$ + g$id$ + b$id$;
    for (var i = 0; i < $port[result]$.length ; i++){
        $port[result]$[i](result);
    }
}

var $port[r]$ = function(value){
    value = Math.round(value);
    r$id$ = value.toString(16);
    if (value < 16)
        r$id$ = '0'+ r$id$;
    update_backgroud_color$id$();
    return true;
    };

var $port[g]$ = function(value){
    value = Math.round(value);
    g$id$ = value.toString(16);
    if (value < 16)
        g$id$ = '0'+ g$id$;
    update_backgroud_color$id$();
    return true;
    };

var $port[b]$ = function(value){
    value = Math.round(value);
    b$id$ = value.toString(16);
    if (value < 16)
        b$id$ = '0'+ b$id$;
    update_backgroud_color$id$();
    return true;
    };

"""

