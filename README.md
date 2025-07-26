# Wand of the Ring Fairy

This is a Python GUI for [ringfairy](https://github.com/k3rs3d/ringfairy). It allows you to use [ringfairy](https://github.com/k3rs3d/ringfairy) without having to interact with the command line. You can add, update, and remove sites without having to hand-edit a JSON file. 

## Installation

1. Clone or download this repository.
2. Procure dependencies. (Requires Python 3.7+)
    - (Usually Tkinter is included with Python, but be sure it's present!)
    - `pip install --user tk`
3. Place your [ringfairy](https://github.com/k3rs3d/ringfairy) binary in the same directory.

## Invocation

To use the script:

`python wand.py`

Manage your mystical sites:
- Add, compose, and delete site entries. To add a new site, click "Add", fill out the details, and then click the "Save New" button. Always be sure to chant "Save File" after any changes!
- Click "Settings" to set command line parameters, allowing you to override webring's true name, description, and other config file values.
- Tap "Generate Webring" and watch [ringfairy](https://github.com/k3rs3d/ringfairy) magically write HTML into the output directory.

Find your HTML artifacts in the output folder you chose. 
