#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the GreaterThanOrEquals class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class GreaterThanOrEquals(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Greater Than Or Equals (>=)"
        self.label = "Greater Than Or Equals"
        self.color = "163:01:01:150"
        self.group = "Arithmetic Operations"

        self.out_types = ["mosaicode_lib_javascript_webaudio.extensions.ports.bool"]

        self.ports = [
            {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
             "name": "statement_1",
             "label": "Statement 1",
             "conn_type": "Input"},
            {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
             "name": "statement_2",
             "label": "Statement 2",
             "conn_type": "Input"},
            {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.bool",
             "name": "output",
             "label": "Output",
             "conn_type": "Output"}
        ]

        self.codes["onload"] = """
"""

        self.codes["declaration"] = """
var statement_1$id$ = null;
var statement_2$id$ = null;

var $port[output]$ = [];

function greaterThanOrEquals$id$() {
    var ret = statement_1$id$ >= statement_2$id$;
    for (var i = 0; i < $port[output]$.length ; i++){
        $port[output]$[i](ret);
    }
    return true;
}

var $port[statement_1]$ = function(value){
    statement_1$id$ = Math.round(value);
    greaterThanOrEquals$id$();
    return true;
};

var $port[statement_2]$ = function(value){
    statement_2$id$ = Math.round(value);
    greaterThanOrEquals$id$();
    return true;
};
"""

        self.codes["execution"] = """
"""