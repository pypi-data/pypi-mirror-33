#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Midi2Freq class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Midi2Freq(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "midi to freq"
        self.label = "Midi 2 Freq"
        self.color = "250:250:0:150"
        self.group = "MIDI"

        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "name":"midi_value",
                "conn_type":"Input",
                "label":"Midi Value"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "label":"Frequency",
                "conn_type":"Output",
                "name":"frequency"}
            ]
        self.codes["declaration"] = """
// block_$id$ = $label$
var $port[frequency]$ = [];

var $port[midi_value]$ = function(value){
    value = (value < 0) ? 0 : value;
    value = (value >127) ? 127 : value;
    var arg = ((parseFloat(value) - 69.0) / 12.0);
    result =  Math.pow(2.0, arg) * 440.0;
    for (var i = 0; i < $port[frequency]$.length ; i++){
        $port[frequency]$[i](result);
    }
    return true;
    };
"""
