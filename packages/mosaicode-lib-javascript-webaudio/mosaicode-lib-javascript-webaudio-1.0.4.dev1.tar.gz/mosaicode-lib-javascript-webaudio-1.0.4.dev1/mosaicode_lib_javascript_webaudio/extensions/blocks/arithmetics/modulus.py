#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Modulus class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class Modulus(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Modulus Operation (%)"
        self.label = "Modulus"
        self.color = "200:200:25:150"
        self.group = "Arithmetics"

        self.out_types = ["mosaicode_lib_javascript_webaudio.extensions.ports.float"]

        self.ports = [
            {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
             "name": "dividend",
             "label":"Dividend",
             "conn_type":"Input"},
            {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
             "name": "divisor",
             "label": "Divisor",
             "conn_type": "Input"},
            {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
             "name": "rest",
             "label": "Rest",
             "conn_type": "Output"}
        ]

        self.codes["onload"] = """
"""

        self.codes["declaration"] = """
var dividend$id$ = 0.0;
var divisor$id$ = 1.0;
        
var $port[rest]$ = [];

function modulus$id$() {
    if (divisor$id$ === 0.0) {
        divisor$id$ = 1.0;
    }
    
    var rest = dividend$id$ % divisor$id$;
    for (var i = 0; i < $port[rest]$.length ; i++){
        $port[rest]$[i](rest);
    }
    
    return true;
}

var $port[dividend]$ = function(value){
    dividend$id$ = Math.round(value);
    modulus$id$();
    return true;
};

var $port[divisor]$ = function(value){
    divisor$id$ = Math.round(value);
    modulus$id$();
    return true;
};
"""

        self.codes["execution"] = """
"""