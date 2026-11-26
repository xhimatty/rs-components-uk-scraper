# RS Components UK Scraper

An asynchronous Python scraper that extracts product data from the sensors category on [RS Components UK](https://uk.rs-online.com) through its GraphQL endpoint.

The scraper reverse-engineers the site's GraphQL requests to retrieve structured product information directly from the API rather than scraping rendered HTML pages.

The Sensors category spans 2,273 pages with 20 listings per page, giving a theoretical total of 45,460 listings. After deduplicating by product ID, a full run returns 38,139 unique products.

I first assumed the gap was caused by failed pages but it wasn't. Temporary 502 errors and empty responses are retried automatically, and every page eventually recovered. The difference comes from duplicate products appearing on more than one page.

It uses asynchronous HTTP requests, concurrent pagination, rate limiting, automatic retries, and product deduplication to handle large category datasets efficiently.

## Features

- GraphQL API reverse engineering.
- Asynchronous HTTP requests using `curl_cffi` (`AsyncSession`).
- Chrome browser impersonation (TLS and HTTP/2 handshake).
- Session cookie management through environment variables.
- Concurrent page scraping using `asyncio.gather()`.
- Concurrency control using `asyncio.Semaphore`.
- Request rate limiting using `aiolimiter`.
- Automatic retries for failed requests.
- Automatic pagination based on API response metadata.
- Structured product extraction.
- CSV data export using `pandas`.
- Logging to both terminal and file.
- Raw API response inspection and JSON export.

## How the scraper works

The scraper follows these steps:

- Initialises an asynchronous HTTP session with Chrome impersonation.
- Loads cookies from `.env` and updates session headers.
- Sends an initial request for page 1.
- Reads `lastPage` from the first response so it knows how many pages to fetch
- Creates concurrent requests for the remaining pages.
- Uses a semaphore to limit concurrent requests to 10.
- Uses an asynchronous rate limiter to cap requests at 5 per second.
- Retries failed requests up to three times before giving up, with 1 second delay between attempts.
- Extracts product attributes from each page.
- Deduplicates products by `prod_id`.
- Exports the extracted dataset to CSV.
- Logs every page to the terminal and to `rs_scraper.log`
- Failed requests are logged, and unsuccessful pages do not prevent the remaining pages from being processed.


## Tech Stack

- Python
- curl_cffi
- asyncio
- aiolimiter
- pandas
- python-dotenv
- JSON


## Extracted Data

The scraper extracts the following product attributes:

| Field | Description |
|---|---|
| prod_id | Unique product identifier |
| title | Product title |
| price | Product price |
| pack_price | Pack price |
| unit_priced | Unit pricing information |
| pack_type | Packaging type |
| pack_size | Pack quantity |
| sales_unit_of_measure | Sales unit of measure |
| brand | Product brand |
| mpn | Manufacturer part number |
| leaf_category_name | Product leaf category |
| stock_status | Product stock availability |
| image | Product image URL |
| product_url | Product URL |

### Example

```json
{
    "prod_id": "7033739",
    "title": "SICK IME18-08BPSZC0S Threaded Barrel Inductive Proximity Sensor, M18 x 1 PNP IME 30V 8 mm 30 V dc 200mA",
    "price": 27.81,
    "pack_price": 27.81,
    "unit_priced": false,
    "pack_type": "FINISHED",
    "pack_size": 1,
    "sales_unit_of_measure": "EA",
    "brand": "SICK",
    "mpn": "IME18-08BPSZC0S",
    "leaf_category_name": "Proximity Sensors",
    "stock_status": "IN_STOCK",
    "image": "https://media.rs-online.com/t_large/F7033739-01.jpg",
    "product_url": "https://uk.rs-online.com/web/p/proximity-sensors/7033739"
}
```

The scraper saves these as rows in `sensors.csv`, one product per row.

## Project Structure

```text
RS-Components-Scraper/
│
├── rs.py
├── dumps.py
├── rs.json
├── sensors.csv
├── rs_scraper.log
├── .env
├── .gitignore
└── README.md
```

- `rs.py`: Main asynchronous scraper.
- `dumps.py`: Utility used during API reverse engineering to capture and export raw GraphQL responses.
- `rs.json`: Formatted raw GraphQL response.
- `sensors.csv`: Extracted product dataset.
- `rs_scraper.log`: Scraping logs.
- `.env`: Stores session cookies.

## Installation

Install the required dependencies:

```bash
pip install curl_cffi aiolimiter pandas python-dotenv
```

## Configuration

The scraper requires valid RS Components session cookies.

Store the cookies as a JSON string in your `.env` file:

```env
RS_COOKIES='{"cookie_name":"cookie_value"}'
```

The scraper loads the environment variables using `python-dotenv`, converts the cookie string into a Python dictionary using `json.loads()`, and updates the asynchronous session's cookie jar.

## Usage

Run the scraper:

```bash
python rs.py
```

Once scraping is complete, the extracted product dataset is saved as:

```text
sensors.csv
```

## About dumps.py

During API reverse engineering, I used `dumps.py` to dump a raw API response into `rs.json` so I could inspect its structure. This made it easier to examine the nested JSON, identify product attributes, and understand the API response. I also used it to save my cookies into `.env`. I wrote it before making the scraper async, so it only works with my older synchronous version of `rs.py`. It isn't needed to run the scraper.

## Notes

- The scraper targets RS Components UK's GraphQL endpoint.
- The category being scraped is determined by the GraphQL query variables.
- The current configuration targets the Sensors category.
- Session cookies may expire and require refreshing. If requests start failing, grab fresh ones.
- HTTP failures, including intermittent 502 responses, are handled through automatic retries.
- The scraper uses concurrent requests to improve extraction efficiency while controlling request frequency.
- `.env` and all CSV/JSON files are gitignored. Don't commit your cookies.
- This is for learning and personal use. Check the site's terms before scraping at scale.