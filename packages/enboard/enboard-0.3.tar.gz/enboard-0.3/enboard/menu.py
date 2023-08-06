"""

Parts of this copied from prompt_toolkit, which is BSD licensed:

Copyright (c) 2014, Jonathan Slenders
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

* Neither the name of the {organization} nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import functools
import re
import subprocess
from prompt_toolkit.application import Application, get_app, run_in_terminal
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.formatted_text import PygmentsTokens, to_formatted_text
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import HasFocus
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window, ConditionalContainer
from prompt_toolkit.layout.controls import (BufferControl, FormattedTextControl,
    UIControl, UIContent)
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.layout.screen import Point
from prompt_toolkit.styles import style_from_pygments_dict
from prompt_toolkit.utils import get_cwidth
from prompt_toolkit.widgets import HorizontalLine
from pygments.token import Token

from .envs import find_envs

def _trim_text(text, max_width):
    """
    Trim the text to `max_width`, append dots when the text is too long.
    Returns (text, width) tuple.
    
    Copied from prompt_toolkit
    """
    width = get_cwidth(text)

    # When the text is too wide, trim it.
    if width > max_width:
        # When there are no double width characters, just use slice operation.
        if len(text) == width:
            trimmed_text = (text[:max(1, max_width-3)] + '...')[:max_width]
            return trimmed_text, len(trimmed_text)

        # Otherwise, loop until we have the desired width. (Rather
        # inefficient, but ok for now.)
        else:
            trimmed_text = ''
            for c in text:
                if get_cwidth(trimmed_text + c) <= max_width - 3:
                    trimmed_text += c
            trimmed_text += '...'

            return (trimmed_text, get_cwidth(trimmed_text))
    else:
        return text, width

class MenuControl(UIControl):
    def __init__(self, items):
        self.items = items
        self.selected_ix = 0
        self.search_buffer = Buffer(name='search',
                        on_text_changed=lambda sender: self.select_visible())
        self.new_name_buffer = Buffer(name='new_name')

    def is_focusable(self):
        return True

    def visible_indices(self):
        search = self.search_buffer.document.text
        i = 0
        for j, item in enumerate(self.items):
            if item.display.startswith(search):
                yield i, j
                i += 1
    
    def create_content(self, width, height):
        visible_indices = dict(self.visible_indices())
        
        def get_line(i):
            if i not in visible_indices:
                return to_formatted_text(PygmentsTokens([(Token.MenuItem, ' ' * width)]))
            j = visible_indices[i]
            is_selected = (j == self.selected_ix)
            item = self.items[j]
            return to_formatted_text(PygmentsTokens(self._get_menu_item_tokens(item, is_selected, width)))
        
        return UIContent(get_line=get_line,
                         cursor_position=Point(x=0, y=self.selected_ix or 0),
                         line_count=len(visible_indices),
                        )
        
    def _get_menu_item_tokens(self, item, is_selected, width):
        if is_selected:
            token = Token.MenuItem.Current
        else:
            token = Token.MenuItem

        text, tw = _trim_text(item.display, width - 2)
        padding = ' ' * (width - 2 - tw)
        return [(token, ' %s%s ' % (text, padding))]
    
    def preferred_height(self, width, max_available_height, wrap_lines):
        return max(len(self.items), max_available_height)

    @property
    def selected(self):
        return self.items[self.selected_ix]

    def select_visible(self, direction='forwards'):
        visible_indices = set(j for (i,j) in self.visible_indices())
        if not visible_indices:
            self.selected_ix = len(self.items)  # Nothing selected
            return

        ix = self.selected_ix
        if direction=='forwards':
            lim = max(visible_indices)
            if ix > lim:
                self.selected_ix = lim
                return
            delta = +1
        else:
            lim = min(visible_indices)
            if ix < lim:
                self.selected_ix = lim
                return
            delta = -1
        
        while ix not in visible_indices:
            ix += delta
        self.selected_ix = ix

def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `CommandLineInterface.run()` call.
    """
    event.cli.exit(result=None)

def up(event):
    menu = event.cli.menu_control
    menu.selected_ix -= 1
    menu.select_visible(direction='backwards')

def down(event):
    menu = event.cli.menu_control
    menu.selected_ix += 1
    menu.select_visible(direction='forwards')

def select(event):
    menu = event.cli.menu_control
    try:
        event.cli.exit(result=menu.selected)
    except IndexError:
        pass

