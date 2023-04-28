import os
try:
   from rgbprint import Color
except:
    os.system("pip install rgbprint")

title = (f"""
{Color(0x6e34bb)}  ███▄▄▄▄    ▄█     ▄██████▄     ▄█    █▄        ███        ▄████████    ▄████████  ▄█        ▄█       
{Color(0x733cb6)}  ███▀▀▀██▄ ███    ███    ███   ███    ███   ▀█████████▄   ███    ███   ███    ███ ███       ███            _.._
{Color(0x7d4aae)}  ███   ███ ███▌   ███    █▀    ███    ███      ▀███▀▀██   ███    █▀    ███    ███ ███       ███          .' .-'`
{Color(0x8c5fa2)}  ███   ███ ███▌  ▄███         ▄███▄▄▄▄███▄▄     ███   ▀  ▄███▄▄▄       ███    ███ ███       ███         /  /
{Color(0x9d7794)}  ███   ███ ███▌ ▀▀███ ████▄  ▀▀███▀▀▀▀███▀      ███     ▀▀███▀▀▀     ▀███████████ ███       ███         |  |
{Color(0xae9186)}  ███   ███ ███    ███    ███   ███    ███       ███       ███          ███    ███ ███       ███         \  '.___.;
{Color(0xbfa978)}  ███   ███ ███    ███    ███   ███    ███       ███       ███          ███    ███ ███▌    ▄ ███▌    ▄    '._  _.'
{Color(0xcebe6c)}   ▀█   █▀  █▀     ████████▀    ███    █▀       ▄████▀     ███          ███    █▀  █████▄▄██ █████▄▄██       ``
{Color(0xd8cc64)}                                                                                   ▀         ▀         
{Color(0xddd45f)}                       > all we know is that stars will fall and holidays come and go <""")

def _print_stats(self) -> None:
    print(f"""{title}
 {Color(0xffffff)}-----------
  {Color(0x6e34bb)}Script  {Color(0xffffff)}:  {Color(0xddd45f)}xolo#4249
  {Color(0x6e34bb)}Theme   {Color(0xffffff)}:  {Color(0xddd45f)}SleepyLuc#9967
 {Color(0xffffff)}-----------
  {Color(0x6e34bb)}Version {Color(0xffffff)}:  {Color(0xddd45f)}{self.version}
  {Color(0x6e34bb)}Task    {Color(0xffffff)}:  {Color(0xddd45f)}{self.task}
 {Color(0xffffff)}-----------
  {Color(0x6e34bb)}Items   {Color(0xffffff)}:  {Color(0xddd45f)}{len(self.items)}
  {Color(0x6e34bb)}Snipes  {Color(0xffffff)}:  {Color(0xddd45f)}{self.buys}
  {Color(0x6e34bb)}Errors  {Color(0xffffff)}:  {Color(0xddd45f)}{self.errors}
  {Color(0x6e34bb)}Speed   {Color(0xffffff)}:  {Color(0xddd45f)}{self.last_time}
  {Color(0x6e34bb)}Checks  {Color(0xffffff)}:  {Color(0xddd45f)}{self.checks}
 {Color(0xffffff)}-----------
""")