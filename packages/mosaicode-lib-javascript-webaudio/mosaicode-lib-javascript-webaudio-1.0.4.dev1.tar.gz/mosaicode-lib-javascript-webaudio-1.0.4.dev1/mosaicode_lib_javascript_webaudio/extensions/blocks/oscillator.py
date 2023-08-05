#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Oscillator class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Oscillator(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Sound output"
        self.label = "Oscillator"
        self.color = "50:150:250:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                "label":"Osc Frequency",
                "conn_type":"Input",
                "name":"osc_freq"},
                 {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "conn_type":"Input",
                 "label":"Frequency",
                 "name":"freq"},
                 {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "conn_type":"Input",
                 "name":"type",
                 "label":"Type"},
                 {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                 "name":"sound",
                "conn_type":"Output",
                 "label":"Sound"}
                 ]
        self.group = "Sound"

        self.properties = [{"name": "freq",
                            "label": "Frequency",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                             "upper": 20000,
                            "step": 1,
                            "value": 440
                            },
                           {"name": "type",
                            "label": "Type",
                            "type": MOSAICODE_COMBO,
                            "values": ["square",
                                       "sine",
                                       "sawtooth",
                                       "triangle"],
                            "value": "sine"
                            }
                           ]

        self.codes["declaration"] = """
// block_$id$ = Oscillator
var block_$id$ =  context.createOscillator();
var $port[osc_freq]$ = block_$id$.frequency;
var $port[sound]$ = block_$id$;
var $port[freq]$ = function(value){
    block_$id$.frequency.value = value;
};
var $port[type]$ = function(value){
    oscillator = ''
    if (value < 1) oscillator = 'square';
    if (value == 1) oscillator = 'sine';
    if (value == 2) oscillator = 'sawtooth';
    if (value > 2) oscillator = 'triangle';
    block_$id$.type = oscillator;
};
"""
        self.codes["execution"] = """
block_$id$.type = '$prop[type]$';
block_$id$.frequency.value = $prop[freq]$; // value in hertz
block_$id$.detune.value = 100; // value in cents
block_$id$.start(0);
"""
