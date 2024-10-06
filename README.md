# 📦 Kleinanzeigen Scraper

This Python project is a web scraper designed to monitor listings on [Kleinanzeigen.de](https://www.kleinanzeigen.de/) for specific items and notify you when a new listing appears below your set price cap. It uses `requests` and `BeautifulSoup` to fetch and parse the listings and is capable of excluding listings based on predefined keywords.

## 🚀 Features

- **Customizable Search**: You can specify the product you're looking for, set a maximum price cap, and define an update interval.
- **Real-Time Updates**: Continuously checks for new listings and alerts you when new items are available.
- **Keyword Filtering**: Filters out listings based on excluded keywords (e.g., "Suche" for users who are looking for something rather than selling).
- **Formatted Output**: Provides color-coded output in the terminal using `colorama` for easy reading.

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/kleinanzeigen-scraper.git
cd kleinanzeigen-scraper
```

### 2. Create a Virtual Environment (Optional but recommended)

```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# On Windows
.\env\Scripts\activate

# On MacOS/Linux
source env/bin/activate
```

### 3. Install Required Dependencies

```bash
pip install -r requirements.txt
```

Ensure the `requirements.txt` contains:

```txt
requests
beautifulsoup4
colorama
```

### 4. Run the Script

```bash
python scraper.py
```

## 🔧 Usage

When you run the script, it will prompt you for three inputs:

1. **Product name**: Enter the name of the product you're searching for.
2. **Maximum price**: Set the price cap (in EUR) for listings you'd like to monitor.
3. **Update interval**: Specify the time interval (in seconds) for checking new listings.

For example:
```
Please enter the product you want to look out for: Nintendo Switch
Please enter the maximum price-cap you want to see: 200
Please enter the interval in which you want to update your requests: 60
```

The scraper will then continuously check Kleinanzeigen for new listings matching your criteria. When a new listing is found, it will display information like the title, price, and a link to the item.

### Example Output:

```bash
Checking for new listings...
New Listing Found! Title: Nintendo Switch, Link: https://www.kleinanzeigen.de/Nintendo-Switch/12345, Price: 180€
Waiting for before next check...
```

## 📝 Configuration

### Banned Keywords

You can customize the list of banned keywords in the `banned_title_keywords` array within the script. These keywords will exclude listings containing those words in the title. For example:

```python
banned_title_keywords = ["Suche", 'suche', 'SUCHE', '!SUCHE!', 'DS,2DS,3DS XL']
```

This ensures that unwanted listings like search requests or unrelated products are filtered out.

## ⚠️ Disclaimer

This script is intended for educational purposes only. Please make sure you respect the terms of service of Kleinanzeigen and avoid making too frequent requests that could put load on their servers. Consider increasing the interval time to be more respectful of the website.

## 🤝 Contributing

Feel free to fork the repository and submit pull requests. Contributions are welcome!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

