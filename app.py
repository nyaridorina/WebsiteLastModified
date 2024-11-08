from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

app = Flask(__name__)

def get_last_modified(url):
    """
    Attempts to get the Last-Modified header from the HTTP response.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        if 'Last-Modified' in response.headers:
            last_modified = response.headers['Last-Modified']
            # Parse the date string into a datetime object
            try:
                last_modified_date = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
            except ValueError:
                # Some servers might use different formats
                last_modified_date = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S GMT')
            return last_modified_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None
    except Exception as e:
        print(f"Error fetching headers: {e}")
        return None

def scrape_last_updated(url):
    """
    Scrapes the webpage for common patterns indicating the last update time.
    """
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Common patterns for dates
        date_patterns = [
            r'Last updated on (\w+ \d{1,2}, \d{4})',
            r'Updated: (\w+ \d{1,2}, \d{4})',
            r'Last Modified: (\w+ \d{1,2}, \d{4})',
            r'(\w+ \d{1,2}, \d{4})'  # Generic date pattern
        ]

        text = soup.get_text(separator=' ', strip=True)

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    # Attempt multiple date formats
                    for fmt in ('%B %d, %Y', '%d %B %Y', '%b %d, %Y'):
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            return parsed_date.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                except:
                    continue
        return None
    except Exception as e:
        print(f"Error scraping webpage: {e}")
        return None

def scrape_author(url):
    """
    Scrapes the webpage for common patterns indicating the author.
    """
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Common meta tag for author
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author and meta_author.get('content'):
            return meta_author.get('content').strip()

        # Look for author in the page content
        author_patterns = [
            r'By (\w+ \w+)',
            r'Author: (\w+ \w+)',
            r'Written by (\w+ \w+)',
            r'Contributors?: (\w+ \w+)',
            r'Edited by (\w+ \w+)'
        ]

        text = soup.get_text(separator=' ', strip=True)
        for pattern in author_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None
    except Exception as e:
        print(f"Error scraping author: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    update_info = ""
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if not url:
            update_info = "Please enter a URL."
            return render_template('index.html', update_info=update_info)

        # Ensure the URL starts with http:// or https://
        if not re.match(r'^https?:\/\/', url):
            url = 'http://' + url

        last_modified = get_last_modified(url)
        if last_modified:
            update_info = f"**Last Modified:** {last_modified}"
        else:
            scraped_date = scrape_last_updated(url)
            if scraped_date:
                update_info = f"**Last Updated (scraped):** {scraped_date}"
            else:
                update_info = "Last update information not found."

        # Attempt to find the author if available
        author = scrape_author(url)
        if author:
            update_info += f"<br>**Updated By:** {author}"

    return render_template('index.html', update_info=update_info)

if __name__ == '__main__':
    app.run(debug=True)
