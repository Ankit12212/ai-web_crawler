import json 
import os
from typing import List, Set, Tuple

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode, 
    CrawlerRunConfig, 
    LLMExtractionStrategy,
    LLMConfig
)
from models.venue import Venue
from utils.data_utils import is_complete_venue, is_duplicate_venue

def get_browser_config() -> BrowserConfig:
    return BrowserConfig(
        browser_type="chromium",
        headless=False,
        verbose=True
    )

def get_llm_strategy() -> LLMExtractionStrategy:
    return LLMExtractionStrategy(
        llm_config = LLMConfig(
            provider="groq/deepseek-r1-distill-llama-70b",
            api_token=os.getenv("GROQ_API_KEY")
        ),
        schema=Venue.model_json_schema(),
        extraction_type="schema",
        instruction=(
            "Extract all venue objects with 'name', 'location', 'price', 'capacity', "
            "'rating', 'reviews', and 'description' from the provided follwoing content."
        ),
        input_format="markdown",
        verbose=True
    )

async def fetch_and_process_page(
        crawler: AsyncWebCrawler,
        page_number: int,
        base_url: str,
        session_id: str,
        llm_strategy: LLMExtractionStrategy,
        required_keys: List[str],
        seen_names: Set[str],
        css_selector: str
) -> Tuple[List[Venue], bool]:
    url = f'{base_url}?{page_number}'
    print(f"Crawling {url}...")

    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            session_id=session_id,
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=llm_strategy,
            css_selector=css_selector),
        
    )

    if not result:
        print(f"Error fetching page {page_number}: {result.error_message}")
        return [], True
    
    extracted_data = json.loads(result.extracted_content)

    print("Extracted venues:", extracted_data)

    complete_venues = []
    for venue in extracted_data:
        print("Processing venue:", venue)

        if venue.get("error") is False:
            venue.pop("error", None)  

        if not is_complete_venue(venue, required_keys):
            continue  

        if is_duplicate_venue(venue["name"], seen_names):
            print(f"Duplicate venue '{venue['name']}' found. Skipping.")
            continue  

        seen_names.add(venue["name"])
        complete_venues.append(venue)

    if not complete_venues:
        print(f"No complete venues found on page {page_number}.")
        return [], False

    print(f"Extracted {len(complete_venues)} venues from page {page_number}.")
    return complete_venues, False  