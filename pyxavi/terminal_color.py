class TerminalColor:
    # Normal colors
    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    LILA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'

    # Double point (bold?) colors
    BLACK_INTENSE = '\033[1;30m'
    RED_INTENSE = '\033[1;31m'
    GREEN_INTENSE = '\033[1;32m'
    YELLOW_INTENSE = '\033[1;33m'
    BLUE_INTENSE = '\033[1;34m'
    LILA_INTENSE = '\033[1;35m'
    CYAN_INTENSE = '\033[1;36m'
    WHITE_INTENSE = '\033[1;37m'

    # Style
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    # To terminate the style in the string. Mandatory!
    END = '\033[0m'
