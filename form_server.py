from flask import Flask, render_template_string, request
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)

# HTML template for the form
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amazon Scraper</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='amazon_styles.css') }}">
</head>
<body>
    <div class="container">
        <h1>Amazon Scraper Input Form</h1>
        <form method="POST" action="/scrape">
            <div class="form-group">
                <label for="keyword">Keyword:</label>
                <input type="text" id="keyword" name="keyword" required>
            </div>
            <div class="form-group">
                <label for="pages">Number of Pages:</label>
                <input type="number" id="pages" name="pages" min="1" required>
            </div>
            <button type="submit">Scrape</button>
        </form>
    </div>

</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scrape', methods=['POST'])
def scrape():
    keyword = request.form['keyword']
    pages = request.form['pages']
    
    try:
        # Run the existing scraper script
        process = subprocess.Popen(
            ['python', 'amazon_scraper.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        input_data = f"{keyword}\n{pages}\n"
        stdout, stderr = process.communicate(input=input_data)

        if process.returncode != 0:
            return f"<h2>Error:</h2><pre>{stderr}</pre>"

        # Perform data analysis on the scraped data
        csv_file = 'amazon_products.csv'  # Replace with the actual file name
        if not os.path.exists(csv_file):
            return "<h2>Error: Scraped data file not found!</h2>"
        
        # Load CSV data
        data = pd.read_csv(csv_file)

        # Ensure columns are strings before using .str methods
        data['Price'] = data['Price'].astype(str).str.replace(',', '', regex=False)
        data['Reviews'] = data['Reviews'].astype(str).str.replace(',', '', regex=False)
        data['Rating'] = data['Rating'].astype(str).str.extract(r'(\d+\.\d+)', expand=False)

        # Convert cleaned columns to numeric, handling invalid values as NaN
        data['Price'] = pd.to_numeric(data['Price'], errors='coerce')
        data['Reviews'] = pd.to_numeric(data['Reviews'], errors='coerce')
        data['Rating'] = pd.to_numeric(data['Rating'], errors='coerce')

        # Drop rows with missing or invalid values
        data.dropna(subset=['Price', 'Rating', 'Reviews'], inplace=True)

        # Define the "best product" as the one with the highest (Rating * Reviews / Price)
        data['Score'] = (data['Rating'] * data['Reviews']) / data['Price']
        best_product = data.loc[data['Score'].idxmax()]
        best_product_link = best_product['Link']


        # Plot graphs
        sns.set(style="whitegrid")
        plt.figure(figsize=(10, 6))

        # Plot 1: Rating vs. Reviews
        plt.subplot(1, 2, 1)
        sns.scatterplot(data=data, x='Reviews', y='Rating', size='Price', sizes=(20, 200), hue='Price', palette='viridis')
        plt.title('Rating vs. Reviews')

        # Plot 2: Price vs. Score
        plt.subplot(1, 2, 2)
        sns.scatterplot(data=data, x='Price', y='Score', hue='Score', palette='coolwarm')
        plt.title('Price vs. Score')

        # Save the plots
        plot_file = 'static/analysis_plots.png'
        plt.tight_layout()
        plt.savefig(plot_file)
        plt.close()

        # Display the link for the best product and analysis graphs
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Scraping Results</title>
            <link rel="stylesheet" href="/static/amazon_styles.css">
        </head>
        <body>
            <div class="message">
                <h2>Scraping Complete!</h2>
                <p>The scraped data is available <a href="http://localhost:8000" target="_blank">here</a>.</p>
                <h3>Best Product Recommendation:</h3>
                <p>To view the product we recommend based on analysis: <a href="{best_product_link}" target="_blank">click here</a></p>
                <h3>Analysis Graphs:</h3>
                <img src="/{plot_file}" alt="Analysis Graphs" style="max-width: 100%; height: auto;">
                <br><br>
                <a href="/">← Back to Home</a>
            </div>
        </body>
        </html>
        """

    except Exception as e:
        return f"<h2>Error:</h2><pre>{str(e)}</pre>"

if __name__ == '__main__':
    app.run(debug=True)
