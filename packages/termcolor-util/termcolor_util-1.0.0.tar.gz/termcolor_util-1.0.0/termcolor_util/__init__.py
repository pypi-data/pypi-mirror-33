from termcolor import colored


def yellow(text: str, bold=False, underline=False) -> str:
    attrs = []

    if bold:
        attrs.append("bold")

    if underline:
        attrs.append("underline")

    return colored(text, color="yellow", attrs=attrs)


def green(text: str, bold=False, underline=False) -> str:
    attrs = []

    if bold:
        attrs.append("bold")

    if underline:
        attrs.append("underline")

    return colored(text, color="green", attrs=attrs)


def blue(text: str, bold=False, underline=False) -> str:
    attrs = []

    if bold:
        attrs.append("bold")

    if underline:
        attrs.append("underline")

    return colored(text, color="blue", attrs=attrs)


def red(text: str, bold=False, underline=False) -> str:
    attrs = []

    if bold:
        attrs.append("bold")

    if underline:
        attrs.append("underline")

    return colored(text, color="red", attrs=attrs)


def gray(text: str, bold=False, underline=False) -> str:
    attrs = []

    if bold:
        attrs.append("bold")

    if underline:
        attrs.append("underline")

    return colored(text, color="grey", attrs=attrs)


def cyan(text: str, bold=False, underline=False) -> str:
    attrs = []

    if bold:
        attrs.append("bold")

    if underline:
        attrs.append("underline")

    return colored(text, color="cyan", attrs=attrs)


def magenta(text: str, bold=False, underline=False) -> str:
    attrs = []

    if bold:
        attrs.append("bold")

    if underline:
        attrs.append("underline")

    return colored(text, color="magenta", attrs=attrs)


def white(text: str, bold=False, underline=False) -> str:
    attrs = []

    if bold:
        attrs.append("bold")

    if underline:
        attrs.append("underline")

    return colored(text, color="white", attrs=attrs)
