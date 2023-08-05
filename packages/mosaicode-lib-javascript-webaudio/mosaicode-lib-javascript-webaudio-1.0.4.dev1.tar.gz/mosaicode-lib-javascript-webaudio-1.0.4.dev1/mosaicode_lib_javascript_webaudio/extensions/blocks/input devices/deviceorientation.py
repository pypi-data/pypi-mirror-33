#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the DeviceOrientation class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class DeviceOrientation(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Device Orientation"
        self.label = "Device Orientation"
        self.color = "50:50:50:150"
        self.group = "Input Device"

        self.out_types = ["mosaicode_lib_javascript_webaudio.extensions.ports.float",
                          "mosaicode_lib_javascript_webaudio.extensions.ports.float",
                          "mosaicode_lib_javascript_webaudio.extensions.ports.float"]

        self.ports = [
            {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
            "conn_type":"Output",
            "name":"alpha",
            "label":"Alpha"},
            {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
            "conn_type":"Output",
            "name":"beta",
            "label":"Beta"},
            {"type": "mosaicode_lib_javascript_webaudio.extensions.ports.float",
             "conn_type": "Output",
             "name": "gamma",
             "label": "Gamma"}
        ]

        self.codes["onload"] = """
window.addEventListener('deviceorientation', handleDeviceOrientation$id$);
                """

        self.codes["declaration"] = """
var $port[alpha]$ = [];
var $port[beta]$ = [];
var $port[gamma]$ = [];

function handleDeviceOrientation$id$(event){
    for (var i = 0 ; i < $port[alpha]$.length ; i++)
        $port[alpha]$[i](event.alpha);
        
    for (var i = 0 ; i < $port[beta]$.length ; i++)
        $port[beta]$[i](event.beta);
        
    for (var i = 0 ; i < $port[gamma]$.length ; i++)
        $port[gamma]$[i](event.gamma);                
}      
"""

