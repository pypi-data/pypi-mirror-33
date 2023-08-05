#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Lowshelf class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class Lowshelf(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = " Lowshelf"
        self.label = "Lowshelf"
        self.color = "50:150:250:150"
        self.group = "Audio Filter"

        self.ports = [{"type": "mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                       "name": "sound_input",
                       "conn_type": "Input",
                       "label": "Sound"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "name": "freq",
                       "conn_type": "Input",
                       "label": "Frequency"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "name": "gain",
                       "conn_type": "Input",
                       "label": "Gain"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                       "label": "Sound",
                       "conn_type": "Output",
                       "name": "output"}
                      ]
        self.codes["declaration"] = """
// block_$id$ = $label$
var block_$id$ = context.createBiquadFilter();
block_$id$.type = "lowshelf";

var $port[freq]$ = function(value){
    block_$id$.frequency = parseFloat(value);
    return true;
    };

var $port[gain]$ = function(value){
    block_$id$.Q = parseFloat(value);
    return true;
    };

var $port[sound_input]$ = block_$id$;
var $port[output]$ = block_$id$;
"""
