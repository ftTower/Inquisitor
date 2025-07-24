# utils.py
import time

def return_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def log_exit(to_print):
    print(f"{colored('[  EXIT ]', BLACK, styles=[BLINK])} : {to_print}")

def log_info(to_print):
    print(f"{colored('[ INFOS ]', BLUE, styles=[BOLD])} : {to_print}")

def log_warning(to_print):
    print(f"{colored('[WARNING]', YELLOW, styles=[BOLD])} : {to_print}")

def log_error(to_print):
    print(f"{colored('[ ERROR ]', RED, styles=[BOLD])} : {to_print}")

def log_success(to_print):
    print(f"{colored('[SUCCESS]', GREEN, styles=[BOLD])} : {to_print}")

def log_debug(to_print):
    print(f"{colored('[ DEBUG ]', MAGENTA, styles=[BOLD])} : {to_print}")


ERASE_LINES = True 

# Codes de réinitialisation/reset
RESET = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m" # Peut ne pas fonctionner dans tous les terminaux
REVERSE = "\033[7m" # Inverse les couleurs d'avant-plan et d'arrière-plan
HIDDEN = "\033[8m" # Cache le texte
STRIKETHROUGH = "\033[9m"

# Couleurs de premier plan (texte)
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BRIGHT_BLACK = "\033[90m"  # Gris
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# Couleurs d'arrière-plan (fond)
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"
BG_BRIGHT_BLACK = "\033[100m" # Gris foncé
BG_BRIGHT_RED = "\033[101m"
BG_BRIGHT_GREEN = "\033[102m"
BG_BRIGHT_YELLOW = "\033[103m"
BG_BRIGHT_BLUE = "\033[104m"
BG_BRIGHT_MAGENTA = "\033[105m"
BG_BRIGHT_CYAN = "\033[106m"
BG_BRIGHT_WHITE = "\033[107m"
# Efface la ligne courante
ERASE_LINE = "\033[2K"
# Efface de la position du curseur jusqu'au début de la ligne
ERASE_LINE_START = "\033[1K"
# Efface de la position du curseur jusqu'à la fin de la ligne
ERASE_LINE_END = "\033[0K"
# Efface l'écran depuis le curseur jusqu'en haut
ERASE_SCREEN_UP = "\033[1J"
# Efface l'écran depuis le curseur jusqu'en bas
ERASE_SCREEN_DOWN = "\033[0J"

def erase_lines(n=1):
    seq = ""
    if ERASE_LINES == False:
        return seq
    for i in range(n):
        seq += ERASE_LINE
        if i < n - 1:
            seq += "\033[1A"
    return seq
def colored(text, foreground=None, background=None, styles=None):
    codes = []
    if text is None:
        return ""
    if foreground:
        codes.append(foreground)
    if background:
        codes.append(background)
    if styles:
        codes.extend(styles)

    if not codes:
        return text

    return "".join(codes) + text + RESET
    return "".join(codes) + text + RESET