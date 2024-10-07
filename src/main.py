import requests
import os
from bs4 import BeautifulSoup
import time
import datetime
import asyncio
from colorama import Fore, Back, Style
from scraper import read_banned_keywords, get_user_search, run_search

def banner():
    print(f'''{Fore.GREEN}
    ____             __         __                    __                                                               
   / __ \____ ______/ /_  _____/ /_  __  ______  ____/ /                                                               
  / / / / __ `/ ___/ __ \/ ___/ __ \/ / / / __ \/ __  /                                                                
 / /_/ / /_/ / /__/ / / (__  ) / / / /_/ / / / / /_/ /                                                                 
/_____/\__,_/\___/_/ /_/____/_/ /_/\__,_/_/ /_/\__,_/                                                                  
    __ __ __     _                              _                     _____       _ ________                           
   / //_// /__  (_)___  ____ _____  ____  ___  (_)___ ____  ____     / ___/____  (_) __/ __/__  _____                  
  / ,<  / / _ \/ / __ \/ __ `/ __ \/_  / / _ \/ / __ `/ _ \/ __ \    \__ \/ __ \/ / /_/ /_/ _ \/ ___/                  
 / /| |/ /  __/ / / / / /_/ / / / / / /_/  __/ / /_/ /  __/ / / /   ___/ / / / / / __/ __/  __/ /                      
/_/ |_/_/\___/_/_/ /_/\__,_/_/ /_/ /___/\___/_/\__, /\___/_/ /_/   /____/_/ /_/_/_/ /_/  \___/_/                       
                        __        __          /____/         __               __                                       
   ____ ___  ____ _____/ /__     / /_  __  __   / /_  ____ _/ /______________/ /_  ____ ___  ___  _________  ___  ____ 
  / __ `__ \/ __ `/ __  / _ \   / __ \/ / / /  / __ \/ __ `/ / ___/ ___/ ___/ __ \/ __ `__ \/ _ \/ ___/_  / / _ \/ __ \\
 / / / / / / /_/ / /_/ /  __/  / /_/ / /_/ /  / / / / /_/ / (__  |__  ) /__/ / / / / / / / /  __/ /    / /_/  __/ / / /
/_/ /_/ /_/\__,_/\__,_/\___/  /_.___/\__, /  /_/ /_/\__,_/_/____/____/\___/_/ /_/_/ /_/ /_/\___/_/    /___/\___/_/ /_/ 
                                    /____/                                                                             
    
    {Style.RESET_ALL}
          ''')

async def send_to_discord(message):
    print(f"Sending to Discord: {message}")

async def main():
    current_dir = os.path.dirname(__file__)
    
    banned_title_keywords = read_banned_keywords(os.path.join(current_dir, '../resources/banned_keywords.txt'))
    print(banned_title_keywords)
    banner()
    query, preis, time, duration = get_user_search()
    if query is not None and preis is not None and time is not None:
        await run_search(query, preis, time, duration, banned_title_keywords, send_to_discord=send_to_discord)

if __name__ == '__main__':
    asyncio.run(main())