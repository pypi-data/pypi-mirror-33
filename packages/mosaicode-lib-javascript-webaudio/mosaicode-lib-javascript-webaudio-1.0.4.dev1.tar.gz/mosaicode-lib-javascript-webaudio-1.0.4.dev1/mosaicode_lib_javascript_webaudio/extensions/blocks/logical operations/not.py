#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Not class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class Not(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Logical Operation NOT"
        self.label = "NOT"
        self.color = "249:229:4:150"
        self.group = "Logical Operations"

        self.out_types = ["mosaicode_lib_javascript_webaudio.extensions.ports.bool"]

        self.ports = [
            {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.bool",
             "name": "condition",
             "label": "Condition",
             "conn_type": "Input"},
            {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.bool",
             "name": "output",
             "label": "Output",
             "conn_type": "Output"}
        ]

        self.codes["onload"] = """
"""

        self.codes["declaration"] = """
var condition$id$ = null;

var $port[output]$ = [];

function not$id$() {
    var ret = !condition$id$;    
    for (var i = 0; i < $port[output]$.length ; i++){
        $port[output]$[i](ret);
    }
    return true;
}

var $port[condition]$ = function(value){
    condition$id$ = value;
    not$id$();
    return true;
};
"""

        self.codes["execution"] = """
"""