#!/usr/bin/env python3

## External Perimeter Fan Adjust
# This Script post-processes G-Code to change the fan speed for the outer-most wall / perimeter.
# Can be used from command line and as a post-processing script in PrusaSlicer Output options.
# Modifications are done in place.
# Supports:     PrusaSlicer, Cura 
# Version:      1.0
# Licence:      CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/

## Import required modules 
# All included in python3
import sys
import re
import argparse
from xmlrpc.client import Boolean

## Set up command line arguments parser with defaults
# source file is expected as a path with no flags
# -s, --speed       to set the fan speed % for external perimeters, defaults to 100 if no arguments are given 
# -l, --startLayer  to set layer at which to start injecting speed adjustments, defaults to 4
# -i, --interactive to show settings and feedback, requiring user input
# Example 1: 
#   externalPerimeterFanAdjust.py c:/foo.gcode
# Example 2:
#   externalPerimeterFanAdjust.py c:/foo.gcode -s 85 -l 3 -i
parser  = argparse.ArgumentParser()
parser.add_argument("source", default = "", type=str)
parser.add_argument("-s", "--speed", dest = "speed", default = 100, type=float)
parser.add_argument("-l", "--startLayer", dest = "start", default = 4, type=int)
parser.add_argument("-i", "--interactive", dest = "interactive", default = False, action="store_true")

## Parse arguments
# Skip first argument, it's the path to the script called (this script)
args = parser.parse_args(sys.argv[1:])
source_file =  args.source 
interactive = args.interactive

## Wrangle inputs 
# Speed is set through g-code with values 0-255
# Script will crash on errors
target_fan_speed = args.speed * 255/100.0
target_fan_speed = target_fan_speed if target_fan_speed <=255 else 255
target_fan_speed = target_fan_speed if target_fan_speed >=0 else 0

start_layer = args.start

if (interactive):
    ## Wait for user input to continue
    print("\n SETTINGS:")
    print(f"\tExternal Perimeter Fan: {target_fan_speed/255*100}%") 
    print(f"\tStarting at layer: {start_layer}")
    print(f"\tSource file: {source_file}")
    input("press enter to continue") 
    print("\nworking...")

## Variables to keep track of the actual sliced fan speed
sliced_fan_speed = 0
fan_changed = False

## Regular Expressions
# The file will be processed line-wise, this defines what to look for on each line
extrusion_type_re = re.compile("^;TYPE:.*")
external_perimeter_type_ps = "External perimeter"
external_perimeter_type_cura = "WALL-OUTER"
layer_change_re = re.compile("^;(LAYER_CHANGE|LAYER\:).*")
fan_change_re = re.compile("^M106.*")
fan_stop_re = re.compile("^M107.*")

## Lambda "function" to set fan speeds > 0 with M106, otherwise use the stop fan command M107
fan_gcode = lambda x : f"M106 S{x}" if x > 0 else "M107" 

## Read source file as list of line 
with open(source_file) as f:
    gcode_lines = f.readlines()
changes = 0

## Write to destination file 
with open(source_file, "w") as dest:
    current_layer = 1 # init at 1 for non-programmers
    # Loop over all source g-code lines 
    for current_line in gcode_lines: 
        # Count layer changes 
        if (layer_change_re.match(current_line) != None): 
            current_layer += 1
        # Check and set fan speed set by slicer
        elif (fan_change_re.match(current_line) != None): 
            speed = float(current_line.split('S')[1])
            sliced_fan_speed = speed
        # Check and set fan stop set by slicer
        elif (fan_stop_re.match(current_line) != None): 
            sliced_fan_speed = 0
        # Check for extrusion type annotation, skip if layer too low 
        elif (extrusion_type_re.match(current_line) != None and current_layer >= start_layer): 
            type = str.strip(current_line.split(':')[1])
            # if the extrusion type is an outer perimeter, insert command to change to target speed
            # inserted commands are tagged with a ;EPFA comment
            if (type == external_perimeter_type_ps or type == external_perimeter_type_cura):
                dest.write(f"{fan_gcode(target_fan_speed)} ;EPFA:Adjust \n")
                fan_changed = True
                changes += 1
            # for all other types reset fan speed to that defined by the slicer 
            elif fan_changed: 
                fan_changed = False
                dest.write(f"{fan_gcode(sliced_fan_speed)} ;EPFA:Reset \n")
                changes += 1
        dest.write(current_line)

if (interactive):
    print(f"\nInserted {changes} lines for fan speed changes")
    input("press enter to exit")