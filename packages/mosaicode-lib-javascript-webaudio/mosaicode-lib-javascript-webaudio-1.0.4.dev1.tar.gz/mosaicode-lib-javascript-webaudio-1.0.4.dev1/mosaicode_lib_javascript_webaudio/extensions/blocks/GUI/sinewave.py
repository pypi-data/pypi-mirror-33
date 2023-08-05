#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Speaker class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class SineWave(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Sine Wave"
        self.label = "Sine Wave"
        self.color = "150:050:050:150"
        self.group = "GUI"

        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                "label":"Sound",
                "conn_type":"Input",
                "name":"input"}
            ]

        self.properties = [{"name": "width",
                            "label": "Width",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 32000,
                            "value": 640
                            },
                            {"name": "height",
                            "label": "Height",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 32000,
                            "value": 240
                            }
                           ]

        self.codes["onload"]="draw_sinewave$id$();"

        self.codes["declaration"] = """
// block_$id$ = $label$
var block_$id$ = context.createAnalyser();
var $port[input]$ = block_$id$;
"""

        self.codes["execution"]="""
function draw_sinewave$id$(){
    var canvas = document.getElementById("canvas$id$");
    var canvasCtx = canvas.getContext("2d");
    var bufferLength = 64;
    var dataArray = new Uint8Array(bufferLength);

    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = 'rgb(0, 0, 0)';

      block_$id$.getByteTimeDomainData(dataArray);

      canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
      canvasCtx.beginPath();

      var sliceWidth = canvas.width * 1.0 / bufferLength;
      var x = 0;

      for(var i = 0; i < bufferLength; i++) {

        var v = dataArray[i] / 128.0;
        var y = v * canvas.height/2;

        if(i === 0) {
          canvasCtx.moveTo(x, y);
        } else {
          canvasCtx.lineTo(x, y);
        }

        x += sliceWidth;
      }

      canvasCtx.stroke();
      drawVisual = requestAnimationFrame(draw_sinewave$id$);
}
"""

        self.codes["html"] = """
<canvas id="canvas$id$" class="visualizer" width="$prop[width]$" height="$prop[height]$"></canvas>
"""
