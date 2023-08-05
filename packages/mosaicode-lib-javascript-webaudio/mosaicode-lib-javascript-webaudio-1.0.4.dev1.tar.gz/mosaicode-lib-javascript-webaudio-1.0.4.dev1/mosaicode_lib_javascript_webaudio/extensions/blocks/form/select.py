#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Button class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Select(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Select"
        self.label = "Select"
        self.color = "50:150:250:150"
        self.group = "Form"

        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.string",
                "label":"String Value",
                "conn_type":"Output",
                "name":"str_value"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Float Value",
                "conn_type":"Output",
                "name":"float_value"}
            ]
        self.properties = [{"name": "label",
                            "label": "Label",
                            "type": MOSAICODE_STRING,
                            "value": "Label"
                            },
                           {"name": "values",
                            "label": "Values",
                            "type": MOSAICODE_STRING,
                            "value": "values"
                            }
                           ]

        self.codes["declaration"] = """
// block_$id$ = $label$
var $port[str_value]$ = [];
var $port[float_value]$ = [];
"""

        self.codes["function"] = """
function populateCombo(combo, text_values){
        var values = text_values.split(',');
        for (var i = 0 ; i < values.length ; i++){
            var c = document.createElement("option");
            c.text = values[i];
            combo.options.add(c, combo.options.length);
        }
        }
"""

        self.codes["onload"] = "populateCombo(document.getElementById('block_$id$'), '$prop[values]$');"

        self.codes["execution"] = """
function change$id$(){
    el = document.getElementById("block_$id$");
    value = el.options[el.selectedIndex].value;
    for (var i = 0; i < $port[str_value]$.length ; i++){
        $port[str_value]$[i](value);
    }
    for (var i = 0; i < $port[float_value]$.length ; i++){
        $port[float_value]$[i](el.selectedIndex);
    }
};
"""

        self.codes["html"] = """
$prop[label]$ <select onchange="change$id$();" id="block_$id$"></select><br>
"""

