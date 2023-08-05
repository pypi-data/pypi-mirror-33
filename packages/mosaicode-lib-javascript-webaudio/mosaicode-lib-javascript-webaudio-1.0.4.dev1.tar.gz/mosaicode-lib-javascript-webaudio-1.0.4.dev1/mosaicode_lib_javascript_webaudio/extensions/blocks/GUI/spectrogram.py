#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Visualizer class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class Spectrogram(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Spectrogram"
        self.label = "Spectrogram"
        self.color = "150:150:250:150"
        self.ports = [{"type": "mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                       "label": "Input",
                       "conn_type": "Input",
                       "name": "input"}
                      ]

        self.group = '''GUI'''

        self.codes["onload"] = """
(function () {
  function SpectrogramVisualizer(audioContext, canvasElement) {
    this.analyserNode = audioContext.createAnalyser();
    this.analyserNode.fftSize = 8192;
    this.fftData = new Float32Array(this.analyserNode.frequencyBinCount);

    this.graphicWidth = parseInt(getComputedStyle(canvasElement).width, 10);
    this.graphicHeight = parseInt(getComputedStyle(canvasElement).height, 10);

    var gc = this.graphicContext = canvasElement.getContext("2d");
    gc.fillStyle = '#000000';

    this.pixel = gc.createImageData(1,1);
    this.pixel.data[3] = 255;

    this.gain = 0;
    this.stopping = false;

    this.draw();
  }

  SpectrogramVisualizer.prototype.acceptConnection = function (connectedNode) {
    connectedNode.connect(this.analyserNode);
    this.connectedNode = connectedNode;
  };

  SpectrogramVisualizer.prototype.draw = function () {
    if (this.stopping) {
      this.stopping = false;
      return;
    }

    var gc = this.graphicContext;
    var gw = this.graphicWidth;
    var gh = this.graphicHeight;

    if (!this.connectedNode) {
      gc.fillRect(0, 0, gw, gh);
    }
    else {
      var slideImage = gc.getImageData(0, 0, gw - 1, gh);
      gc.putImageData(slideImage, 1, 0);

      var i, y, n;

      this.analyserNode.getFloatFrequencyData(this.fftData);

      for (i = 0; i < gh; ++i) {
        n = Math.min(Math.max((this.fftData[i] + this.gain + 80) * 4, 0), 255);
        this.pixel.data[0] = n;
        this.pixel.data[1] = n;
        this.pixel.data[2] = n;
        gc.putImageData(this.pixel, 0, gh - i);
      }
    }

    this.animationHandle = requestAnimationFrame(function () { this.draw(); }.bind(this));
  };

  SpectrogramVisualizer.prototype.releaseConnection = function () {
    this.connectedNode.disconnect(this.analyserNode);
    delete this.connectedNode;
  };

  SpectrogramVisualizer.prototype.stop = function () {
    this.stopping = true;
  };

  window.App = window.App || {};
  window.App.SpectrogramVisualizer = SpectrogramVisualizer;
})();

(function () {
    var visCanvas_$id$ = document.getElementById('spectrogram_$id$')
    var visualizer_$id$ = new  App.SpectrogramVisualizer(context, visCanvas_$id$);
    visualizer_$id$.gain = 1;
    visualizer_$id$.acceptConnection(block_$id$);
})();
"""
        self.codes["declaration"] = """
var block_$id$ = context.createGain();
block_$id$.gain = 1;
var $port[input]$ = block_$id$;
"""
        self.codes["html"] = """
<h2>SpectrogramVisualizer_Block$id$</h2>
<div>
  <canvas id="spectrogram_$id$" width="1024" height="300"></canvas>
</div>

"""
