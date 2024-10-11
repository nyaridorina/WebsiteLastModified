from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        url = request.form['webaddress']
        try:
            response = requests.head(url)
            last_modified = response.headers.get('Last-Modified', 'No information available')
            editor = response.headers.get('X-Modified-By', 'No editor information available')
            result = f"This site has been lastly modified at: {last_modified}. Editor: {editor}."
        except requests.RequestException as e:
            result = f"An error occurred: {str(e)}"
    
    html = '''
    <!doctype html>
    <title>Website Last Modified Checker</title>
    <h1>Check when a website was last updated</h1>
    <form method=post>
      Web Address: <input type=text name=webaddress>
      <input type=submit value=Check>
    </form>
    <p>{{ result }}</p>
    '''
    
    return render_template_string(html, result=result)

if __name__ == '__main__':
    app.run(debug=True)
