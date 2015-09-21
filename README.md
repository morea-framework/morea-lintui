# morea-lintui

## Overview

morea-lintui is a Morea content validator (like lint for C) and Morea content editor (via a Text User Interface, or tui).

The content validator does:

  - Check YAML syntax (more precisely than jekyll)
  - Check that every reference to a Morea id is valid
  - Perform ype-checking of references
  - Check for value collisions
  - Issue warnings for potentially dangerous behavior
  

The content editor does:

  - Provide a simple way to view Morea content
  - Provide a simple way to edit parts of the Morea content


## Installation

Lintui (for now) requires Python 2.7.  A Python 3 version is forthcoming.

  - Install Python 2.7, if not already installed on your system (which comes with the pip package manager since Python 2.7.9)
    - If you don't have pip: <tt>sudo apt-get install python-pip</tt>
  - Install the [urwid](http://urwid.org) package (command: <tt>sudo pip-2.7 install urwid</tt>)
  - Install the [PyYaml] (http://pyyaml.org) package (command: <tt>sudo pip-2.7 install PyYaml</tt>)
  - Download this package and make <tt>morea-lintui.py</tt> (top directory) executable and have your path point to it
  
## User guide

<tt>morea-lintui.py</tt> should be invoked from a Morea root directory (i.e., from a location in which either 
    the <tt>master/src/morea/</tt> or the <tt>src/morea</tt> directory is visible)
    
Here are typical invocations:

  - <tt>morea-lintui.py</tt>
    - Validates the Morea content, printing error and warning messages
  - <tt>morea-lintui.py --parse-comments</tt>
    - Same as above, but also validates commented-out Yaml content
  - <tt>morea-lintui.py --parse-comments --tui</tt>
    - Validate content and launch the Text User Inferface

All the above executions first display some information and warnings, which can be avoided via the <tt>--no-splash</tt> command-line option.

<tt>morea-lintui.py --help</tt> lists all command-line options. 
  
The use of the Text User Interface is intuitive. Use the direction arrows to navigate, <space> or <enter> to select, and the hot keys listed at the top and bottom of the interface to change view, save, cancel, quit, etc.

## Screenshot

Here are some screenshots of the content editor TUI:

<img src="https://github.com/morea-framework/morea-lintui/blob/master/docs/screenshot1.jpg">

<img src="https://github.com/morea-framework/morea-lintui/blob/master/docs/screenshot2.jpg">

<img src="https://github.com/morea-framework/morea-lintui/blob/master/docs/screenshot3.jpg">
