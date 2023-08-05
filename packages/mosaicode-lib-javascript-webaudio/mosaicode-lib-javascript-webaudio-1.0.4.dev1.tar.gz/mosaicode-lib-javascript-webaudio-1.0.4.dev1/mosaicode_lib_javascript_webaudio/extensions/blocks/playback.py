#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Playback class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class Playback(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Playback"
        self.label = "Playback"
        self.color = "150:150:250:150"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                "label":"Output",
                "conn_type":"Output",
                "name":"output"}
            ]

        self.group = '''Sound'''

        self.properties = [{"name": "loop",
                            "label": "Loop",
                            "type": MOSAICODE_CHECK,
                            "value": "True"
                            },
                           {"name": "label",
                            "label": "Label",
                            "type": MOSAICODE_STRING,
                            "value": "Playback"
                           }
                        ]

        self.codes["declaration"] = '''
var block_$id$ = context.createBufferSource();
var $port[output]$ = block_$id$;
'''

        self.codes["html"] = '''
$prop[label]$ <input type="file" id="pb_$id$" onchange="handleFile_$id$(this.files)">
'''

        self.codes["execution"] = '''
function handleFile_$id$() {
    var input_pb_$id$ = document.getElementById("pb_$id$");
    input_pb_$id$.addEventListener("change", handleFile_$id$, false);

    var reader = new FileReader();
    reader.onload = function(ev) {
          context.decodeAudioData(ev.target.result, function(buffer) {
                   block_$id$.buffer = buffer;
                   block_$id$.loop = ("$prop[loop]$" == "True");
          });
    };
    reader.readAsArrayBuffer(input_pb_$id$.files[0]);

    $port[output]$.start();
}
'''

        self.codes["onload"] = ''''''
