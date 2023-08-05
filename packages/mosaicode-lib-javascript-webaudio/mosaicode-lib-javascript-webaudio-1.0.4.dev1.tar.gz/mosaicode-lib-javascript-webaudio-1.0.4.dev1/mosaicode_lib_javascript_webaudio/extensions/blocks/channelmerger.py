#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the ChannelMerger class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class ChannelMerger(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Channel Merger"
        self.label = "Channel Merger"
        self.color = "50:150:250:150"

        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                "label":"Sound Input 1",
                "conn_type":"Input",
                "name":"sound_input_1"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                "conn_type":"Input",
                "label":"Sound Input 2",
                "name":"sound_input_2"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                "label":"Sound Output",
                "conn_type":"Output",
                "name":"sound_output"}
            ]

        self.group = "Sound"

        self.codes["function"] = """
Merger = function(context) {
  var that = this;
  this.x = 0; // Initial sample number
  this.context = context;
  this.node = context.createScriptProcessor(1024, 1, 1);
  this.node.onaudioprocess = function(e) { that.process(e) };
}

Merger.prototype.process = function(e) {
  var in1 = e.inputBuffer.getChannelData(0);
  var out = e.outputBuffer.getChannelData(0);
  for (var i = 0; i < in1.length; ++i) {
      out[i] = in1[i];
  }
}
"""
        self.codes["declaration"] = """
// block_$id$ = Channel Merger
var block_$id$_obj = new Merger(context);
var $port[sound_output]$ = block_$id$_obj.node;
var $port[sound_input_1]$ = block_$id$_obj.node;
var $port[sound_input_2]$ = block_$id$_obj.node;
"""
