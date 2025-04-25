# Idealista Scraper & Dashboard (WIP)

## 📌 Project Overview

This project is a web scraper for Idealista that collects real estate data to analyze market trends, property pricing, and investment opportunities. The collected data is used to build a dashboard with key metrics, including:

- Total number of properties for sale in a specific area
- Properties matching specific filters
- Properties that are close to matching filters
- Average price per square meter in different locations
- Overvalued and undervalued properties
- Alerts for properties below expected market value
- Time properties have been listed and average selling time

The dashboard provides real-time insights to help users make informed investment decisions.

## 🚀 Features

- **Web Scraper**: Collects real estate data (price, location, size, property type, etc.).
- **Data Processing**: Computes key real estate metrics.
- **Dashboard**: Visualizes insights through charts and tables.
- **Alerts System**: Notifies users when undervalued properties appear.
- **Price Comparisons**: Identifies properties above or below the average market price.

## 📊 Key Metrics

| Metric                   | Formula                                                   | Required Data                  |
|--------------------------|-----------------------------------------------------------|---------------------------------|
| **Total properties for sale** | Count of all listed properties in the area              | Property listings               |
| **Matching properties**   | Count of properties that meet filters                     | Property type, price, size, etc.|
| **Near-match properties** | Properties within a margin of the filter range (e.g., ±5%)| Property type, price, size      |
| **Average price per area**| Prices of all properties in the area                      | Prices in the area              |
| **Price deviation**       | Prices in the area                                        | Prices in the area              |
| **Price comparison**      | Property price, area average price                        | Property price, area price      |
| **Overvalued properties** | Price per m², area price per m²                           | Price per m², area price per m² |
| **Undervalued properties**| Price, estimated value from comparable listings           | Price, estimated value          |
| **Average selling time**  | Listing & selling dates                                   | Listing & selling dates         |

## 🛠️ Tech Stack

- **Python**: Main programming language
- **BeautifulSoup / curl_cffi**: Web scraping

## 📥 Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/idealista-scraper.git
    cd idealista-scraper
    ```

2. Setup 
    ```bash
    uv init
    ``` 
   [uv documentation](https://docs.astral.sh/uv/)

3. Run it
    ```bash
    uv run async_scraper.py
    ```

## 📌 Usage

- Run the scraper periodically to update the dataset.

## 📜 License

This project is licensed under the MIT License.

## 📧 Contact

For any inquiries, reach out at leosdev13@gmail.com.

