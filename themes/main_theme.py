from colorama import Fore, Back, Style

# self.version = Shows Version
# title = Shows the title 
# self.items = Shows a list of every item
# self.buys = Shows every success buy
# self.errors = Shows every error occured
# self.last_time = Shows the last execution time
# self.checks = Shows total price checks
# self.task = Shows current task


title = ("""
▒██   ██▒ ▒█████   ██▓     ▒█████             ██████  ███▄    █  ██▓ ██▓███  ▓█████  ██▀███  
▒▒ █ █ ▒░▒██▒  ██▒▓██▒    ▒██▒  ██▒         ▒██    ▒  ██ ▀█   █ ▓██▒▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒
░░  █   ░▒██░  ██▒▒██░    ▒██░  ██▒         ░ ▓██▄   ▓██  ▀█ ██▒▒██▒▓██░ ██▓▒▒███   ▓██ ░▄█ ▒
 ░ █ █ ▒ ▒██   ██░▒██░    ▒██   ██░           ▒   ██▒▓██▒  ▐▌██▒░██░▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  
▒██▒ ▒██▒░ ████▓▒░░██████▒░ ████▓▒░         ▒██████▒▒▒██░   ▓██░░██░▒██▒ ░  ░░▒████▒░██▓ ▒██▒
▒▒ ░ ░▓ ░░ ▒░▒░▒░ ░ ▒░▓  ░░ ▒░▒░▒░          ▒ ▒▓▒ ▒ ░░ ▒░   ▒ ▒ ░▓  ▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░
░░   ░▒ ░  ░ ▒ ▒░ ░ ░ ▒  ░  ░ ▒ ▒░          ░ ░▒  ░ ░░ ░░   ░ ▒░ ▒ ░░▒ ░      ░ ░  ░  ░▒ ░ ▒░
 ░    ░  ░ ░ ░ ▒    ░ ░   ░ ░ ░ ▒           ░  ░  ░     ░   ░ ░  ▒ ░░░          ░     ░░   ░ 
 ░    ░      ░ ░      ░  ░    ░ ░                 ░           ░  ░              ░  ░   ░     
                                                                                             
""")
def _print_stats(self) -> None:
        print(f"Version: {self.version}")
        print(Fore.GREEN + Style.BRIGHT + title)
        print(Fore.RESET + Style.RESET_ALL)
        print(Style.BRIGHT + f"                           [ Loaded items: {Fore.GREEN}{Style.BRIGHT}{len(self.items)}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Total buys: {Fore.GREEN}{Style.BRIGHT}{self.buys}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Total errors: {Fore.RED}{Style.BRIGHT}{self.errors}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Last Speed: {Fore.YELLOW}{Style.BRIGHT}{self.last_time}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Total price checks: {Fore.YELLOW}{Style.BRIGHT}{self.checks}{Fore.WHITE}{Style.BRIGHT} ]")
        print()
        print(Style.BRIGHT + f"                           [ Current Task: {Fore.GREEN}{Style.BRIGHT}{self.task}{Fore.WHITE}{Style.BRIGHT} ]")
