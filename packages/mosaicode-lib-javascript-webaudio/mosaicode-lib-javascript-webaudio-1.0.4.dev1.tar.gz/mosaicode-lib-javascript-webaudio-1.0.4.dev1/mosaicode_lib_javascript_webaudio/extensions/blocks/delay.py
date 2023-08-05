#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Delay class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Delay(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Delay"
        self.label = "Delay"
        self.color = "150:150:250:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                "label":"Input",
                "conn_type":"Input",
                "name":"input"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                "label":"Output",
                "conn_type":"Output",
                "name":"output"}
            ]

        self.group = "Sound"

        self.properties = [{"name": "time",
                            "label": "Time",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 10000,
                            "step": 1,
                            "value": 1
                            }
                           ]

        self.codes["declaration"] = """
// block_$id$ = Delay
var block_$id$ = context.createDelay();
block_$id$.delayTime.value = $prop[time]$;
var $port[input]$ = block_$id$;
var $port[output]$ = block_$id$;
"""

