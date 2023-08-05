#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Button class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Text(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Text"
        self.label = "Text"
        self.color = "50:150:250:150"
        self.group = "Form"

        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.string",
                "label":"Value",
                "conn_type":"Output",
                "name":"value"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.string",
                "label":"Value",
                "conn_type":"Input",
                "name":"invalue"}
            ]
        self.properties = [{"name": "value",
                            "label": "Value",
                            "type": MOSAICODE_STRING,
                            "value": ''
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
    e = e || window.event;
    if (e.keyCode != 13) //Ignore if it is not enter
        return;
    value = document.getElementById("block_$id$").value;
    for (var i = 0; i < $port[value]$.length ; i++){
        $port[value]$[i](value);
    }
};
"""

        self.codes["html"] = """
$prop[label]$ <input type="text" value="$prop[value]$" onkeypress="enter_value$id$(event);"
id="block_$id$"><br>
"""

