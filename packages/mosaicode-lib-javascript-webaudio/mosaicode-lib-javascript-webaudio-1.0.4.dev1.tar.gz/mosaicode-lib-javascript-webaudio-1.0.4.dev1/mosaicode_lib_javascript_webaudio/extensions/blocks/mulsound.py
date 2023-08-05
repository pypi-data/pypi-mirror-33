#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the MulSound class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class MulSound(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Mul Sound"
        self.label = "Mul Sound"
        self.color = "50:150:250:150"
        self.group = "Sound"

        self.ports = [{"type": "mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                       "name": "sound_input0",
                       "conn_type": "Input",
                       "label": "Sound"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                       "name": "sound_input1",
                       "conn_type": "Input",
                       "label": "Input"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                       "label": "Sound",
                       "conn_type": "Output",
                       "name": "output"}
                      ]

        self.codes["function"] = """
MulSound = function(context, analyzer0, analyzer1) {
    var that = this;
    this.analyzer0 = analyzer0;
    this.analyzer1 = analyzer1;
    this.context = context;
    this.node = context.createScriptProcessor(1024, 1, 1);
    this.node.onaudioprocess = function(e) {that.process(e)};
}

MulSound.prototype.process = function(e) {
    var in0 = new Float32Array(this.analyzer0.fftSize);
    var in1 = new Float32Array(this.analyzer1.fftSize);

    this.analyzer0.getFloatTimeDomainData(in0);
    this.analyzer1.getFloatTimeDomainData(in1);

    var out = e.outputBuffer.getChannelData(0);
    for (var i = 0; i < in0.length; ++i) {
        out[i] = in0[i] * in1[i];
    }
}
"""
        self.codes["declaration"] = """
// block_$id$ = $label$
var block_$id$_in0 = context.createAnalyser();
var block_$id$_in1 = context.createAnalyser();

var $port[sound_input0]$ = block_$id$_in0;
var $port[sound_input1]$ = block_$id$_in1;
var block_$id$_obj = new MulSound(context, block_$id$_in0, block_$id$_in1);
var $port[output]$ = block_$id$_obj.node;
"""
