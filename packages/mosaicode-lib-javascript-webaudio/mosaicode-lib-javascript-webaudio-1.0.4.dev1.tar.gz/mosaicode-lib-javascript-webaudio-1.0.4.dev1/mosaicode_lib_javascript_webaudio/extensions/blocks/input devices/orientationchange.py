#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the OrientationChange class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class OrientationChange(BlockModel):

    # -------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Orientation Change"
        self.label = "Orientation Change"
        self.color = "50:50:50:150"
        self.group = "Input Device"

        self.out_types = ["mosaicode_lib_javascript_webaudio.extensions.ports.bool",
                          "mosaicode_lib_javascript_webaudio.extensions.ports.bool"]

        self.ports = [
            {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.bool",
            "conn_type":"Output",
            "name":"portrait",
            "label":"Portrait"},
            {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.bool",
            "conn_type":"Output",
            "name":"landscape",
            "label":"Landscape"}
        ]

        self.codes["onload"] = """
window.addEventListener('orientationchange', onOrientationChange$id$, false);
                """

        self.codes["declaration"] = """
var $port[portrait]$ = [];
var $port[landscape]$ = [];

function onOrientationChange$id$(event){
    var isPortrait = window.orientation % 180 === 0;
    if (window.orientation % 180 === 0) {
        for (var i = 0 ; i < $port[portrait]$.length ; i++)
            $port[portrait]$[i](isPortrait);
            
    } else {    
        for (var i = 0 ; i < $port[landscape]$.length ; i++)
            $port[landscape]$[i](isPortrait);
    }                
}
"""

        self.codes["execution"] = """
onOrientationChange$id$();
"""