"""
This is a Python code with several methods that simplify
routines related to the Linux terminal.
"""


def text_colored(color, text):
    """
    This Python program takes in a color name and a text input from the
    user, and then converts the text into ANSI output sequences that will
    render the text in the chosen color.
    """
    color_list = {
        "reset": "\033[0m",
        "bold": "\033[01m",
        "disable": "\033[02m",
        "underline": "\033[04m",
        "reverse": "\033[07m",
        "strikethrough": "\033[09m",
        "invisible": "\033[08m",
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "orange": "\033[33m",
        "blue": "\033[34m",
        "purple": "\033[35m",
        "cyan": "\033[36m",
        "lightgrey": "\033[37m",
        "darkgrey": "\033[90m",
        "lightred": "\033[91m",
        "lightgreen": "\033[92m",
        "yellow": "\033[93m",
        "lightblue": "\033[94m",
        "pink": "\033[95m",
        "lightcyan": "\033[96m",
        "bgblack": "\033[40m",
        "bgred": "\033[41m",
        "bggreen": "\033[42m",
        "bgorange": "\033[43m",
        "bgblue": "\033[44m",
        "bgpurple": "\033[45m",
        "bgcyan": "\033[46m",
        "bglightgrey": "\033[47m",
    }

    return f"{color_list[color]}{text}{color_list['reset']}"
