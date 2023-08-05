#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the Mouse class.
"""
from mosaicode.GUI.fieldtypes import *
from mosaicode.model.blockmodel import BlockModel

class MousePosition(BlockModel):

    # --------------------------------------------------------------------------
    def __init__(self):
        BlockModel.__init__(self)

        self.language = "javascript"
        self.framework = "webaudio"
        self.help = "Mouse Position"
        self.label = "Mouse Position"
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
                "label":"Y"}
                ]

        self.codes["function"] = """
// ----------------- Mouse position ----------------------------
// Detect if the browser is IE or not.
// If it is not IE, we assume that the browser is NS.
var IE = document.all?true:false

// If NS -- that is, !IE -- then set up for mouse capture
if (!IE) document.captureEvents(Event.MOUSEMOVE)

// Set-up to use getMouseXY function onMouseMove
document.onmousemove = getMouseXY;

// Temporary variables to hold mouse x-y pos.s
var tempX = 0
var tempY = 0

// Variable to keep output ports
var x_ports = [];
var y_ports = [];

// Main function to retrieve mouse x-y pos.s

function getMouseXY(e) {
  if (IE) { // grab the x-y pos.s if browser is IE
    tempX = event.clientX + document.body.scrollLeft
    tempY = event.clientY + document.body.scrollTop
  } else {  // grab the x-y pos.s if browser is NS
    tempX = e.pageX
    tempY = e.pageY
  }
  // catch possible negative values in NS4
  if (tempX < 0){tempX = 0}
  if (tempY < 0){tempY = 0}

    // X value
    for (var i = 0; i < x_ports.length ; i++)
        for (var j = 0; j < x_ports[i].length ; j++)
                x_ports[i][j](tempX);

    // Y value
    for (var i = 0; i < y_ports.length ; i++)
        for (var j = 0; j < y_ports[i].length ; j++)
                y_ports[i][j](tempY);
  return true
}
// ----------------- Mouse position ----------------------------\n
"""

        self.codes["declaration"] = """
// block_$id$ = Mouse
var $port[x]$ = [];
var $port[y]$ = [];
x_ports.push($port[x]$);
y_ports.push($port[y]$);
"""
