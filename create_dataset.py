# Import necessary libraries
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

# Set up Chrome browser options
chrome_options = Options()
# Run Chrome in headless mode (without a GUI)
chrome_options.add_argument("--headless")

# Initialize the WebDriver with the specified options
driver = webdriver.Chrome(options=chrome_options)
# Open the webpage containing the article
driver.get("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10853571/?report=classic")

# Find the main document section using XPath and extract its HTML content
document = driver.find_element("xpath", "//section[@role='document']")
document = BeautifulSoup(document.get_attribute("innerHTML"), "html.parser")

# Extract the title of the paper
paper_title = document.find("h1").text

# Find the abstract section and extract its title, content, and keywords
abstract = document.find("div", {"id": "Abs1"})
abstract_title = abstract.find("h2").text
abstract_content = abstract.find("p").text
keywords_title = abstract.find("strong", {"class": "kwd-title"}).text
keywords = abstract.find("span", {"class": "kwd-text"}).text

# Find all sections whose IDs start with "Sec" followed by numbers using regex
sections = document.find_all('div', id=re.compile(r"^Sec\d+$"))

# Initialize a list to hold the text of all sections
all_sections = []

# Loop through each section found
for section in sections:
    current_section = ""
    # If the section contains h2 headings, add their text to the current section
    if section.find_all("h2") is not None:
        for h2 in section.find_all("h2"):
            current_section += h2.text + "\n"
    # If the section contains h3 headings, add their text to the current section
    if section.find_all("h3") is not None:
        for h3 in section.find_all("h3"):
            current_section += h3.text + "\n"
    # If the section contains h4 headings, add their text to the current section
    if section.find_all("h4") is not None:
        for h4 in section.find_all("h4"):
            current_section += h4.text + "\n"
    # If the section contains paragraphs, add their text to the current section
    if section.find_all("p") is not None:
        for p in section.find_all("p"):
            current_section += p.text + "\n"
    # Append the current section text to the list of all sections
    all_sections.append(current_section)

# Write the extracted content to a text file
with open("./data/paper.txt", "w") as file:
    file.write(paper_title + "\n")
    file.write(abstract_title + "\n")
    file.write(abstract_content + "\n")
    file.write(keywords_title + "\n")
    file.write(keywords + "\n")
    for section in all_sections:
        file.write(section + "\n")

# Close the WebDriver
driver.close()