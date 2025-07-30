# australia-apartments-scraping

This small project scrapes apartment data from ( https://www.apartments.com.au/ ) in three Australian cities: **Adelaide**, **Canberra**, and **Perth**. Specifically:
- Adelaide: 268 projects
- Canberra: 181 projects
- Perth: 319 projects

## 📦 Technologies Used
- **Python**
- **Selenium** – for web scraping
- **Pandas** – for data processing and saving to Excel

## 📁 Project Structure
- `scrape.py`: Contains core scraping logic used by all location files
- `adelaide.py`, `canberra.py`, `perth.py`: Use `scrape.py` to extract data for each location individually

## ⚙️ How to Use

1. **Clone or download** this repository.
2. Make sure all 4 Python files are in the same folder.
3. **Install dependencies** by running:
   ```bash
   pip install selenium pandas
Download ChromeDriver compatible with your Chrome version and place it in your system PATH or project folder.

Use a Python IDE (e.g., VS Code) to run:

adelaide.py

canberra.py

perth.py

The scripts will open a Chrome browser to perform scraping (headless mode is not supported due to missing data issues).

⚠️ Limitations
Runtime: Each script can take from 30 minutes to 1.5 hours due to the large amount of data.

Headless mode not supported: Running in headless mode results in incomplete data. Therefore, Chrome windows will visibly open during execution, which may be inconvenient.

> 🔒 The Excel output file is available upon request and will be shared privately to avoid unnecessary file size and comply with site terms.

