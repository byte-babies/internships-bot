#!/usr/bin/env python3
"""
Script to fetch and update local JSON data files with the latest internship listings.
This script fetches data from both repository sources and saves them locally.

Usage:
    python fetch_latest_data.py          # Interactive mode
    python fetch_latest_data.py --yes    # Non-interactive mode (auto-confirm)
    python fetch_latest_data.py --stats  # Show current stats only
"""

import json
import os
import asyncio
import aiohttp
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

JSON_URL_1 = 'https://raw.githubusercontent.com/vanshb03/Summer2026-Internships/refs/heads/dev/.github/scripts/listings.json'
JSON_URL_2 = 'https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/refs/heads/dev/.github/scripts/listings.json'
JSON_URL_3 = 'https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/refs/heads/dev/.github/scripts/listings.json'
PREVIOUS_DATA_FILE = 'previous_data.json'
PREVIOUS_DATA_FILE_2 = 'previous_data_simplify.json'
PREVIOUS_DATA_FILE_3 = 'previous_data_simplify2.json'

logging.basicConfig(
    level=logging.INFO,
    format='[{asctime}] [{levelname:<8}] {name}: {message}',
    style='{',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('data_fetcher')

async def fetch_json_from_url(url: str) -> list:
    """Fetch JSON data directly from URL"""
    logger.info(f"Fetching JSON data from {url}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text_data = await response.text()
                    data = json.loads(text_data)
                    logger.info(f"Successfully fetched {len(data)} items from {url}")
                    return data
                else:
                    logger.error(f"Error fetching {url}: HTTP {response.status}")
                    return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from {url}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching JSON from {url}: {e}")
        return []

def save_json_data(data: list, file_path: str) -> bool:
    """Save JSON data to file"""
    try:
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup"
            os.rename(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

        logger.info(f"Successfully saved {len(data)} items to {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {e}")
        if os.path.exists(f"{file_path}.backup"):
            os.rename(f"{file_path}.backup", file_path)
            logger.info(f"Restored backup for {file_path}")
        return False

async def update_data_files():
    """Main function to update both data files"""
    logger.info("Starting data update process...")
    start_time = datetime.now()

    logger.info("Updating first data source...")
    data1 = await fetch_json_from_url(JSON_URL_1)
    if data1:
        success1 = save_json_data(data1, PREVIOUS_DATA_FILE)
    else:
        logger.error("Failed to fetch data from first source")
        success1 = False

    logger.info("Updating second data source...")
    data2 = await fetch_json_from_url(JSON_URL_2)
    if data2:
        success2 = save_json_data(data2, PREVIOUS_DATA_FILE_2)
    else:
        logger.error("Failed to fetch data from second source")
        success2 = False
    
    logger.info("Updating third data source...")
    data3 = await fetch_json_from_url(JSON_URL_3)
    if data3:
        success3 = save_json_data(data3, PREVIOUS_DATA_FILE_3)
    else:
        logger.error("Failed to fetch data from third source")
        success3 = False

    end_time = datetime.now()
    duration = end_time - start_time

    logger.info("=" * 50)
    logger.info("UPDATE SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Duration: {duration.total_seconds():.2f} seconds")
    logger.info(f"Source 1: {'Success' if success1 else 'Failed'}")
    logger.info(f"Source 2: {'Success' if success2 else 'Failed'}")
    logger.info(f"Source 3: {'Success' if success3 else 'Failed'}")

    if success1 and success2 and success3:
        logger.info("All data files updated successfully!")
        return True
    else:
        logger.error("Some data files failed to update")
        return False

def print_file_stats():
    """Print statistics about the data files"""
    logger.info("\nDATA FILE STATISTICS:")
    logger.info("-" * 30)

    for file_path in [PREVIOUS_DATA_FILE, PREVIOUS_DATA_FILE_2, PREVIOUS_DATA_FILE_3]:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    file_size = os.path.getsize(file_path)
                    logger.info(f"{file_path}:")
                    logger.info(f"  • Items: {len(data)}")
                    logger.info(f"  • Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                    logger.info(f"  • Last modified: {datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        else:
            logger.info(f"{file_path}: File does not exist")

async def main():
    """Main entry point"""
    logger.info("Internship Data Fetcher")
    logger.info("=" * 40)

    print_file_stats()

    print("\n" + "=" * 50)
    response = input("Do you want to update the data files? (y/N): ").strip().lower()

    if response not in ['y', 'yes']:
        logger.info("Update cancelled by user.")
        return

    success = await update_data_files()

    if success:
        print("\n" + "=" * 50)
        print_file_stats()

    logger.info("\nDone!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nUpdate interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")