from colorama import Back, Fore, Style, init

def padding(length):
    return " " * length

def yellow(string):
    return Fore.YELLOW + string + Style.RESET_ALL

def green(string):
    return Fore.GREEN + string + Style.RESET_ALL

def blue(string):
    return Fore.BLUE + string + Style.RESET_ALL
