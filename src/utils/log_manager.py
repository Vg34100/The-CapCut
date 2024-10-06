from logging import basicConfig, INFO, info, warning, error

# Terminal color definitions
class fg:
    BLACK   = '\033[30m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'
    RESET   = '\033[39m'

class bg:
    BLACK   = '\033[40m'
    RED     = '\033[41m'
    GREEN   = '\033[42m'
    YELLOW  = '\033[43m'
    BLUE    = '\033[44m'
    MAGENTA = '\033[45m'
    CYAN    = '\033[46m'
    WHITE   = '\033[47m'
    RESET   = '\033[49m'

class style:
    BRIGHT    = '\033[1m'
    DIM       = '\033[2m'
    NORMAL    = '\033[22m'
    RESET_ALL = '\033[0m'

def log_info(message: str) -> None:
    """Log an info message."""
    info(message)
    print(message)

def log_warning(message: str) -> None:
    """Log a warning message."""
    warning(message)
    print(f"{fg.YELLOW}{message}{style.RESET_ALL}")

def log_error(message: str) -> None:
    """Log an error message."""
    error(message)
    print(f"{fg.RED}{message}{style.RESET_ALL}")

def log_attribute(message: str) -> None:
    """Logs an attribute."""
    info(f"Logging attribute: {message}")
    print(f"{fg.BLUE}{message}{style.RESET_ALL}")
    
def ask_input(message: str, expected_type: type = str):
    """Prompt the user for input with a custom message and terminal colors.
    Optionally converts the input to the specified type."""
    while True:
        try:
            answer = input(f"{fg.YELLOW}{message}{style.RESET_ALL}: {fg.CYAN}")
            print(style.RESET_ALL, end='')  # Ensure that reset style is applied
            if expected_type == int:
                return int(answer)
            elif expected_type == float:
                return float(answer)
            return answer  # Default is str
        except ValueError:
            log_error(f"Invalid input. Please enter a valid {expected_type.__name__}.")
        except Exception as e:
            log_error(f"Error getting user input: {e}")
            return None