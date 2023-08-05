#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the String class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class String(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = ""
        self.label = "String"
        self.color = "150:50:150:150"
        self.group = "Types"
        self.ports = [{"type": "mosaicode_lib_javascript_webaudio.extensions.ports.string",
                       "conn_type": "Output",
                       "name": "string_value",
                       "label": "Value"}
                      ]

        self.properties = [{"name": "string_value",
                            "label": "Value",
                            "value": "",
                            "type": MOSAICODE_STRING
                            }]

        self.codes["onload"] = """
load_string$id$();
        """

        self.codes["declaration"] = """
var $port[string_value]$ = [];

function load_string$id$(){
    for (var i = 0 ; i < $port[string_value]$.length ; i++)
        $port[string_value]$[i]('$prop[string_value]$');
};

"""
