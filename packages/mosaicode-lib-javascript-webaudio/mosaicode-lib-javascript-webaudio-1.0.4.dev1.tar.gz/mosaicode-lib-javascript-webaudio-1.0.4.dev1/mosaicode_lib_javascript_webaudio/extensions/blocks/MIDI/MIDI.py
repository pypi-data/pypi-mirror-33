#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Button class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class MIDI(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "MIDI"
        self.label = "MIDI"
        self.color = "250:250:0:150"
        self.group = "MIDI"
        self.ports = [{"type":"mosaicode_lib_javascript_webaudio.extensions.ports.midi",
                "label":"Note",
                "conn_type":"Output",
                "name":"note"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.midi",
                "label":"Control",
                "conn_type":"Output",
                "name":"control"}
            ]
        self.properties = []

        self.codes["function"] = """
// request MIDI access

if (navigator.requestMIDIAccess) {
    navigator.requestMIDIAccess({sysex: false}).then(MidiSuccess, MidiFailure);
} else {
    alert("No MIDI support in your browser.");
}

// midi functions
function MidiSuccess(midi) {
    // when we get a succesful response, run this code
    console.log('MIDI Access Object', midi);
    var inputs = midi.inputs.values();

    for (var input = inputs.next(); input && !input.done; input = inputs.next()) {
        // each time there is a midi message call the onMIDIMessage function
        input.value.onmidimessage = MidiMessage;
    }
}

function MidiFailure(e) {
    // when we get a failed response, run this code
    message = "No access to MIDI devices or your browser doesn't support WebMIDI API. Please use WebMIDIAPIShim " + e;
    console.log(message);
    alert(message);
}

// Variable to keep output ports
var note_output = [];
var control_output = [];

function MidiMessage (message) {
    //Note On
    if((message.data[0] == 144 && message.data[2] > 0) ||
    // Note Off
    (message.data[0] === 128 || (message.data[0] == 144 && message.data[2] === 0))
    ){
        for (var i = 0; i < note_output.length ; i++)
            for (var j = 0; j < note_output[i].length ; j++)
                    note_output[i][j]([message.data[1],message.data[2]]);
    }


    //Ctrl
    if (message.data[0] === 176 ){
        for (var i = 0; i < control_output.length ; i++)
            for (var j = 0; j < control_output[i].length ; j++)
                    control_output[i][j]([message.data[1],message.data[2]]);
    }
    // Not used
    // (message.data[0] === 176 )//Drum pad
    // (message.data[0] === 208 )//Aftertouch
}


"""

        self.codes["declaration"] = """
// block_$id$ = Mouse
var $port[note]$ = [];
var $port[control]$ = [];
note_output.push($port[note]$);
control_output.push($port[control]$);
"""
