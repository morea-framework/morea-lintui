# morea-lintui

Morea content validator (like lint for C) and Morea content editor (via a Text User Interface, or tui).

Required Python packages:

  - [urwid](http://urwid.org)
  - [PyYaml] (http://pyyaml.org)
  - curses

The content validator does:

  - Check YAML syntax (more precisely than jekyll)
  - Check that every reference to a Morea id is valid
  - Type-checking of references
  - Checking for value collisions
  - Issue warnings for potentially dangerous behavior


The content editor does:

  - Provide a simple way to view Morea content
  - Provide a simple way to edit parts of the Morea content


Here is a screenshot of the content editor TUI:

<img src="https://github.com/morea-framework/morea-lintui/blob/master/docs/morea_lintui.jpg">