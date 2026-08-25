"""
Keyboard event processing module for TypeMaster.
Provides helpers for interpreting GUI keypress elements into characters or control actions.
"""

def process_key_event(event) -> tuple[str, str | None]:
    """
    Interprets a Tkinter keypress event.
    Returns a tuple (action, value):
      - ("backspace", None) for Backspace key
      - ("input", char) for valid printable characters
      - ("ignore", None) for control/utility keys (Esc, Shift, Control, Tab, etc.)
    """
    if not event:
        return "ignore", None
        
    keysym = getattr(event, "keysym", None)
    char = getattr(event, "char", None)
    
    if keysym == "BackSpace":
        return "backspace", None
        
    # Check if char exists and is a single printable character.
    # Exclude control characters like Tab (\t), Carriage Return (\r), and Newline (\n)
    if char and len(char) == 1 and char.isprintable() and char not in ("\t", "\r", "\n"):
        return "input", char
        
    return "ignore", None
