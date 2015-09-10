import copy
import urwid

__author__ = 'casanova'
import curses



def launch(_content):
    # Make a deep copy of content
    content = copy.deepcopy(_content)


    def exit_on_q(key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    class QuestionBox(urwid.Filler):
        def keypress(self, size, key):
            if key != 'enter':
                return super(QuestionBox, self).keypress(size, key)
            self.original_widget = urwid.Text(
                u"Nice to meet you,\n%s.\n\nPress Q to exit." %
                edit.edit_text)

    edit = urwid.Edit(u"What is your name?\n")
    fill = QuestionBox(edit)
    loop = urwid.MainLoop(fill, unhandled_input=exit_on_q)
    loop.run()


    # Set up the screencurses.noecho()
    # stdscr = curses.initscr()
    # curses.noecho()
    # curses.cbreak()
    # stdscr.keypad(1)
    # win = curses.newwin(50, 50)
    # DO NOTHING
    # curses.flash()
    # reset terminal properties
    # curses.nocbreak()
    # stdscr.keypad(0)
    # curses.echo()
    # curses.endwin()

    return content
