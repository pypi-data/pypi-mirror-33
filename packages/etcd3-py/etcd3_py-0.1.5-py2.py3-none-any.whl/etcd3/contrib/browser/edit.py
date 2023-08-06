#!/usr/bin/python

"""
Usage:
edit.py <filename>
"""

import sys

import urwid

import pygments
from pygments.lexers.python import PythonLexer

palette = [
    ('body','default', 'default'),
    ('foot','dark cyan', 'dark blue', 'bold'),
    ('key','light cyan', 'dark blue', 'underline'),
    ('reversed','light cyan', 'dark blue', 'underline'),
    (pygments.token.Comment, urwid.LIGHT_GRAY, urwid.DEFAULT),
    (pygments.token.Literal.String.Doc, urwid.LIGHT_RED, urwid.DEFAULT),
    (pygments.token.Name.Namespace, urwid.LIGHT_BLUE, urwid.DEFAULT),
    (pygments.token.Name.Builtin, urwid.DARK_CYAN, urwid.DEFAULT),
    (pygments.token.Text, urwid.WHITE, urwid.DEFAULT),
    (pygments.token.Operator.Word, urwid.DARK_GREEN, urwid.DEFAULT),
    (pygments.token.Name, urwid.WHITE, urwid.DEFAULT),
    (pygments.token.Punctuation, urwid.WHITE, urwid.DEFAULT),
    (pygments.token.Keyword, urwid.DARK_GREEN, urwid.DEFAULT),
    (pygments.token.Name.Function, urwid.LIGHT_BLUE, urwid.DEFAULT),
    (pygments.token.Name.Class, urwid.LIGHT_BLUE, urwid.DEFAULT),
    (pygments.token.Keyword.Namespace, urwid.DARK_GREEN, urwid.DEFAULT),
    (pygments.token.Name.Builtin.Pseudo, urwid.DARK_CYAN, urwid.DEFAULT),
    (pygments.token.Operator, urwid.WHITE, urwid.DEFAULT),
    (pygments.token.Literal.Number.Integer, urwid.DARK_RED, urwid.DEFAULT),
    (pygments.token.Literal.String, urwid.LIGHT_RED, urwid.DEFAULT),
    ]

def split_tokens(tokens):
    """Split output of Formatter.get_tokens on newlines"""

    sentence = []
    #for (_, token, word) in tokens:
    for (token, word) in tokens:
        lines = word.split("\n")

        # If there are no newlines, we can simply add the
        # token to the current sentence
        sentence.append((token, lines.pop(0)))

        # If there are any newlines in this token,
        # then split on them
        for line in lines:
            yield sentence
            sentence = []
            sentence.append((token, line))

class LineWalker(urwid.ListWalker):
    def __init__(self):
        self.lines = []
        self.focus = 0

    def set_focus(self, pos):
        self.focus = pos

    def get_focus(self):
        return self.get_at_pos(self.focus)

    def get_prev(self, start_from):
        return self.get_at_pos(start_from - 1)

    def get_next(self, start_from):
        return self.get_at_pos(start_from + 1)

    def get_at_pos(self, pos):
        if pos < 0 or pos >= len(self.lines):
            return None, None
        else:
            return self.lines[pos], pos

    def load_text(self, text):
        for line in text.split("\n"):
            self.lines.append(Line(line))
        self.reformat()

    def count_empty_lines_start(self):
        """Find the first non-empty line."""
        i = 0
        while i < len(self.lines) and len(self.lines[i].edit_text.strip()) == 0:
            i += 1
        return i

    def reformat(self):
        # Unfortunately, pygments does some preprocessing, which we need to
        # hack around.
        # Pygments starts highlighting from the first non-empty line
        start = 0 #self.count_empty_lines_start()
        text = "\n".join(line.edit_text for line in self.lines)

        tokens = list(PythonLexer(stripnl=False, stripall=False, ensurenl=False, tabsize=0)
                .get_tokens(text))
        #tokens = list(PythonLexer().get_tokens_unprocessed(text))
        for i, sentence in enumerate(split_tokens(tokens)):
            i += start
            if sentence:
                t, l = urwid.Text(sentence).get_text()
                self.lines[i].formatting = l
            else:
                self.lines[i].formatting = None

    def clear(self):
        self.lines = []

    def split(self):
        focus = self.lines[self.focus]
        pos = focus.edit_pos
        edit = Line(focus.edit_text[pos:])
        #edit.original_text = "" #why?
        #edit.set_edit_pos(0) # really?
        focus.set_edit_text(focus.edit_text[:pos])
        self.lines.insert(self.focus+1, edit)

    def combine_focus_with_prev(self):
        above, _ = self.get_prev(self.focus)
        if above is not None:
            focus = self.lines[self.focus]
            above.set_edit_pos(len(above.edit_text))
            above.set_edit_text(above.edit_text + focus.edit_text)
            del self.lines[self.focus]
            self.focus -= 1

    def combine_focus_with_next(self):
        below, bi = self.get_next(self.focus)
        if below is not None:
            focus = self.lines[self.focus]
            focus.set_edit_text(focus.edit_text + below.edit_text)
            del self.lines[bi]

    # Maybe these will be useful later
    #def get_char_at_pos(self, lp):
        #line_pos, edit_pos = lp
        #line, line_pos = self.get_at_pos(line_pos)
        #return line[line_pos]

    #def get_next_char(self, lp):
        #line_pos, edit_pos = lp
        #line, line_pos = self.get_at_pos(line_pos)
        #if line_pos < len(line.edit_text):
            #return get_char_at_pos((line_pos, edit_pos + 1))
        #else:
            #return get_char_at_pos((line_pos + 1, 0))

    #def get_previous_char(self, lp):
        #line_pos, edit_pos = lp
        #line, line_pos = self.get_at_pos(line_pos)
        #if line_pos > 0:
            #return get_char_at_pos((line_pos, edit_pos - 1))
        #else:
            #previous_line, no = get_at_pos(line_pos - 1)
            #return get_char_at_pos((no - 1, len(previous_line.edit_text)))

