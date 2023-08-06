from __future__ import unicode_literals
from .output_adapter import OutputAdapter

import win32com.client as wincl
speak = wincl.Dispatch("SAPI.SpVoice")

class TerminalAdapter(OutputAdapter):
    """
    A simple adapter that allows mitoo to
    communicate through the terminal.
    """

    def process_response(self, statement, session_id=None):
        """
        Print the response to the user's input.
        """
        speak.Speak(statement)
        print(statement.text)
        return statement.text
