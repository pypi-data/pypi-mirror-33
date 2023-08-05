#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the HRTF class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel


class HRTF(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "HRTF"
        self.label = "HRTF"
        self.color = "50:150:250:150"
        self.group = "Sound"

        self.ports = [{"type": "mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                       "name": "sound_input",
                       "conn_type": "Input",
                       "label": "Sound"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.point",
                       "name": "panner_pos",
                       "conn_type": "Input",
                       "label": "Panner Position"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.point",
                       "name": "listener_pos",
                       "conn_type": "Input",
                       "label": "Listener Position"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.point",
                       "name": "panner_orientation",
                       "conn_type": "Input",
                       "label": "Panner Orientation"},

                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.point",
                       "name": "listener_forward",
                       "conn_type": "Input",
                       "label": "Listener Forward"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.point",
                       "name": "listener_up",
                       "conn_type": "Input",
                       "label": "Listener Up"},
                      {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.sound",
                       "label": "Sound",
                       "conn_type": "Output",
                       "name": "output"}
                      ]

        self.properties = [{"name": "distance_model",
                            "label": "Distance Model",
                            "type": MOSAICODE_COMBO,
                            "values": ["linear",
                                       "inverse",
                                       "exponential"],
                            "value": "inverse"
                            },
                           {"name": "cone_inner_angle",
                            "label": "coneInnerAngle",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 360,
                            "value": 360
                            },
                           {"name": "cone_outer_angle",
                            "label": "Cone Outer Angle",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 360,
                            "value": 0
                            },
                           {"name": "cone_outer_gain",
                            "label": "Cone Outer Gain",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 32000,
                            "value": 0
                            },
                           {"name": "ref_distance",
                            "label": "Ref Distance",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 32000,
                            "value": 1
                            },
                           {"name": "max_distance",
                            "label": "Max Distance",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 32000,
                            "value": 10000
                            },
                           {"name": "rolloff_factor",
                            "label": "Rolloff Factor",
                            "type": MOSAICODE_FLOAT,
                            "lower": 0,
                            "upper": 32000,
                            "value": 1
                            }
                           ]

        self.codes["declaration"] = """
// block_$id$ = $label$
var block_$id$_width = window.innerWidth;
var block_$id$_height = window.innerHeight;
var block_$id$_xPos = Math.floor(block_$id$_width/2);
var block_$id$_yPos = Math.floor(block_$id$_height/2);
var block_$id$_zPos = 295;
var block_$id$ = context.createPanner();

block_$id$.panningModel = 'HRTF';
block_$id$.distanceModel = "$prop[distance_model]$";
block_$id$.refDistance = $prop[ref_distance]$;
block_$id$.maxDistance = $prop[max_distance]$;
block_$id$.rolloffFactor = $prop[rolloff_factor]$;
block_$id$.coneInnerAngle = $prop[cone_inner_angle]$;
block_$id$.coneOuterAngle = $prop[cone_outer_angle]$;
block_$id$.coneOuterGain = $prop[cone_outer_gain]$;

var block_$id$_panner_pos = [0, 0, 0];
var block_$id$_listener_pos = [0, 0, 0];
var block_$id$_panner_orientation = [0, 0, 0];
var block_$id$_listener_forward = [0, 0, 0];
var block_$id$_listener_up = [0, 0, 0];


var $port[panner_pos]$ = function(value){
    block_$id$_panner_pos = value;
    block_$id$.setPosition(value[0],
                           value[1],
                           value[2]);
    return true;
};
var $port[listener_pos]$ = function(value){
    block_$id$_listener_pos = value;
    context.listener.setPosition(value[0],
                                 value[1],
                                 value[2]);
    return true;
};
var $port[panner_orientation]$ = function(value){
    block_$id$_panner_orientation = value;
    block_$id$.setOrientation(value[0],
                              value[1],
                              value[2]);
    return true;
};
var $port[listener_forward]$ = function(value){
    block_$id$_listener_forward = value;
    context.listener.setOrientation(value[0],
                                    value[1],
                                    value[2],
                                    block_$id$_listener_up[0],
                                    block_$id$_listener_up[1],
                                    block_$id$_listener_up[2]);
    return true;
};

var $port[listener_up]$ = function(value){
    block_$id$_listener_up = value;
    context.listener.setOrientation(block_$id$_listener_forward[0],
                                    block_$id$_listener_forward[1],
                                    block_$id$_listener_forward[2],
                                    value[0],
                                    value[1],
                                    value[2]);
    return true;
};

var $port[sound_input]$ = block_$id$;
var $port[output]$ = block_$id$;
"""
