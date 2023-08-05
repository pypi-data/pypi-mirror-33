#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the FloatValue class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Hour(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Hour"
        self.label = "Hour"
        self.color = "150:10:20:150"
        self.group = "Input Device"

        self.ports = [
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Hour",
                "conn_type":"Output",
                "name":"hour"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Minute",
                "conn_type":"Output",
                "name":"minute"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Second",
                "conn_type":"Output",
                "name":"second"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Millisecond",
                "conn_type":"Output",
                "name":"millisecond"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Time",
                "conn_type":"Output",
                "name":"time"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Generate",
                "conn_type":"Input",
                "name":"generate"}
            ]

        self.properties = []

        self.codes["declaration"] = """
// block_$id$ = $label$
var $port[hour]$ = [];
var $port[minute]$ = [];
var $port[second]$ = [];
var $port[millisecond]$ = [];
var $port[time]$ = [];

var $port[generate]$ = function(value){
    var d = new Date();
    for (var i = 0; i < $port[hour]$.length ; i++){
        $port[hour]$[i](d.getHours());
    }
    for (var i = 0; i < $port[minute]$.length ; i++){
        $port[minute]$[i](d.getMinutes());
    }
    for (var i = 0; i < $port[second]$.length ; i++){
        $port[second]$[i](d.getSeconds());
    }
    for (var i = 0; i < $port[millisecond]$.length ; i++){
        $port[millisecond]$[i](d.getMilliseconds());
    }
    for (var i = 0; i < $port[time]$.length ; i++){
        $port[time]$[i](d.getTime());
    }
    return true;
    };

"""
