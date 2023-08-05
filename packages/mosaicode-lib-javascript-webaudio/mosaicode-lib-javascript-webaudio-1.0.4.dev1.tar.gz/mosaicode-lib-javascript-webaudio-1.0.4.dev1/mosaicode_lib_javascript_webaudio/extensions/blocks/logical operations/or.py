#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the OR class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class Or(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Logical Operation OR"
        self.label = "OR"
        self.color = "249:229:4:150"
        self.group = "Logical Operations"

        self.out_types = ["mosaicode_lib_javascript_webaudio.extensions.ports.bool"]

        self.ports = [
            {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.bool",
             "name": "condition_1",
             "label": "Condition 1",
             "conn_type": "Input"},
            {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.bool",
             "name": "condition_2",
             "label": "Condition 2",
             "conn_type": "Input"},
            {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.bool",
             "name": "output",
             "label": "Output",
             "conn_type": "Output"}
        ]

        self.codes["onload"] = """
"""

        self.codes["declaration"] = """
var condition_1$id$ = null;
var condition_2$id$ = null;

var $port[output]$ = [];

function or$id$() {
    var ret = condition_1$id$ || condition_2$id$;    
    for (var i = 0; i < $port[output]$.length ; i++){
        $port[output]$[i](ret);
    }
    return true;
}

var $port[condition_1]$ = function(value){
    condition_1$id$ = value;
    or$id$();
    return true;
};

var $port[condition_2]$ = function(value){
    condition_2$id$ = value;
    or$id$();
    return true;
};
"""

        self.codes["execution"] = """
"""