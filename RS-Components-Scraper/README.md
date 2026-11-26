# RS Components UK GraphQL Scraper

An asynchronous Python scraper that extracts product data from the sensors category on [RS Components UK](https://uk.rs-online.com) through its GraphQL endpoint.

The scraper reverse-engineers the site's GraphQL requests to retrieve structured product information directly from the API rather than scraping rendered HTML pages.

The whole category is about 2,273 pages (20 products each), roughly 45,000 products

It uses asynchronous HTTP requests, concurrent pagination, rate limiting, automatic retries, and product deduplication to handle large category datasets efficiently.

## Features

- GraphQL API reverse engineering.
- Asynchronous HTTP requests using `curl_cffi`.
- Chrome browser impersonation.
- Session cookie management through environment variables.
- Concurrent page scraping using `asyncio.gather()`.
- Concurrency control using `asyncio.Semaphore`.
- Request rate limiting using `aiolimiter`.
- Automatic retries for failed requests.
- Automatic pagination based on API response metadata.
- Product deduplication using unique product IDs.
- Structured product extraction.
- CSV data export using pandas.
- Logging to both terminal and file.
- Raw API response inspection and JSON export.

## Tech Stack

- Python
- curl_cffi
- asyncio
- aiolimiter
- pandas
- python-dotenv
- JSON

## How it works

- Sends the same `Browse` GraphQL query the website sends, one request per page
- Reads `lastPage` from the first response so it knows how many pages to fetch
- Uses `curl_cffi` with Chrome impersonation so requests look like a real browser
- Runs asynchronously, but capped at 10 concurrent requests and 5 requests per second so it doesn't hammer the server
- Retries a failed page up to 3 times before giving up on it
- Removes duplicate products by `prod_id`
- Logs every page to the terminal and to `rs_scraper.log`


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

## About dumps.py

I used this earlier on to save my cookies into `.env` and to dump one raw API response into `rs.json` so I could look at the structure. I wrote it before making the scraper async, so it only works with my older synchronous version of `rs.py`. it isn't needed to run the scraper.

## Scraping Workflow

The scraper follows these steps:

1. Initializes an asynchronous HTTP session with Chrome impersonation.
2. Loads session cookies and configures request headers.
3. Sends an initial request for page 1.
4. Extracts the total number of pages from the GraphQL pagination response.
5. Creates concurrent requests for the remaining pages.
6. Uses a semaphore to control concurrent requests.
7. Uses an asynchronous rate limiter to control request frequency.
8. Retries failed requests up to three times, with a one-second delay between attempts.
9. Extracts product attributes from each page.
10. Deduplicates products using their unique product IDs.
11. Exports the extracted dataset to CSV.

## Concurrency and Rate Limiting

The scraper uses the following configuration:

```python
semaphore = asyncio.Semaphore(10)
limiter = AsyncLimiter(5, 1)
```

- **Semaphore:** Limits concurrent page requests to 10.
- **Rate limiter:** Controls request frequency to approximately 5 requests per second.
- **asyncio.gather():** Executes page requests concurrently and collects their results.
- **Retry logic:** Attempts failed requests up to three times before giving up.

Failed requests are logged, and unsuccessful pages do not prevent the remaining pages from being processed.

## Pagination and Deduplication

Pagination is handled dynamically using the API's `lastPage` value.

The scraper fetches page 1 separately to determine the total number of pages, then schedules requests for the remaining pages.

Product records are deduplicated using `prod_id` to prevent duplicate entries in the final dataset.

## Logging

The scraper uses Python's built-in logging module.

Logs are written to:

- Terminal (StreamHandler).
- `rs_scraper.log` (FileHandler).

Logging provides information about failed requests, retry attempts, page processing, and the total number of extracted products.

## Raw API Response Export

During API reverse engineering, a separate `dumps.py` utility was used to capture the complete GraphQL response.

The response was serialized using `json.dumps()` with indentation and saved to `rs.json`.

This provided a convenient way to inspect the nested JSON structure, identify product attributes, and understand the API response before implementing the asynchronous scraper.

## Usage

Run the scraper:

```bash
python rs.py
```

Once scraping is complete, the extracted product dataset is saved as:

```text
sensors.csv
```

The output contains the structured product attributes listed above.

## Notes

- The scraper targets RS Components UK's GraphQL endpoint.
- The category being scraped is determined by the GraphQL query variables.
- The current configuration targets the Sensors category.
- Session cookies may expire and require refreshing. If requests start failing, grab fresh ones.
- HTTP failures, including intermittent 502 responses, are handled through automatic retries.
- The scraper uses concurrent requests to improve extraction efficiency while controlling request frequency.
- `.env` and all CSV/JSON files are gitignored. Don't commit your cookies.
- This is for learning and personal use. Check the site's terms before scraping at scale.