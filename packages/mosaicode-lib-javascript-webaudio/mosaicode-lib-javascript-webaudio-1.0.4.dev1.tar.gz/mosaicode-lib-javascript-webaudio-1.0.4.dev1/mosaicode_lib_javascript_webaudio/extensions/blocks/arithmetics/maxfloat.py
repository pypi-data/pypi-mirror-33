#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the AddFloat class.
"""
from mosaicode.model.blockmodel import BlockModel

class MaxFloat(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Max Float"
        self.label = "Max Float"
        self.color = "200:200:25:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "name":"first_number",
                "conn_type":"Input",
                "label":"First Number"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "name":"second_number",
                "conn_type":"Input",
                "label":"Second Number"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Result",
                "conn_type":"Output",
                "name":"result"}
            ]
        self.group = "Arithmetics"

        self.codes["declaration"] = """
// block_$id$ = Add Float
var block_$id$_arg1 = 0;
var block_$id$_arg2 = 0;
var $port[result]$ = [];

var $port[first_number]$ = function(value){
    block_$id$_arg1 = parseFloat(value);
    result = (block_$id$_arg1 > block_$id$_arg2)?block_$id$_arg1:block_$id$_arg2;
    for (var i = 0; i < $port[result]$.length ; i++){
        $port[result]$[i](result);
    }
    return true;
    };

var $port[second_number]$ = function(value){
    block_$id$_arg2 = parseFloat(value);
    result = (block_$id$_arg1 > block_$id$_arg2)?block_$id$_arg1:block_$id$_arg2;
    for (var i = 0; i < $port[result]$.length ; i++){
        $port[result]$[i](result);
    }
    return true;
    };
"""
