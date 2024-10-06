import requests
import os
from bs4 import BeautifulSoup
import time
import datetime
from colorama import Fore, Back, Style

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


def get_user_search():
    try:    
        query = str(input("Please enter the product you want to look out for: "))
        preis = int(input("Please enter the maximum price-cap you want to see: "))
        time = int(input("Please enter the intervall in which you want to update your requests. "))
        return query, preis, time
    except ValueError as err:
        print(f'{Fore.RED}Invalid input! {err}{Style.RESET_ALL}')
        return None, None
    
def query_listings(url, excluded_keywords):
    """Query the listings from the given URL and filter out excluded keywords."""
    try:
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = soup.find('div', class_='position-relative')

        if listings:
            articles = listings.find_all('article')
            #print(f'{Fore.RED}Number of total listings found: {len(articles)}{Style.RESET_ALL}')
            filtered_listings = []

            for article in articles:
                link, title, price = '', '', 0.0
                a_elements = article.find_all('a', href=True)

                for a in a_elements:
                    link = a['href']
                    title = a.get_text(strip=True)

                    if any(keyword.lower() in title.lower() for keyword in excluded_keywords):
                        break

                price_elements = article.find_all('p', class_='aditem-main--middle--price-shipping--price')
                if price_elements:
                    # FOR NOW: This also ignores VB and Zu Verschenken listings.
                    # TODO: Implement a config where this is modifiable
                    price = price_elements[0].get_text(strip=True).replace('€', '').replace('.', '').replace(',', '.').replace('VB', '').replace('Zu verschenken','').strip()
                    price = float(price) if price else 0

                if title and link:
                    filtered_listings.append({
                        'title': title,
                        'link': f'https://www.kleinanzeigen.de{link}',
                        'price': price
                    })
            return filtered_listings    
        else:
            print(f'{Fore.RED}No listings found!{Style.RESET_ALL}')
            return []

    except requests.RequestException as e:
        print(f'{Fore.RED}Failed to retrieve listings: {e}{Style.RESET_ALL}')
        return []
    

def run_search(query, price_cap, intervall, excluded_keywords):
    url = f"https://www.kleinanzeigen.de/s-{query.replace(' ', '-')}/k0"  
    seen_listings = set()  

    while True:
        print(f"{Fore.YELLOW}Checking for new listings...")
        listings = query_listings(url, excluded_keywords)

        for listing in listings:
            #Make sure Price is parsed as a float!
            try:
                price = float(listing['price'])
            except ValueError:
                continue
            
            if listing['title'] not in seen_listings and price <= price_cap:
                print(f"{Fore.GREEN}New Listing Found! {Fore.WHITE}Title:{Fore.LIGHTMAGENTA_EX}{listing['title']}, {Fore.WHITE}Link: {Fore.LIGHTGREEN_EX}{listing['link']}, {Fore.WHITE}Price: {Fore.LIGHTCYAN_EX}{listing['price']}{Style.RESET_ALL}")
                seen_listings.add(listing['title'])  

        print(f"{Fore.YELLOW}Waiting for before next check...{Style.RESET_ALL}")
        time.sleep(intervall)  

def read_banned_keywords(path):
    try:
        with open(path, 'r') as file:
            banned_words = []
            for line in file:
                line = line.strip()
                
                if line.startswith('#') or not line:
                    continue
                
                banned_words.append(line)
                
            return banned_words
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File not found: {path}{Style.RESET_ALL}")
        return []

def main():
    current_dir = os.path.dirname(__file__)
    
    banned_title_keywords = read_banned_keywords(os.path.join(current_dir, '../resources/banned_keywords.txt'))
    print(banned_title_keywords)
    banner()
    query, preis, time = get_user_search()
    if query is not None and preis is not None and time is not None:
        run_search(query, preis, time, banned_title_keywords)

if __name__ == '__main__':
    main()
