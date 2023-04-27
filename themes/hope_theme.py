import os
try:
   from rgbprint import gradient_print, Color, rgbprint
except:
    os.system("pip install rgbprint")
    
title = ("""
             _._
           .'   '.
          /       \  ___    
   _.--. |     /  |.'   `'.            ▄█    █▄     ▄██████▄     ▄███████▄    ▄████████ 
 .'     `\   \|   /        \          ███    ███   ███    ███   ███    ███   ███    ███ 
/     _   \.=..=./  _.'    /          ███    ███   ███    ███   ███    ███   ███    █▀   
'.   .-'-.}`.<>.`{-'-.    /          ▄███▄▄▄▄███▄▄ ███    ███   ███    ███  ▄███▄▄▄      
  \ .---.{ <>()<> }.--..-'          ▀▀███▀▀▀▀███▀  ███    ███ ▀█████████▀  ▀▀███▀▀▀        
  '/     _},'<>`.{_    `\             ███    ███   ███    ███   ███          ███    █▄     
 .'   .-'/ )=..=;`\`-    \            ███    ███   ███    ███   ███          ███    ███   
(         /  /| \         )           ███    █▀     ▀██████▀   ▄████▀        ██████████   
 '-..___.'    :  '.___..-'            █                                         
        |      `   |               
        '.      _.'                 
           `--.-'                          
""")

def _print_stats(self) -> None:
        gradient_print(title, start_color=Color(0xff0062), end_color=Color(0xe895b5))
        gradient_print(f"                                           ┃ Theme   : ! Raptor#0975 ", start_color=Color(0xff0062), end_color=Color(0xf0bdd1))
        gradient_print(f"                                           ┃ Version : 8.0.0         ", start_color=Color(0xff0062), end_color=Color(0xf0bdd1))
        gradient_print(f"                                           ┃ Updated : 26.04.2023 ", start_color=Color(0xff0062), end_color=Color(0xf0bdd1))
        print()
        gradient_print(f"                                          ╠══════════════╬════════════╣", start_color=Color(0xff0062), end_color=Color(0xf0bdd1))
        print()  
        gradient_print(f"                                           ┃ Results : {self.buys}       ", start_color=Color(0xff0062), end_color=Color(0xf0bdd1))
        gradient_print(f"                                           ┃ Errors  : {self.errors}    ", start_color=Color(0xff0062), end_color=Color(0xf0bdd1))
        gradient_print(f"                                           ┃ Speed   : {self.last_time}  ", start_color=Color(0xff0062), end_color=Color(0xf0bdd1))
        gradient_print(f"                                           ┃ Checks  : {self.checks}      ", start_color=Color(0xff0062), end_color=Color(0xf0bdd1))
        print()
        gradient_print(f"                                          ╠══════════════╬════════════╣", start_color=Color(0xff0062), end_color=Color(0xf0bdd1))
        
        print()
        gradient_print(f"                                           ┃ Items  : {', '.join(self.items)} ", start_color=Color(0xff0062), end_color=Color(0xf0bdd1))
        gradient_print(f"                                           ┃ Status : {self.task} ", start_color=Color(0xff0062), end_color=Color(0xf0bdd1))