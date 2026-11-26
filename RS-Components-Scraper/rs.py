from curl_cffi.requests import AsyncSession
from aiolimiter import AsyncLimiter
import asyncio
import copy
import pandas as pd
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('rs_scraper.log', encoding='utf-8'),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

async def main():
    async with AsyncSession(impersonate='chrome') as session:

        RS_COOKIES = json.loads(os.getenv('RS_COOKIES', '{}'))

        session.cookies.update(RS_COOKIES)

        session.headers.update ({
            'accept': 'application/graphql-response+json, application/json',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'data-graph-authorisation-commerce': 'false',
            'origin': 'https://uk.rs-online.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://uk.rs-online.com/web/c/automation-control-gear/sensors/?pn=2',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Google Chrome";v="157", "Chromium";v="157"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36',
            'x-correlation-id': '89487a97-9f7f-411c-bfd7-eaecaf77ef57',
            'x-rs-iso-country-code': 'GB',
        })

        json_data = {
            'query': '\n  query Browse(\n      $countryCode: CountryCode!\n      $sortOptions: Sort\n      $language: Language!\n      $page: Int\n      $pageSize: PageSize\n      $pageType: String\n      $filters: [Filters]\n      $visitorId: String\n      $userIdHash: String\n      $companyId: String\n      $path: String\n      $taxonomyPath: String!\n      $taxonomyCountryCode: countryCode!\n      $taxonomyLanguage: language\n      $experiments: [String]\n  ) {\n      browse(\n          countryCode: $countryCode\n          sortOptions: $sortOptions\n          language: $language\n          page: $page\n          pageSize: $pageSize\n          pageType: $pageType\n          filters: $filters\n          visitorId: $visitorId\n          userIdHash: $userIdHash\n          companyId: $companyId\n          path: $path\n          experiments: $experiments\n      ) {\n          \n    pagination {\n      limit\n      page\n      total\n      lastPage\n    }\n\n          \n  taxonomy {\n    description\n    meta {\n      description\n      title\n    }\n    name\n    nodes {\n      description {\n        name\n        urlSafeName\n      }\n      parentId\n      level\n      id\n    }\n    type\n  }\n\n          \n   records {\n      ... on Product {\n        id\n        article {\n          title\n          merchandisingFlags\n          discoverArticleAttributes {\n            displayPrice\n            price\n            packPrice\n            unitPriced\n            packType\n            packSize\n            salesUnitOfMeasure\n            baseUnitOfMeasure\n            breakQty1\n            brandURL\n            brand\n            image\n            leafCategoryName\n            mpn\n            productURL\n            euEnergyEfficiencyRating\n            ukEnergyEfficiencyRating\n            imageEUEnergyLabel\n            imageUKEnergyLabel\n            specifications {\n              name\n              value\n              displayName\n            }\n            stockStatus\n          }\n        }\n      }\n    }\n    \n          \n    sortOptions {\n      sortOption\n      sortField\n      sortDirection\n      selected\n    }\n\n          \n  childCategory {\n    childCategories {\n      displayName\n      seoUrl\n    }\n    displayName\n    imgUrl\n    seoUrl\n  }\n\n          redirectionURL\n          contentManagementSystemId\n          isNewBrowse\n          selectedFilters {\n              \n      displayName\n      key\n      or\n      refinements {\n        type\n        count\n        value\n      }\n      type\n      source\n\n          }\n          availableFilters {\n              \n      displayName\n      key\n      or\n      refinements {\n        type\n        count\n        value\n      }\n      type\n      source\n\n          }\n          searchQueryInfo {\n            searchId\n          }\n          errors {\n              code\n              message\n              type\n          }\n          \n  indexableFilters {\n    displayName\n    href\n  }\n\n          \n  originalRequest {\n    area\n    collection\n    enableTopsort\n    pageCategories\n    pageSize\n    skip\n    query\n    debug\n    preFilter\n    sorts {\n      field\n      direction\n    }\n    visitorId\n    customUrlParams {\n      key\n      value\n    }\n  }\n\n      }\n      getTaxonomy {\n          byPath(taxonomyPath: $taxonomyPath, countryCode: $taxonomyCountryCode, language: $taxonomyLanguage) {\n              errors {\n                  code\n                  type\n                  message\n              }\n              nodes {\n                  id\n                  level\n              }\n          }\n      }\n  }\n',
            'variables': {
                'companyId': '',
                'countryCode': 'GB',
                'filters': [],
                'language': 'EN_GB',
                'page': 2,
                'pageSize': 'RESULT_20',
                'pageType': None,
                'path': 'automation-control-gear/sensors',
                'sortOptions': {
                    'direction': None,
                    'field': None,
                },
                'taxonomyCountryCode': 'GB',
                'taxonomyLanguage': 'EN_GB',
                'taxonomyPath': 'automation-control-gear/sensors',
                'visitorId': 'cmwvtz1v20001358b1tbr82gb',
            },
            'operationName': 'Browse',
        }


        semaphore = asyncio.Semaphore(10)
        limiter = AsyncLimiter(5, 1)

        async def fetch_data(page):
            async with semaphore:
                async with limiter:

                    payload = copy.deepcopy(json_data)
                    payload['variables']['page'] = page

                    for attempt in range(3):
                        try:
                            response = await session.post('https://uk.rs-online.com/web/c/api/datagraph/graphql', json=payload)
                            response.raise_for_status()

                            data = response.json()

                            if not data['data']['browse']['records']:
                                raise ValueError('No records returned')

                            return data

                        except Exception as e:
                            if attempt == 2:
                                logger.error('Page %d failed after 3 attempts: %r', page, e)
                                raise

                            logger.warning('Page %d failed. %d of 3 attempts: %r. Retrying...', page, attempt + 1, e)

                            await asyncio.sleep(1)

        def fetch_products(data):

            records = []

            for record in data['data']['browse']['records']:
                article = record['article'][0]
                attrr = article.get('discoverArticleAttributes', {})
                prod_id = record['id']
                title = article.get('title')
                price = attrr.get('price')
                pack_price = attrr.get('packPrice')
                unit_priced = attrr.get('unitPriced')
                pack_type = attrr.get('packType')
                pack_size = attrr.get('packSize')
                sales_unit_of_measure = attrr.get('salesUnitOfMeasure')
                brand = attrr.get('brand')
                mpn = attrr.get('mpn')
                leaf_category_name = attrr.get('leafCategoryName')
                stock_status = attrr.get('stockStatus')
                image = attrr.get('image')
                product_url = attrr.get('productURL')

                records.append({
                    'prod_id': prod_id,
                    'title': title,
                    'price': price,
                    'pack_price': pack_price,
                    'unit_priced': unit_priced,
                    'pack_type': pack_type,
                    'pack_size': pack_size,
                    'sales_unit_of_measure': sales_unit_of_measure,
                    'brand': brand,
                    'mpn': mpn,
                    'leaf_category_name': leaf_category_name,
                    'stock_status': stock_status,
                    'image': image,
                    'product_url': product_url
                })

            return records

        async def get_products():
            first_page = await fetch_data(1)
            last_page = first_page['data']['browse']['pagination']['lastPage']

            tasks = [fetch_data(page) for page in range(2, last_page + 1)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            results.insert(0, first_page)

            products = []
            seen = set()

            for page, data in enumerate(results, start=1):
                if isinstance(data, Exception):
                    logger.error('Page %d failed: %r', page, data)
                    continue

                for product in fetch_products(data):
                    prod_id = product['prod_id']

                    if prod_id not in seen:
                        seen.add(prod_id)

                        products.append(product)

                logger.info('Scraped %d out of %d pages', page, last_page)

            return products

        products = await get_products()
        logger.info('%d products extracted', len(products))

        df = pd.DataFrame(products)
        df.to_csv('sensors.csv', index=False)

if __name__ == '__main__':
    asyncio.run(main())