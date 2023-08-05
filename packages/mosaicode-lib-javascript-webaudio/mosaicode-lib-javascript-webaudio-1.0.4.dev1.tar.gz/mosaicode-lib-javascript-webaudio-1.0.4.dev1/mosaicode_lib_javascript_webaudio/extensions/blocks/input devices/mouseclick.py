#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Mouse class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class MouseClick(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Mouse Click"
        self.label = "Mouse Click"
        self.color = "50:50:50:150"
        self.group = "Input Device"

        self.out_types = ["mosaicode_lib_javascript_webaudio.extensions.ports.float", "mosaicode_lib_javascript_webaudio.extensions.ports.float"]
        self.ports = [
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "conn_type":"Output",
                "name":"x",
                "label":"X"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "conn_type":"Output",
                "name":"y",
                "label":"Y"},
                {"type":"mosaicode_lib_javascript_webaudio.extensions.ports.float",
                "conn_type":"Output",
                "name":"button",
                "label":"Button"}
                ]

        self.codes["function"] = """
// ----------------- Mouse click ----------------------------
// Variable to keep output ports
var x_click_ports = [];
var y_click_ports = [];
var button_click_ports = [];

document.onmousedown = getMouseClick;
function getMouseClick(event) {
    // X value
    for (var i = 0; i < x_click_ports.length ; i++)
        for (var j = 0; j < x_click_ports[i].length ; j++)
                x_click_ports[i][j](event.x);

    // Y value
    for (var i = 0; i < y_click_ports.length ; i++)
        for (var j = 0; j < y_click_ports[i].length ; j++)
                y_click_ports[i][j](event.y);

    // Button value
    for (var i = 0; i < button_click_ports.length ; i++)
        for (var j = 0; j < button_click_ports[i].length ; j++)
                button_click_ports[i][j](event.button);

  return true
}
// ----------------- Mouse position ----------------------------\n
"""

        self.codes["declaration"] = """
// block_$id$ = Mouse
var $port[x]$ = [];
var $port[y]$ = [];
var $port[button]$ = [];
x_click_ports.push($port[x]$);
y_click_ports.push($port[y]$);
button_click_ports.push($port[button]$);
"""
