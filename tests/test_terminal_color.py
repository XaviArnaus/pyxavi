from pyxavi.terminal_color import TerminalColor
import pytest


@pytest.mark.parametrize(
    argnames=('color_test', 'code'),
    argvalues=[
        (f"{TerminalColor.BLACK}This is black{TerminalColor.END}", "\033[0;30m"),
        (f"{TerminalColor.RED}This is red{TerminalColor.END}", "\033[0;31m"),
        (f"{TerminalColor.GREEN}This is green{TerminalColor.END}", "\033[0;32m"),
        (f"{TerminalColor.YELLOW}This is yellow{TerminalColor.END}", "\033[0;33m"),
        (f"{TerminalColor.BLUE}This is blue{TerminalColor.END}", "\033[0;34m"),
        (f"{TerminalColor.MAGENTA}This is MAGENTA{TerminalColor.END}", "\033[0;35m"),
        (f"{TerminalColor.CYAN}This is cyan{TerminalColor.END}", "\033[0;36m"),
        (f"{TerminalColor.WHITE}This is white{TerminalColor.END}", "\033[0;37m"),
        (f"{TerminalColor.BLACK_BRIGHT}This is black{TerminalColor.END}", "\033[1;30m"),
        (f"{TerminalColor.RED_BRIGHT}This is red{TerminalColor.END}", "\033[1;31m"),
        (f"{TerminalColor.GREEN_BRIGHT}This is green{TerminalColor.END}", "\033[1;32m"),
        (f"{TerminalColor.YELLOW_BRIGHT}This is yellow{TerminalColor.END}", "\033[1;33m"),
        (f"{TerminalColor.BLUE_BRIGHT}This is blue{TerminalColor.END}", "\033[1;34m"),
        (f"{TerminalColor.MAGENTA_BRIGHT}This is MAGENTA{TerminalColor.END}", "\033[1;35m"),
        (f"{TerminalColor.CYAN_BRIGHT}This is cyan{TerminalColor.END}", "\033[1;36m"),
        (f"{TerminalColor.WHITE_BRIGHT}This is white{TerminalColor.END}", "\033[1;37m"),
        (f"{TerminalColor.BOLD}This is bold{TerminalColor.END}", "\033[1m"),
        (f"{TerminalColor.UNDERLINE}This is underline{TerminalColor.END}", "\033[4m"),
    ],
)
def test_dd(color_test, code):

    assert code in color_test and "\033[0m" in color_test
