#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Speaker class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class FreqBar(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Freq Bar"
        self.label = "Freq Bar"
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

        self.codes["onload"]="draw_freqbar$id$();"

        self.codes["declaration"] = """
// block_$id$ = $label$
var block_$id$ = context.createAnalyser();
block_$id$.fftSize = 256;
var $port[input]$ = block_$id$;
"""

        self.codes["execution"]="""
function draw_freqbar$id$(){
    var canvas = document.getElementById("canvas$id$");
    var canvasCtx = canvas.getContext("2d");
    var bufferLength = 64;
    var dataArray = new Uint8Array(bufferLength);
    var bufferLengthAlt = block_$id$.frequencyBinCount;

    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = 'rgb(0, 0, 0)';

      block_$id$.getByteFrequencyData(dataArray);

      canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
      canvasCtx.beginPath();


      var barWidth = (canvas.width / bufferLengthAlt) * 2.5;
      var barHeight;
      var x = 0;

      for(var i = 0; i < bufferLengthAlt; i++) {
        barHeight = dataArray[i];
        canvasCtx.fillStyle = 'rgb(' + (barHeight+100) + ',50,50)';
        canvasCtx.fillRect(x, canvas.height - barHeight/2, barWidth, barHeight/2);
        x += barWidth + 1;
      }
      canvasCtx.stroke();
      drawVisual = requestAnimationFrame(draw_freqbar$id$);
}
"""

        self.codes["html"] = """
<canvas id="canvas$id$" class="visualizer" width="$prop[width]$" height="$prop[height]$"></canvas>
"""
