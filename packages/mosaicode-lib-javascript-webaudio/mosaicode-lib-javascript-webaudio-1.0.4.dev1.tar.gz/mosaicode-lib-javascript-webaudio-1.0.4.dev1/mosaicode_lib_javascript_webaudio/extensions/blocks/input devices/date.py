#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the FloatValue class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Date(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Date"
        self.label = "Date"
        self.color = "150:10:20:150"
        self.group = "Input Device"

        self.ports = [
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Day",
                "conn_type":"Output",
                "name":"day"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Month",
                "conn_type":"Output",
                "name":"month"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Year",
                "conn_type":"Output",
                "name":"year"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Generate",
                "conn_type":"Input",
                "name":"generate"}
            ]

        self.properties = []

        self.codes["declaration"] = """
// block_$id$ = $label$
var $port[day]$ = [];
var $port[month]$ = [];
var $port[year]$ = [];

var $port[generate]$ = function(value){
    var d = new Date();
    for (var i = 0; i < $port[day]$.length ; i++){
        $port[day]$[i](d.getDate());
    }
    for (var i = 0; i < $port[month]$.length ; i++){
        $port[month]$[i](d.getMonth());
    }
    for (var i = 0; i < $port[year]$.length ; i++){
        $port[year]$[i](d.getFullYear());
    }
    return true;
    };

"""
