#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Distortion class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Distortion(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Distortion"
        self.label = "Distortion"
        self.color = "50:150:250:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                               "label":"Input",
                            "conn_type":"Input",
                               "name":"input"},
                      {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                              "label":"Output",
                           "conn_type":"Output",
                              "name":"output"}
                     ]

        self.properties = [{"name": "curve",
                            "label": "Curve",
                            "type": MOSAICODE_FLOAT,
                            "value": 800
                            }
                           ]


        self.group = "Sound"

        self.codes["declaration"] = '''
var block_$id$ = context.createWaveShaper();
block_$id$.curve = makeDistortionCurve($prop[curve]$);
block_$id$.oversample = '4x';
var $port[input]$ = block_$id$;
var $port[output]$ = block_$id$;
'''


        self.codes["function"] = '''
function makeDistortionCurve(amount) {
  var k = typeof amount === 'number' ? amount : 50,
    n_samples = 44100,
    curve = new Float32Array(n_samples),
    deg = Math.PI / 180,
    i = 0,
    x;
  for ( ; i < n_samples; ++i ) {
    x = i * 2 / n_samples - 1;
    curve[i] = ( 3 + k ) * x * 20 * deg / ( Math.PI + k * Math.abs(x) );
  }
  return curve;
};
'''
