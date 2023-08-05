#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Title class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Title(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Window Title"
        self.label = "Title"
        self.color = "50:150:250:150"
        self.group = "Form"

        self.ports = [{
            "type":"mosaicode_lib_javascript_webaudio.extensions.ports.string",
            "label":"Value",
            "conn_type":"Input",
            "name":"title"}
            ]
        self.properties = [{"name": "title",
                            "label": "Value",
                            "type": MOSAICODE_STRING,
                            "value": 'Mosaicode - Document Title'
                            }]

        self.codes["declaration"] = """
var $port[title]$ = function(value){
    window.document.title = value;
    return 1;
}
"""

        self.codes["onload"] = """
$port[title]$('$prop[title]$');\n
        """