def newenv(name):
    subprocess.run(['conda', 'create', '-y', '-n', name, 'python=3'])

def newenv_event(event):
    name = event.cli.current_buffer.document.text
    run_in_terminal(functools.partial(newenv, name))
    event.cli.current_buffer.reset()
    event.cli.layout.focus(event.cli.menu_control)
    event.cli.menu_control.items = find_envs()
    event.cli.menu_control.selected_ix = 0

def delete(event):
    menu = event.cli.menu_control
    try:
        menu.selected.delete()
    except IndexError:
        return
    menu.items = find_envs()

def start_search(event):
    event.cli.layout.focus('search')

def start_newenv(event):
    event.cli.layout.focus('new_name')

def cancel_entry(event):
    event.cli.current_buffer.reset()
    event.cli.layout.focus(event.cli.menu_control)

searching = HasFocus('search')
new_entry = HasFocus('new_name')
no_focus = ~(searching | new_entry)

def bind_shortcuts(bindings):
    bindings.add('q', filter=no_focus)(exit_)
    bindings.add(Keys.Up)(up)
    bindings.add(Keys.Down)(down)
    bindings.add(Keys.ControlN)(down)
    bindings.add(Keys.ControlP)(up)
    bindings.add(Keys.ControlM, filter=~new_entry)(select)
    bindings.add(Keys.ControlM, filter=new_entry)(newenv_event)
    bindings.add(Keys.Delete, filter=~new_entry)(delete)
    bindings.add('/', filter=no_focus)(start_search)
    bindings.add('n', filter=no_focus)(start_newenv)
    bindings.add(Keys.ControlC, filter=(searching | new_entry))(cancel_entry)

def shortcut_tokens(s):
    m = re.match(r'\[(.+)\](.+)$', s)
    if m:
        return [
            (Token.Toolbar.Key, m.group(1)),
            (Token.Toolbar, m.group(2)),
        ]
    raise ValueError("Didn't recognise shortcut %r" % s)

def make_toolbar_tokens():
    app = get_app()
    if app.current_buffer.name == 'search':
        t = shortcut_tokens('[Enter]:Select') + [
            (Token.Toolbar, '  '),
        ] + shortcut_tokens('[Ctrl-C]:Cancel search')
    elif app.current_buffer.name == 'new_name':
        t = shortcut_tokens('[Enter]:Create') + [
            (Token.Toolbar, '  '),
        ] + shortcut_tokens('[Ctrl-C]:Cancel')
    else:
        t = shortcut_tokens('[Enter]:Select') + [
            (Token.Toolbar, '  '),
        ] + shortcut_tokens('[N]ew') + [
            (Token.Toolbar, '  '),
        ] + shortcut_tokens('[Del]ete') + [
            (Token.Toolbar, '  '),
        ] + shortcut_tokens('[Q]uit') + [
            (Token.Toolbar, '  '),
        ] + shortcut_tokens('[/]:Search')
    return PygmentsTokens(t)

def text_entry_toolbar(buffer, prompt):
    bc = BufferControl(buffer, input_processors=[
                          BeforeInput(PygmentsTokens([(Token.Prompt, prompt)]))
                      ])
    w = Window(bc)
    hff = HasFocus(buffer)
    return ConditionalContainer(w, filter=hff)

def create_menu_cli():
    kb = KeyBindings()
    bind_shortcuts(kb)
    menu = MenuControl(find_envs())

    layout = Layout(HSplit([
        # List of environments
        Window(content=menu),

        # Divider
        HorizontalLine(),

        # Search toolbar
        text_entry_toolbar(menu.search_buffer, 'Search: '),

        # New environment toolbar
        text_entry_toolbar(menu.new_name_buffer, 'New environment name: '),

        # Shortcut hints toolbar
        Window(content=FormattedTextControl(text=make_toolbar_tokens)),
    ]), focused_element=menu)

    style = style_from_pygments_dict({
        Token.MenuItem: '',
        Token.MenuItem.Current: 'reverse',
        Token.Toolbar.Key: 'bold',
    })

    #loop = create_eventloop()
    application = Application(key_bindings=kb, layout=layout,
                              full_screen=True, style=style)
                              # buffers=BufferMapping(initial=DUMMY_BUFFER),
                              # on_buffer_changed=buffer_changed,
    application.menu_control = menu
    return application
