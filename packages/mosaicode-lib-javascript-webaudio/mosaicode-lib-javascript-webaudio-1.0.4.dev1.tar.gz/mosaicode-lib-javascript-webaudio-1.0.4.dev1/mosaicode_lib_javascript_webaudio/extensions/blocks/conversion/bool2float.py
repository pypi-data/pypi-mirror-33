#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Bool2Float class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Bool2Float(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Bool to Float"
        self.label = "Bool 2 Float"
        self.color = "200:200:25:150"
        self.ports = [
            {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.bool",
            "label":"Bool Input",
            "conn_type":"Input",
            "name":"bool_input"},
            {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
            "label":"Float Output",
            "conn_type":"Output",
            "name":"float_output"}
        ]
        self.properties = []
        self.group = "Conversion"

        self.codes["declaration"] = """
var $port[float_output]$ = [];
var $port[bool_input]$ = function(value) {
    var ret = value ? 1.0 : 0.0;
    for (var i = 0; i < $port[float_output]$.length ; i++){
        $port[float_output]$[i](ret);
    }
    return true;
};
"""
