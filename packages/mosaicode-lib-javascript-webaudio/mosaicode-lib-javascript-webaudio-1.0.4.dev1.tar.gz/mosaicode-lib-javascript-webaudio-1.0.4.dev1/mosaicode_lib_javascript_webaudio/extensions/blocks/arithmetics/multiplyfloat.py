#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the MultiplyFloat class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class MultiplyFloat(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Multiply float values"
        self.label = "Multiply Float"
        self.color = "200:200:25:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "name":"first_number",
                "conn_type":"Input",
                "label":"First Number"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "conn_type":"Input",
                "name":"second_number",
                "label":"Second Number"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Result",
                "conn_type":"Output",
                "name":"result"}
            ]
        self.group = "Arithmetics"

        self.codes["declaration"] = """
// block_$id$ = Multiply Float
var block_$id$_arg1 = 0;
var block_$id$_arg2 = 0;
var $port[result]$ = [];

var $port[first_number]$ = function(value){
    block_$id$_arg1 = parseFloat(value);
    result = parseFloat(block_$id$_arg1) * parseFloat(block_$id$_arg2);
    for (var i = 0; i < $port[result]$.length ; i++){
        $port[result]$[i](result);
    }
    return true;
    };

var $port[second_number]$ = function(value){
    block_$id$_arg2 = parseFloat(value);
    result = parseFloat(block_$id$_arg1) * parseFloat(block_$id$_arg2);
    for (var i = 0; i < $port[result]$.length ; i++){
        $port[result]$[i](result);
    }
    return true;
    };
"""
