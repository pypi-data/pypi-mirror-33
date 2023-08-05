#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Speaker class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Speaker(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Sound output"
        self.label = "Speaker"
        self.color = "150:150:250:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                "label":"Sound",
                "conn_type":"Input",
                "name":"sound"}
            ]
        self.group = "Sound"

        self.codes["declaration"] = """
// block_$id$ = $label$
var $port[sound]$ = context.destination;
"""
