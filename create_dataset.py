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
driver.get("https://pmc.ncbi.nlm.nih.gov/articles/PMC4718671/")

# Find the main document section using XPath and extract its HTML content
document = driver.find_element("xpath", "//article")
document = BeautifulSoup(document.get_attribute("innerHTML"), "html.parser")

# Extract the title of the paper
paper_title = document.find("h1").text

print(paper_title)

# Find the abstract section and extract its title, content, and keywords
abstract = document.find("section", {"class": "abstract"})
abstract_title = abstract.find("h2").text
abstract_content = abstract.find("p").text
keywords = abstract.find("section", {"id": "kwd-group1"})
keywords_title = keywords.find("strong").text if keywords else ""
keywords = keywords.find("p").text.replace(keywords_title, '') if keywords else ""

# Find all sections whose IDs start with "Sec" followed by numbers using regex
sections = document.find_all('section', id=re.compile(r"^Sec\d+$"))

if not sections:
    sections = document.find_all('section', id=re.compile(r"^sec\d+$"))

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
with open(f"./data/paper_{paper_title}.txt", "w") as file:
    file.write("# " + paper_title + "\n")
    file.write("## " + abstract_title + "\n")
    file.write(abstract_content + "\n")
    file.write("\n" + "**" + keywords_title.strip() + "**" + "\n")
    file.write(keywords + "\n")
    for section in all_sections:
        file.write(section + "\n")

# Close the WebDriver
driver.close()