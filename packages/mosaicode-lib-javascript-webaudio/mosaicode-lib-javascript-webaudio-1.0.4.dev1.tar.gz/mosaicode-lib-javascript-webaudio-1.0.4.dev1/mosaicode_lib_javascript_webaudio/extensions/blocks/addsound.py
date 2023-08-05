#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the AddSound class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class AddSound(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Add Sound"
        self.label = "Add Sound"
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
Merger = function(context) {
  var that = this;
  this.x = 0; // Initial sample number
  this.context = context;
  this.node = context.createScriptProcessor(1024, 1, 1);
  this.node.onaudioprocess = function(e) { that.process(e) };
}

Merger.prototype.process = function(e) {
  var in0 = e.inputBuffer.getChannelData(0);
  var out = e.outputBuffer.getChannelData(0);
  for (var i = 0; i < in0.length; ++i) {
      out[i] = in0[i];
  }
}
"""
        self.codes["declaration"] = """
// block_$id$ = $label$
var block_$id$_obj = new Merger(context);
var $port[sound_input0]$ = block_$id$_obj.node;
var $port[sound_input1]$ = block_$id$_obj.node;
var $port[output]$ = block_$id$_obj.node;
"""
