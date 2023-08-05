#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Midi2Freq class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class StripMidi(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Strip Midi"
        self.label = "Strip Midi"
        self.color = "250:250:0:150"
        self.group = "MIDI"

        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.midi",
                "name":"midi_value",
                "conn_type":"Input",
                "label":"Midi Value"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Note",
                "conn_type":"Output",
                "name":"note"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Velocity",
                "conn_type":"Output",
                "name":"velocity"}
            ]
        self.codes["declaration"] = """
// block_$id$ = $label$
var $port[note]$ = [];
var $port[velocity]$ = [];

var $port[midi_value]$ = function(value){
    for (var i = 0; i < $port[note]$.length ; i++){
        $port[note]$[i](value[0]);
    }
    for (var i = 0; i < $port[note]$.length ; i++){
        $port[velocity]$[i](value[1]);
    }
    return true;
    };
"""
