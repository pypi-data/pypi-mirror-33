from termcolor_util import yellow, green, blue, red, gray, cyan, magenta, white


if __name__ == '__main__':
    print(cyan("termcolor_util"),
          cyan("v1.0.0", bold=True))

    for color in [yellow, green, blue, red, gray, cyan, magenta, white]:
        print(color(color.__name__),
              color(color.__name__, underline=True),
              color(color.__name__, bold=True),
              color(color.__name__, bold=True, underline=True))
