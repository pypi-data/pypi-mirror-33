#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Print class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Brackground(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Change Background color"
        self.label = "Background"
        self.color = "50:150:0:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.color",
                "name":"rgb",
                "conn_type":"Input",
                "label":"RGB COlor"}
                ]
        self.group = "Interface"

        self.properties = [{"name": "color",
                            "label": "Color",
                            "value": "#F00",
                            "format": "FF00FF",
                            "type": MOSAICODE_COLOR
                            }
                           ]

        self.codes["declaration"] = """
var $port[rgb]$ = function(value){
    document.body.style.backgroundColor = value;
    return true;
    };
"""
        self.codes["onload"] = """
$port[rgb]$('$prop[color]$');\n
"""
