from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    additional_info = None
    if request.method == 'POST':
        url = request.form['webaddress']
        try:
            # Get headers to find Last-Modified
            response = requests.head(url)
            last_modified = response.headers.get('Last-Modified', 'No information available')
            editor = response.headers.get('X-Modified-By', 'No editor information available')
            result = f"This site has been lastly modified at: {last_modified}. Editor: {editor}."
            
            # Additional check for meta tags or other indicators in HTML
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_last_modified = soup.find('meta', attrs={'name': 'last-modified'})
            if meta_last_modified and meta_last_modified.get('content'):
                additional_info = f"Meta Tag Last Modified: {meta_last_modified['content']}"
            
            # Check sitemap for lastmod
            sitemap_url = url.rstrip('/') + '/sitemap.xml'
            sitemap_response = requests.get(sitemap_url)
            if sitemap_response.status_code == 200:
                sitemap_soup = BeautifulSoup(sitemap_response.content, 'xml')
                lastmod = sitemap_soup.find('lastmod')
                if lastmod:
                    additional_info = (additional_info or '') + f" | Sitemap Last Modified: {lastmod.text}"
        
        except requests.RequestException as e:
            result = f"An error occurred: {str(e)}"
    
    html = '''
    <!doctype html>
    <html>
    <head>
        <title>Website Last Modified Checker</title>
    </head>
    <body>
        <h1>Check when a website was last updated</h1>
        <form method="post">
            Web Address: <input type="text" name="webaddress" placeholder="https://example.com">
            <input type="submit" value="Check">
        </form>
        {% if result %}
        <div>
            <h3>Result:</h3>
            <p>{{ result }}</p>
        </div>
        {% endif %}
        {% if additional_info %}
        <div>
            <h3>Additional Information:</h3>
            <p>{{ additional_info }}</p>
        </div>
        {% endif %}
    </body>
    </html>
    '''
    
    return render_template_string(html, result=result, additional_info=additional_info)

if __name__ == '__main__':
    app.run(debug=True)
