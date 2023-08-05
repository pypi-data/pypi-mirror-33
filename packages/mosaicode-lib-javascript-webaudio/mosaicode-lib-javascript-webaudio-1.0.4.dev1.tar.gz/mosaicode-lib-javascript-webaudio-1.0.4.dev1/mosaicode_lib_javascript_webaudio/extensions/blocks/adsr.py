#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the ADSR class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class ADSR(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "ADSR"
        self.label = "ADSR"
        self.color = "50:150:250:150"

        self.ports = [{"type": "mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                       "label": "Input",
                       "conn_type": "Input",
                       "name": "input"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "label": "Attack",
                       "conn_type": "Input",
                       "name": "a"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "label": "Decay",
                       "conn_type": "Input",
                       "name": "d"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "label": "Sustain",
                       "conn_type": "Input",
                       "name": "s"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "label": "Release",
                       "conn_type": "Input",
                       "name": "r"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "label": "Gain",
                       "conn_type": "Input",
                       "name": "g"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                       "conn_type": "Input",
                       "label": "Event Play",
                       "name": "play"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                       "label": "Output",
                       "conn_type": "Output",
                       "name": "output"}
                      ]

        self.group = "Sound"

        self.properties = [
            {"name": "a",
             "label": "Attack",
             "type": MOSAICODE_FLOAT,
             "lower": 0,
             "upper": 10000,
             "step": 1,
             "value": 200
             },
            {"name": "d",
             "label": "Decay",
             "type": MOSAICODE_FLOAT,
             "lower": 0,
             "upper": 10000,
             "step": 1,
             "value": 20
             },
            {"name": "s",
             "label": "Sustain",
             "type": MOSAICODE_FLOAT,
             "lower": 0,
             "upper": 10000,
             "step": 1,
             "value": 100
             },
            {"name": "r",
             "label": "Release",
             "type": MOSAICODE_FLOAT,
             "lower": 0,
             "upper": 10000,
             "step": 1,
             "value": 50
             },
            {"name": "g",
             "label": "Gain",
             "type": MOSAICODE_FLOAT,
             "lower": 0,
             "upper": 10000,
             "step": 1,
             "value": 0.8
             }
        ]

        self.codes["function"] = """
Envelope = function(context, a, d, s, r, g) {
this.node = context.createGain()
this.context = context;
this.node.gain.value = 0;
this.a = a / 1000.0;
this.d = d / 1000.0;
this.s = s / 1000.0;
this.r = r / 1000.0;
this.g = g;
}

Envelope.prototype.play = function(e) {
var time = this.context.currentTime;
// Zero
this.node.gain.linearRampToValueAtTime(0, time);
// Attack time
time += this.a;
this.node.gain.linearRampToValueAtTime(1, time);
// Decay time
time += this.d;
this.node.gain.linearRampToValueAtTime(0.5, time);
// Sustain time (do nothing)
time += this.s;
// Release time
time += this.r;
this.node.gain.linearRampToValueAtTime(0, time);
}

Envelope.prototype.seta = function(a) {
    this.a = parseFloat(a)/1000.0;
}

Envelope.prototype.setd = function(d) {
    this.d = parseFloat(d)/1000.0;
}

Envelope.prototype.sets = function(s) {
    this.s = parseFloat(s)/1000.0;
}

Envelope.prototype.setr = function(r) {
    this.r = parseFloat(r)/1000.0;
}

Envelope.prototype.setg = function(g) {
    this.g = parseFloat(g);
}
"""
        self.codes["declaration"] = """
// block_$id$ = $label$

var block_$id$_obj = new Envelope(context, $prop[a]$, $prop[d]$, $prop[s]$, $prop[r]$, $prop[g]$);
var $port[input]$ = block_$id$_obj.node;
var $port[output]$ = block_$id$_obj.node;

var $port[a]$ = function(value){
    block_$id$_obj.seta(value);
};

var $port[d]$ = function(value){
    block_$id$_obj.setd(value);
};

var $port[s]$ = function(value){
    block_$id$_obj.sets(value);
};

var $port[r]$ = function(value){
    block_$id$_obj.setr(value);
};

var $port[g]$ = function(value){
    block_$id$_obj.setg(value);
};

var $port[play]$ = function(value){
    if (value != 0) {
        block_$id$_obj.play();
    }
};
"""
