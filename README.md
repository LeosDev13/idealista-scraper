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

| Metric                        | Formula                                                    | Required Data                    |
| ----------------------------- | ---------------------------------------------------------- | -------------------------------- |
| **Total properties for sale** | Count of all listed properties in the area                 | Property listings                |
| **Matching properties**       | Count of properties that meet filters                      | Property type, price, size, etc. |
| **Near-match properties**     | Properties within a margin of the filter range (e.g., ±5%) | Property type, price, size       |
| **Average price per area**    | Prices of all properties in the area                       | Prices in the area               |
| **Price deviation**           | Prices in the area                                         | Prices in the area               |
| **Price comparison**          | Property price, area average price                         | Property price, area price       |
| **Overvalued properties**     | Price per m², area price per m²                            | Price per m², area price per m²  |
| **Undervalued properties**    | Price, estimated value from comparable listings            | Price, estimated value           |
| **Average selling time**      | Listing & selling dates                                    | Listing & selling dates          |

## 🛠️ Tech Stack

- **Python**: Main programming language
- **BeautifulSoup / curl_cffi**: Web scraping

## 📥 Installation

### Prerequisites

1. Python 3.11 or higher
2. Supabase account (for the database)
3. [uv](https://docs.astral.sh/uv/) installed

### Initial Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/idealista-scraper.git
   cd idealista-scraper
   ```

2. Create an `.env` file based on the example:

   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your Supabase credentials:

   ```
   SUPABASE_URL=https://your-supabase-project.supabase.co
   SUPABASE_KEY=your-supabase-key
   ```

4. Set up the virtual environment and dependencies:

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

## 🔄 Running the Scraper

### Run the scraper manually:

```bash
uv run -m scraper
```

The scraper will fetch all locations from the database and start extracting property data sequentially, saving them to the database.

## 📊 Running the Dashboard

Start the Streamlit application:

```bash
streamlit run app/app.py
```

The dashboard will be available at `http://localhost:8501`

## 🐳 Docker Setup

### 1. Build the image

```bash
docker build -t idealista-scraper .
```

### 2. Run the container

```bash
docker run --rm -e SUPABASE_URL=your-url -e SUPABASE_KEY=your-key idealista-scraper
```

💡 This will start the scraper and run it automatically with `uv run -m scraper`.

### Running the dashboard with Docker

```bash
docker run --rm -e SUPABASE_URL=your-url -e SUPABASE_KEY=your-key -p 8501:8501 idealista-scraper streamlit run app/app.py
```

### Interactive mode

If you need to open a shell in the container:

```bash
docker run --rm -it idealista-scraper /bin/sh
```

## 🏗️ Project Structure

```
idealista-scraper/
├── app/                    # Streamlit application
│   ├── app.py              # Dashboard entry point
│   └── services/           # Services for the dashboard
├── core/                   # Core components
│   ├── Database.py         # Database interaction
│   ├── Logger.py           # Logging configuration
│   └── models/             # Data models
├── scraper/                # Scraper logic
│   ├── __main__.py         # Scraper entry point
│   └── IdealistaScraper.py # Scraper implementation
└── .env                    # Environment variables (not included in git)
```

## 📜 License

This project is licensed under the MIT License.

## 📧 Contact

For any inquiries, reach out at leosdev13@gmail.com.
