#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Button class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Number(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Number"
        self.label = "Number"
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
                            },
                            {"name": "min",
                            "label": "Min",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                             "upper": 20000,
                            "step": 1,
                            "value": 0
                            },
                            {"name": "max",
                            "label": "Max",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                             "upper": 20000,
                            "step": 1,
                            "value": 100
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
function change_value$id$(e){
    value = document.getElementById("block_$id$").value;
    for (var i = 0; i < $port[value]$.length ; i++){
        $port[value]$[i](value);
    }
};
"""

        self.codes["html"] = """
$prop[label]$ <input type="number" min="$prop[min]$" max="$prop[max]$" onchange="change_value$id$(event);" id="block_$id$"><br>
"""

