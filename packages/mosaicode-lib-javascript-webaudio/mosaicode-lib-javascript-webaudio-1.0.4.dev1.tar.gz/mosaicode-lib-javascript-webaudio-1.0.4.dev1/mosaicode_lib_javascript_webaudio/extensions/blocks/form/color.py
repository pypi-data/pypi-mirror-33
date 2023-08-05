#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Button class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Color(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Color"
        self.label = "Color"
        self.color = "50:150:0:150"
        self.group = "Form"

        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.color",
                "label":"Value",
                "conn_type":"Output",
                "name":"value"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.color",
                "label":"Value",
                "conn_type":"Input",
                "name":"invalue"}
            ]
        self.properties = [{"name": "value",
                            "label": "Value",
                            "type": MOSAICODE_COLOR,
                            "value": '#FFFFFF'
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
    document.getElementById("block_$id$").value = value;
    return true;
    };

"""

        self.codes["execution"] = """
function enter_value$id$(e){
    value = document.getElementById("block_$id$").value;
    for (var i = 0; i < $port[value]$.length ; i++){
        $port[value]$[i](value);
    }
};
"""

        self.codes["html"] = """
$prop[label]$ <input type="color" value="$prop[value]$" oninput="enter_value$id$(event);" id="block_$id$"><br>
"""

