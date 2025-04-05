#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DorkingPRO - Advanced Search Engine Dorking Tool for Bug Bounty Hunters
Author: Claude
Version: 1.0.0
"""

import os
import sys
import json
import time
import random
import asyncio
import argparse
import requests
import urllib.parse
from typing import List, Dict, Set, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs
import aiohttp
from tqdm import tqdm
from fake_useragent import UserAgent
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# ASCII banner
BANNER = f"""
{Fore.CYAN}██████╗  ██████╗ ██████╗ ██╗  ██╗ █████╗ ███████╗███████╗ █████╗ {Fore.RED} ██████╗ ██╗  ██╗ ██╗ █████╗ 
{Fore.CYAN}██╔══██╗██╔═══██╗██╔══██╗██║ ██╔╝██╔══██╗╚══███╔╝╚══███╔╝██╔══██╗{Fore.RED}██╔═████╗╚██╗██╔╝███║██╔══██╗
{Fore.CYAN}██║  ██║██║   ██║██████╔╝█████╔╝ ███████║  ███╔╝   ███╔╝ ███████║{Fore.RED}██║██╔██║ ╚███╔╝ ╚██║███████║
{Fore.CYAN}██║  ██║██║   ██║██╔══██╗██╔═██╗ ██╔══██║ ███╔╝   ███╔╝  ██╔══██║{Fore.RED}████╔╝██║ ██╔██╗  ██║██╔══██║
{Fore.CYAN}██████╔╝╚██████╔╝██║  ██║██║  ██╗██║  ██║███████╗███████╗██║  ██║{Fore.RED}╚██████╔╝██╔╝ ██╗ ██║██║  ██║
{Fore.CYAN}╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝{Fore.RED} ╚═════╝ ╚═╝  ╚═╝ ╚═╝╚═╝  ╚═╝
                                                                                                  {Fore.YELLOW}v1.0
                                                                  
                                Author:    azza0x1a
                                Github:    https://github.com/azza0x1a
                                Instagram: https://www.instagram.com/azza0x1a
