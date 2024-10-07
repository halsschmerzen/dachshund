import os
import time
import requests
from colorama import Style, Fore
from bs4 import BeautifulSoup
import asyncio

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
    
def get_user_search():
    try:    
        query = str(input("Please enter the product you want to look out for: "))
        preis = int(input("Please enter the maximum price-cap you want to see: "))
        time = int(input("Please enter the intervall in which you want to update your requests. "))
        interval = int(input('Please enter the time the program should run.'))
        return query, preis, time, interval
    except ValueError as err:
        print(f'{Fore.RED}Invalid input! {err}{Style.RESET_ALL}')
        return None, None
    
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
    
async def run_search(query, price_cap, interval, duration, excluded_keywords, send_to_discord=None):
    url = f"https://www.kleinanzeigen.de/s-{query.replace(' ', '-')}/k0"  
    seen_listings = set()  
    end_time = time.time() + duration

    while time.time() < end_time:
        print(f"{Fore.YELLOW}Checking for new listings...")
        listings = query_listings(url, excluded_keywords)

        for listing in listings:
            try:
                price = float(listing['price'])
            except ValueError:
                continue
            
            if listing['title'] not in seen_listings and price <= price_cap:
                print(f"{Fore.GREEN}New Listing Found! {Fore.WHITE}Title:{Fore.LIGHTMAGENTA_EX}{listing['title']}, {Fore.WHITE}Link: {Fore.LIGHTGREEN_EX}{listing['link']}, {Fore.WHITE}Price: {Fore.LIGHTCYAN_EX}{listing['price']}{Style.RESET_ALL}")
                seen_listings.add(listing['title'])  
                
                if send_to_discord:
                    message = f'New Listing Found! Title: {listing["title"]}, Link: {listing["link"]}, Price: {listing["price"]}'
                    print(f"Calling send_to_discord with message: {message}")  # Debugging statement
                    await send_to_discord(message)

        print(f"{Fore.YELLOW}Waiting for before next check...{Style.RESET_ALL}")
        await asyncio.sleep(interval)