from flask import Flask, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.by import By
from flask import Flask,request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract')
def extrct():
    return render_template('extract.html')

@app.route('/scrapper', methods=['POST'])
def scrapper():
    # Request data
    paper_url = request.form['url']

    # Set up Chrome browser options
    chrome_options = Options()
    # Run Chrome in headless mode (without a GUI)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Initialize the WebDriver with the specified options
    driver = webdriver.Chrome(options=chrome_options)
    # Open the webpage containing the article
    driver.get(paper_url)

    # Find the main document section using XPath and extract its HTML content
    document = driver.find_element("xpath", "//article")
    document = BeautifulSoup(document.get_attribute("innerHTML"), "html.parser")

    # Extract the title of the paper
    paper_title = document.find("h1").text

    # Find the abstract section and extract its title, content, and keywords
    abstract = document.find("section", {"class": "abstract"})
    abstract_title = abstract.find("h2").text
    abstract_content = abstract.find("p").text
    keywords = abstract.find("section", {"id": "kwd-group1"})
    keywords_title = keywords.find("strong").text
    keywords = keywords.find("p").text.replace(keywords_title, '')

    # Find all sections whose IDs start with "Sec" followed by numbers using regex
    sections = document.find_all('section', id=re.compile(r"^Sec\d+$"))

    # Initialize a list to hold the text of all sections
    all_sections = []

    # Loop through each section found
    for section in sections:
        section_texts = section.find_all(["h2", "h3", "h4", "h5", "p", "table"])
        current_section = ""
        for section_text in section_texts:
            prev = ""
            if section_text.name == "h2":
                prev = "## "
            elif section_text.name == "h3":
                prev = "### "
            elif section_text.name == "h4":
                prev = "#### "
            elif section_text.name == "h5":
                prev = "##### "
            elif section_text.name == "table":
                # Extract the table content and convert to Markdown format
                table_content = ""
                divider = ""
                for row in section_text.find_all("tr"):
                    cells = row.find_all(["th"])
                    for cell in cells:
                        table_content += "| **" + cell.text + "** "
                        divider += "|:---:"
                    table_content += "|\n" if divider else "\n"
                    table_content += divider
                    divider = ""
                    cells = row.find_all(["td"])
                    for cell in cells:
                        table_content += "| " + cell.text + " "
                    table_content += "|"
                table_content += "\n\n"
                current_section += table_content
            current_section += prev + section_text.text + "\n"
        all_sections.append(current_section)

    # Write the extracted content to a text file
    # TODO - Save file in S3
    with open(f"../data/paper_{paper_title}.txt", "w") as file:
        file.write("# " + paper_title + "\n")
        file.write("## " + abstract_title + "\n")
        file.write(abstract_content + "\n")
        file.write("\n" + "**" + keywords_title.strip() + "**" + "\n")
        file.write(keywords + "\n")
        for section in all_sections:
            file.write(section + "\n")

    # TODO - Redirect to correct page
    return "ok"

if __name__ == '__main__':
    app.run(debug=True)
