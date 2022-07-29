# PerimeterFanAdjust
Python3 Script to adjust fan speed of external perimeters. Can be used to experiment on quality, strength and overhang behaviour in 3D printing.

## Requirements
- Python3

## Supports
- G-Code sliced with PrusaSlicer (tested 2.4, 2.5a)
- G-Code sliced with Cura (tested 4.7, 5.1)
- PrusaSlicer Output Post-Processing

## Usage
The Script can be used from the command line or as a post-processing script in PrusaSlicer.

### Command line usage
#### Arguments:
**source file** is expected as a path with no flags
- **-s**; **--speed**	Set the target fan speed (in %) for outermost perimeter, defaults to 100
- **-l**, **--startLayer**  to set layer at which to start injecting speed adjustments, defaults to 4
- **-i**, **--interactive** to show settings and feedback, requiring user input

#### Examples: 
Call with default parameters:
> ./epfa.py /path/to/file.gcode
Set fan speed to 85% an start at second layer
> ./epfa.py /path/to/file.gcode -s 85 -l 2

### PrusaSlicer Post-Processing
- Navigate to _Print Settings -> Output Options -> Post-Processing scripts_
- Depending on your system, enter the path to python and to the script with params or just the script 
> "/path/to/epfa.py" -s 99.2
or
> python3 "/path/to/epfa.py" -l 5
or, this was required for my windows system
> "/path/to/python3.exe" "/path/to/epfa.py" -i