"""

# User agents list for rotation
ua = UserAgent()

@dataclass
class DorkResult:
    """Data class to store dorking results"""
    dork: str
    url: str
    engine: str
    status_code: Optional[int] = None


class SearchEngines:
    """Class to handle different search engines"""
    
    def __init__(self, session, delay: int, timeout: int, debug: bool):
        """Initialize search engine class
        
        Args:
            session: aiohttp session
            delay: Delay between requests in seconds
            timeout: Request timeout in seconds
            debug: Debug mode
        """
        self.session = session
        self.delay = delay
        self.timeout = timeout
        self.debug = debug
    
    async def _make_request(self, url: str) -> str:
        """Make HTTP request with error handling and retries
        
        Args:
            url: URL to fetch
            
        Returns:
            str: HTML content
        """
        headers = {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Sec-GPC': '1',
            'Cache-Control': 'max-age=0',
        }
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if self.debug:
                    print(f"{Fore.YELLOW}[DEBUG] Requesting: {url}")
                
                async with self.session.get(url, headers=headers, timeout=self.timeout) as response:
                    content = await response.text()
                    
                    if response.status == 200:
                        # Add random delay to avoid detection
                        delay_time = self.delay + random.uniform(0.5, 2.0)
                        await asyncio.sleep(delay_time)
                        return content
                    elif response.status == 429:
                        retry_delay = 10 + random.uniform(5, 15)
                        if self.debug:
                            print(f"{Fore.RED}[DEBUG] Rate limited (429). Waiting {retry_delay:.2f}s")
                        await asyncio.sleep(retry_delay)
                        retry_count += 1
                    else:
                        if self.debug:
                            print(f"{Fore.RED}[DEBUG] HTTP Error: {response.status}")
                        return ""
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if self.debug:
                    print(f"{Fore.RED}[DEBUG] Request error: {str(e)}")
                retry_count += 1
                await asyncio.sleep(self.delay)
        
        return ""

    async def search_google(self, dork: str, max_pages: int) -> List[str]:
        """Search Google with given dork
        
        Args:
            dork: Search dork
            max_pages: Maximum number of results pages to fetch
            
        Returns:
            List[str]: List of URLs found
        """
        results = []
        encoded_dork = urllib.parse.quote_plus(dork)
        
        for page in range(0, max_pages):
            start_param = page * 10
            search_url = f"https://www.google.com/search?q={encoded_dork}&start={start_param}"
            
            content = await self._make_request(search_url)
            if not content:
                continue
                
            # Extract links from Google search results
            # This is a simple extraction and might need adjustments
            link_start = 0
            while True:
                link_start = content.find('href="/url?q=', link_start)
                if link_start == -1:
                    break
                
                link_start += 13  # len('href="/url?q=')
                link_end = content.find('&amp;', link_start)
                
                if link_end != -1:
                    url = content[link_start:link_end]
                    # Filter out Google's own domains and common SEO traps
                    if not any(domain in url for domain in ['google.com', 'youtube.com', 'blogger.com']):
                        results.append(url)
                
                link_start = link_end
        
        return results

    async def search_bing(self, dork: str, max_pages: int) -> List[str]:
        """Search Bing with given dork
        
        Args:
            dork: Search dork
            max_pages: Maximum number of results pages to fetch
            
        Returns:
            List[str]: List of URLs found
        """
        results = []
        encoded_dork = urllib.parse.quote_plus(dork)
        
        for page in range(1, max_pages + 1):
            first_param = (page - 1) * 10 + 1
            search_url = f"https://www.bing.com/search?q={encoded_dork}&first={first_param}"
            
            content = await self._make_request(search_url)
            if not content:
                continue
                
            # Extract links from Bing search results
            link_start = 0
            while True:
                link_start = content.find('<a href="http', link_start)
                if link_start == -1:
                    break
                
                link_start = content.find('href="', link_start) + 6
                link_end = content.find('"', link_start)
                
                if link_end != -1:
                    url = content[link_start:link_end]
                    # Filter out Bing's own domains
                    if not any(domain in url for domain in ['bing.com', 'microsoft.com']):
                        results.append(url)
                
                link_start = link_end
        
        return results

    async def search_duckduckgo(self, dork: str, max_pages: int) -> List[str]:
        """Search DuckDuckGo with given dork
        
        Args:
            dork: Search dork
            max_pages: Maximum number of results pages to fetch
            
        Returns:
            List[str]: List of URLs found
        """
        results = []
        encoded_dork = urllib.parse.quote_plus(dork)
        
        # DuckDuckGo uses different pagination mechanism
        # We'll use the API-like endpoint for JSON results
        search_url = f"https://duckduckgo.com/?q={encoded_dork}&format=json"
        
        content = await self._make_request(search_url)
        if not content:
            return results
            
        try:
            data = json.loads(content)
            
            # Extract results from the response
            if 'Results' in data:
                for result in data['Results']:
                    if 'FirstURL' in result:
                        results.append(result['FirstURL'])
            
            # Also check for deep links in related topics
            if 'RelatedTopics' in data:
                for topic in data['RelatedTopics']:
                    if 'FirstURL' in topic:
                        results.append(topic['FirstURL'])
        except json.JSONDecodeError:
            # Fallback to HTML parsing if JSON fails
            link_start = 0
            while True:
                link_start = content.find('<a rel="nofollow" href="http', link_start)
                if link_start == -1:
                    break
                
                link_start = content.find('href="', link_start) + 6
                link_end = content.find('"', link_start)
                
                if link_end != -1:
                    url = content[link_start:link_end]
                    if not any(domain in url for domain in ['duckduckgo.com']):
                        results.append(url)
                
                link_start = link_end
        
        return results

    async def search_yahoo(self, dork: str, max_pages: int) -> List[str]:
        """Search Yahoo with given dork
        
        Args:
            dork: Search dork
            max_pages: Maximum number of results pages to fetch
            
        Returns:
            List[str]: List of URLs found
        """
        results = []
        encoded_dork = urllib.parse.quote_plus(dork)
        
        for page in range(1, max_pages + 1):
            start_param = (page - 1) * 10 + 1
            search_url = f"https://search.yahoo.com/search?p={encoded_dork}&b={start_param}"
            
            content = await self._make_request(search_url)
            if not content:
                continue
                
            # Extract links from Yahoo search results
            link_start = 0
            while True:
                link_start = content.find('<a class=" ac-algo fz-l ac-21th lh-24" href="http', link_start)
                if link_start == -1:
                    break
                
                link_start = content.find('href="', link_start) + 6
                link_end = content.find('"', link_start)
                
                if link_end != -1:
                    url = content[link_start:link_end]
                    # Remove Yahoo redirect
                    if 'r.search.yahoo.com' in url:
                        parsed_url = urlparse(url)
                        query_params = parse_qs(parsed_url.query)
                        if 'p' in query_params:
                            url = query_params['p'][0]
                    
                    if not any(domain in url for domain in ['yahoo.com']):
                        results.append(url)
                
                link_start = link_end
        
        return results

    async def search_yandex(self, dork: str, max_pages: int) -> List[str]:
        """Search Yandex with given dork
        
        Args:
            dork: Search dork
            max_pages: Maximum number of results pages to fetch
            
        Returns:
            List[str]: List of URLs found
        """
        results = []
        encoded_dork = urllib.parse.quote_plus(dork)
        
        for page in range(0, max_pages):
            start_param = page * 10
            search_url = f"https://yandex.com/search/?text={encoded_dork}&p={page}"
            
            content = await self._make_request(search_url)
            if not content:
                continue
                
            # Extract links from Yandex search results
            link_start = 0
            while True:
                link_start = content.find('<a href="http', link_start)
                if link_start == -1:
                    break
                
                link_start = content.find('href="', link_start) + 6
                link_end = content.find('"', link_start)
                
                if link_end != -1:
                    url = content[link_start:link_end]
                    # Filter out Yandex's own domains
                    if not any(domain in url for domain in ['yandex.com', 'yandex.ru']):
                        results.append(url)
                
                link_start = link_end
        
        return results


class DorkingPRO:
    """Main class for DorkingPRO tool"""
    
    def __init__(self, args):
        """Initialize DorkingPRO
        
        Args:
            args: Command line arguments
        """
        self.args = args
        self.results: List[DorkResult] = []
        self.found_urls: Set[str] = set()
        
    async def initialize(self):
        """Initialize async resources"""
        # Create TCP connector with connection pooling
        connector = aiohttp.TCPConnector(
            limit=10,  # Maximum number of connections
            ttl_dns_cache=300,  # DNS cache TTL in seconds
            ssl=False  # Skip SSL verification for performance
        )
        
        # Create clientsession with the connector
        self.session = aiohttp.ClientSession(connector=connector)
        
        # Initialize search engines
        self.search_engines = SearchEngines(
            session=self.session,
            delay=self.args.delay,
            timeout=self.args.timeout,
            debug=self.args.debug
        )
        
    async def close(self):
        """Close resources"""
        await self.session.close()
    
    def load_dorks(self) -> List[str]:
        """Load dorks from file or command line
        
        Returns:
            List[str]: List of dorks to search
        """
        dorks = []
        
        # Process dork from command line
        if self.args.dork:
            dorks.append(self.args.dork)
        
        # Process dorks from file
        if self.args.dork_file:
            try:
                with open(self.args.dork_file, 'r', encoding='utf-8') as f:
                    file_dorks = [line.strip() for line in f if line.strip()]
                    dorks.extend(file_dorks)
            except (IOError, FileNotFoundError) as e:
                print(f"{Fore.RED}[ERROR] Failed to read dork file: {str(e)}")
                sys.exit(1)
        
        # Apply domain to dorks if provided
        if self.args.domain:
            domain = self.args.domain
            
            # If we have no dorks but a domain, use a default set
            if not dorks:
                dorks = [
                    "inurl:admin",
                    "inurl:login",
                    "inurl:phpmyadmin",
                    "inurl:wp-admin",
                    "inurl:upload",
                    "inurl:config",
                    "intext:\"sql syntax near\"",
                    "filetype:sql",
                    "filetype:env",
                    "filetype:log",
                    "ext:php intitle:phpinfo \"published by the PHP Group\"",
                    "inurl:index.php?id=",
                    "inurl:view.php?id="
                ]
            
            # Apply domain to all dorks
            processed_dorks = []
            for dork in dorks:
                # Check if dork already has site: operator
                if "site:" in dork:
                    processed_dorks.append(dork)
                else:
                    processed_dorks.append(f"site:{domain} {dork}")
            
            return processed_dorks
        
        return dorks
    
    async def validate_url(self, url: str) -> Optional[int]:
        """Validate if URL is accessible
        
        Args:
            url: URL to validate
            
        Returns:
            Optional[int]: HTTP status code if successful, None otherwise
        """
        try:
            # Use a short timeout for validation
            async with self.session.head(
                url, 
                allow_redirects=True, 
                timeout=self.args.timeout,
                headers={'User-Agent': ua.random}
            ) as response:
                return response.status
        except Exception:
            return None
    
    async def process_dork(self, dork: str, engine_name: str, max_pages: int) -> List[DorkResult]:
        """Process a single dork with a specific search engine
        
        Args:
            dork: Search dork
            engine_name: Name of the search engine
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List[DorkResult]: List of results for this dork
        """
        urls = []
        
        # Choose the appropriate search method based on engine name
        if engine_name == 'google':
            urls = await self.search_engines.search_google(dork, max_pages)
        elif engine_name == 'bing':
            urls = await self.search_engines.search_bing(dork, max_pages)
        elif engine_name == 'duckduckgo':
            urls = await self.search_engines.search_duckduckgo(dork, max_pages)
        elif engine_name == 'yahoo':
            urls = await self.search_engines.search_yahoo(dork, max_pages)
        elif engine_name == 'yandex':
            urls = await self.search_engines.search_yandex(dork, max_pages)
        
        # Create result objects
        dork_results = []
        
        # Validate URLs if required
        for url in urls:
            # Skip if URL is already found and no-duplicate is enabled
            if self.args.no_duplicate and url in self.found_urls:
                continue
            
            # Add URL to found URLs set
            self.found_urls.add(url)
            
            # Validate URL if validation is enabled
            status_code = None
            if self.args.validate:
                status_code = await self.validate_url(url)
                if status_code is None or status_code >= 400:
                    continue
            
            # Create and add result
            result = DorkResult(
                dork=dork,
                url=url,
                engine=engine_name,
                status_code=status_code
            )
            dork_results.append(result)
        
        return dork_results

    async def run_search(self) -> List[DorkResult]:
        """Run search across all dorks and engines
        
        Returns:
            List[DorkResult]: Combined search results
        """
        # Load dorks
        dorks = self.load_dorks()
        if not dorks:
            print(f"{Fore.RED}[ERROR] No dorks provided or found in file")
            return []
        
        # Determine which engines to use
        engines = ['google', 'bing', 'duckduckgo', 'yahoo', 'yandex']
        if self.args.engine != 'all':
            engines = [self.args.engine]
        
        # Setup progress bar
        total_tasks = len(dorks) * len(engines)
        progress_bar = tqdm(
            total=total_tasks,
            desc="Processing dorks",
            unit="search",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        
        # Create tasks for all combinations of dorks and engines
        tasks = []
        for dork in dorks:
            for engine in engines:
                task = self.process_dork(dork, engine, self.args.max_pages)
                tasks.append(task)
        
        # Process tasks with progress updates
        all_results = []
        for future in asyncio.as_completed(tasks):
            result = await future
            all_results.extend(result)
            progress_bar.update(1)
        
        progress_bar.close()
        return all_results

    def save_results(self, results: List[DorkResult]) -> None:
        """Save results to output file
        
        Args:
            results: List of search results
        """
        if not results:
            print(f"{Fore.YELLOW}[INFO] No results found")
            return
        
        print(f"{Fore.GREEN}[+] Found {len(results)} unique URLs")
        
        if not self.args.output:
            # Just print some results if no output file specified
            print(f"{Fore.CYAN}[+] Top {min(10, len(results))} results:")
            for i, result in enumerate(results[:10], 1):
                print(f"{i}. {result.url} ({result.engine})")
            return
        
        # Determine output format from file extension
        output_file = self.args.output
        file_ext = os.path.splitext(output_file)[1].lower()
        
        try:
            if file_ext == '.json':
                # Save as JSON
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump([asdict(r) for r in results], f, indent=2)
            elif file_ext == '.csv':
                # Save as CSV
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("dork,url,engine,status_code\n")
                    for result in results:
                        f.write(f'"{result.dork}","{result.url}","{result.engine}","{result.status_code}"\n')
            else:
                # Default to TXT (just URLs, one per line)
                with open(output_file, 'w', encoding='utf-8') as f:
                    for result in results:
                        f.write(f"{result.url}\n")
            
            print(f"{Fore.GREEN}[+] Results saved to {output_file}")
            
        except IOError as e:
            print(f"{Fore.RED}[ERROR] Failed to save results: {str(e)}")


async def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="DorkingPRO - Advanced Search Engine Dorking Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Input options
    input_group = parser.add_argument_group('Input Options')
    input_group.add_argument('--domain', type=str, help='Target domain (e.g., example.com)')
    input_group.add_argument('--dork', type=str, help='Single dork to search')
    input_group.add_argument('--dork-file', type=str, help='File containing list of dorks')
    
    # Search engine options
    engine_group = parser.add_argument_group('Search Engine Options')
    engine_group.add_argument(
        '--engine', 
        choices=['google', 'bing', 'duckduckgo', 'yahoo', 'yandex', 'all'],
        default='google',
        help='Search engine to use (default: google)'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('--output', type=str, help='Output file (.json, .csv, or .txt)')
    output_group.add_argument('--validate', action='store_true', help='Validate URLs are accessible')
    output_group.add_argument('--no-duplicate', action='store_true', help='Remove duplicate URLs')
    
    # Advanced options
    advanced_group = parser.add_argument_group('Advanced Options')
    advanced_group.add_argument('--delay', type=int, default=2, help='Delay between requests in seconds (default: 2)')
    advanced_group.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    advanced_group.add_argument('--max-pages', type=int, default=3, help='Maximum number of result pages to fetch (default: 3)')
    advanced_group.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    # Check for required arguments
    if not args.domain and not args.dork and not args.dork_file:
        parser.error("At least one of --domain, --dork, or --dork-file is required")
    
    # Print banner
    print(BANNER)

    
    # Initialize and run
    dorking = DorkingPRO(args)
    await dorking.initialize()
    
    try:
        print(f"{Fore.CYAN}[*] Starting search...")
        results = await dorking.run_search()
        dorking.save_results(results)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Search interrupted by user")
    finally:
        await dorking.close()
    
    print(f"{Fore.GREEN}[+] Search completed")


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
