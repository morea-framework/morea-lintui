morea-lintui is a Morea content validator (like lint for C) and Morea content editor (via a Text User Interface, or tui).

The content validator:

  - Checks YAML syntax (more precisely than jekyll)
  - Checks that every reference to a Morea id is valid
  - Performs ype-checking of references
  - Checks for value collisions
  - Issues warnings for potentially dangerous behavior
  

The content editor:

  - Provides a simple way to view Morea content
  - Provides a simple way to edit parts of the Morea content


## Installation

Lintui (for now) requires Python 2.7.  A Python 3 version is forthcoming.

  - Install Python 2.7, if not already installed on your system

  - Download this entire repo as a zip file, unzip, and execute: <tt>sudo python setup.py install</tt> in the package's top directory.  In addition to installing this system, the installer will also install the urwid and the PyYaml packages.

Once the installation is done, <tt>morea-lintui</tt> should be available on your PATH as a command.
  
## Invocation

<tt>morea-lintui</tt> should be invoked from a Morea root directory (i.e., from a location in which either 
    the <tt>master/src/morea/</tt> or the <tt>src/morea</tt> directory is visible)
    
Here are typical invocations:

  - <tt>morea-lintui</tt>
    - Validates the Morea content, printing error and warning messages

  - <tt>morea-lintui --parse-comments</tt>
    - Same as above, but also validates commented-out Yaml content

  - <tt>morea-lintui --parse-comments --tui</tt>
    - Validate content and launch the Text User Interface

All the above executions first display some information and warnings, which can be avoided via the <tt>--no-splash</tt> command-line option.

<tt>morea-lintui --help</tt> lists all command-line options. 


## TUI usage

The use of the Text User Interface is intuitive. Use the direction arrows to navigate, <space> or <enter> to select, and the hot keys listed at the top and bottom of the interface to change view, save, cancel, quit, etc.

### Manage module-level structure

The Modules page lists all the Modules in your site and allows you to manipulate various properties (Published, Coming Soon, hightlight), and change the order in which they appear in the published site:

![](https://raw.githubusercontent.com/morea-framework/morea-lintui/master/morealintui/docs/screenshot1.jpg)

### Manage all content

You can view all other Morea content, structured by referencing module

![](https://raw.githubusercontent.com/morea-framework/morea-lintui/master/morealintui/docs/screenshot2.jpg)


### Manage file content

Each Morea .md file can be viewed/edited  (modify ordering in lists, commenting/uncommenting, simple tex editing of some fields):

![](https://raw.githubusercontent.com/morea-framework/morea-lintui/master/morealintui/docs/screenshot3.jpg)

