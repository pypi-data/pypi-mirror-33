#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Microphone class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class Microphone(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Microphone"
        self.label = "Microphone"
        self.color = "150:150:250:150"
        self.ports = [{"type": "mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                       "label": "Output",
                       "conn_type": "Output",
                       "name": "output"}
                      ]

        self.group = '''Input Device'''

        self.codes["declaration"] = '''
</script>
<div>
    <span class="title">Microphone</span>
</div>
<div>
    <div>
        <span class="label">Gain</span>
        <input type="range" id="gain-slider_$id$" class="slider" min="-20" max="20" step="1" value="0" />
        <span id="gain-display_$id$" class="label">0 db</span>
    </div>
</div>

<script>
    var gain = 0;
    var audioSource;
    var block_$id$;

    block_$id$  = context.createBiquadFilter();
    block_$id$.type = "lowshelf";
    block_$id$.frequency.value = 1000;

    var $port[output]$ = block_$id$;

    navigator.getUserMedia =
        navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia ||
        navigator.msGetUserMedia;

if (navigator.getUserMedia) {
    navigator.getUserMedia (
      {
        audio: true,
        video: false
      },
      function (stream) {
        audioSource = context.createMediaStreamSource(stream);

         var gainDisplay = document.getElementById('gain-display_$id$');
         var gainSlider = document.getElementById('gain-slider_$id$');

         gainSlider.addEventListener('input', function () {
           gain = parseFloat(gainSlider.value)
           gainDisplay.textContent = gain + ' db';
           block_$id$.gain.value = gainSlider.value;
         });

         audioSource.connect(block_$id$);
      },
      function (err) {
         console.log('Error initializing user media stream: ' + err);
      }
    );
}
'''

        self.codes["onload"] = ''''''