class Line(urwid.Edit):
    def __init__(self, line="", formatting=None):
        super(Line, self).__init__("", line.expandtabs(), allow_tab=True)
        self.set_edit_pos(0)
        self.original_text = line
        self.formatting = formatting

    def get_text(self):
        text = super(Line, self).get_text()
        if self.formatting:
            return text[0], self.formatting
        else:
            return text

class Editor(urwid.ListBox):
    def keypress(self, size, key):
        """This just behavious like a standard editor"""

        # Normal line splitting behaviour
        if key == "enter":
            self.body.split()
            super(Editor, self).keypress(size, "down")
            super(Editor, self).keypress(size, "home")
            self.body.reformat()
        elif key == "backspace":
            if super(Editor, self).keypress(size, key):
                self.body.combine_focus_with_prev()
            self.body.reformat()
        elif key == "delete":
            if super(Editor, self).keypress(size, key):
                self.body.combine_focus_with_next()
            self.body.reformat()

        # Basic navigation
        elif key == "right":
            self.forward_char(size)
        elif key == "left":
            self.backward_char(size)
        elif key == "meta f":
            self.forward_word(size)
        elif key == "meta b":
            self.backward_word(size)
        elif key == "ctrl a":
            super(Editor, self).keypress(size, "home")
        elif key == "ctrl e":
            super(Editor, self).keypress(size, "end")

        # Passthrough
        else:
            super(Editor, self).keypress(size, key)
            self.body.reformat()

    def forward_char(self, size):
        if super(Editor, self).keypress(size, "right"):
            w, pos = self.body.get_focus()
            w, pos = self.body.get_next(pos)
            if w:
                self.set_focus(pos, "above")
                self.keypress(size, "home")

    def backward_char(self, size):
        if super(Editor, self).keypress(size, "left"):
            w, pos = self.body.get_focus()
            w, pos = self.body.get_prev(pos)
            if w:
                self.set_focus(pos, "below")
                self.keypress(size, "end")

    # FIXME end of file problem
    def forward_word(self, size):

        # Why were these swapped?
        self.forward_char(size)
        line, no = self.body.get_focus()

        # Advance until the current word has ended
        while line.edit_pos < len(line.edit_text) and not line.edit_text[line.edit_pos].isspace():
            self.forward_char(size)
            line, no = self.body.get_focus()

        # Advance until the next word starts
        while line.edit_pos >= len(line.edit_text) or line.edit_text[line.edit_pos].isspace():
            self.forward_char(size)
            line, no = self.body.get_focus()

    # TODO begin of file problem
    def backward_word(self, size):
        self.backward_char(size)
        line, no = self.body.get_focus()

        # Advance until cursor is on a word
        while line.edit_pos >= len(line.edit_text) or line.edit_text[line.edit_pos].isspace():
            self.backward_char(size)
            line, no = self.body.get_focus()

        # Advance until beginning of word
        while line.edit_pos < len(line.edit_text) and not line.edit_text[line.edit_pos].isspace():
            self.backward_char(size)
            line, no = self.body.get_focus()

        self.forward_char(size)

class VoFrame(urwid.Frame):
    def __init__(self, *args, **kw):
        super(VoFrame, self).__init__(*args, **kw)
        self.mode = "insert"

    def keypress(self, size, key):
        "This becomes vim like"
        if self.mode == "insert":
            if key == "esc":
                self.mode = "normal"
            else:
                self.body.keypress(size, key)
        elif self.mode == "normal":
            if key == "i":
                self.mode = "insert"
            elif key == "h":
                self.body.keypress(size, "left")
            elif key == "l":
                self.body.keypress(size, "right")
            elif key == "k":
                self.body.keypress(size, "up")
            elif key == "j":
                self.body.keypress(size, "down")
            # FIXME
            elif key == "ctrl b":
                self.body.keypress(size, "page up")
            elif key == "ctrl f":
                self.body.keypress(size, "page down")

class Main(object):
    def __init__(self):
        """@todo: Docstring for __init__.
        :returns: @todo
        """

        self.linewalker = LineWalker()
        if len(sys.argv) > 1:
            text = open(sys.argv[1]).read()
        else:
            text = open(__file__).read()

        # Something needs to be loaded or it will crash
        self.linewalker.load_text(text)

        self.listbox = Editor(self.linewalker)
        #self.top = urwid.Frame(self.listbox)
        self.top = VoFrame(self.listbox)

        self.loop = urwid.MainLoop(self.top, palette=palette)#,
                #unhandled_input=self.unhandled_keypress)

    def main(self):
        self.loop.run()

    def unhandled_keypress(self, key):
        if key == "f1":
            print("behhh")
            self.linewalker.reformat()
        pass
        print(key)

if __name__ == '__main__':
    main = Main()
    main.main()
