#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Button class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Check(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Check"
        self.label = "Check"
        self.color = "50:150:250:150"
        self.group = "Form"

        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Value",
                "conn_type":"Output",
                "name":"value"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Value",
                "conn_type":"Input",
                "name":"invalue"}
            ]
        self.properties = [{"name": "value",
                            "label": "Value",
                            "type": MOSAICODE_FLOAT,
                            "value": '0'
                            },
                           {"name": "label",
                            "label": "Label",
                            "type": MOSAICODE_STRING,
                            "value": "Label"
                            }
                           ]

        self.codes["declaration"] = """
// block_$id$ = $label$
var $port[value]$ = [];

var $port[invalue]$ = function(value){
    if (value)
    document.getElementById("block_$id$").checked = true;
    else
    document.getElementById("block_$id$").checked = false;
    return true;
    };

"""

        self.codes["execution"] = """
function change_value$id$(e){
    value = document.getElementById("block_$id$").checked;
    for (var i = 0; i < $port[value]$.length ; i++){
        if (value)
            $port[value]$[i](1);
        else
            $port[value]$[i](0);
    }
};
"""

        self.codes["html"] = """
<input type="checkbox" onchange="change_value$id$(event);" id="block_$id$"> $prop[label]$ <br>
"""

