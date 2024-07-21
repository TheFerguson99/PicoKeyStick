ansi_codes = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m"
}
def InColor(text,*effects):
    effect_string = "".join(ansi_codes[effect] for effect in effects)
    return f"{effect_string}{text}{ansi_codes['RESET']}"
