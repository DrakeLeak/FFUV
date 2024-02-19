import requests
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re

def crawl_with_assets(url, depth, output_dir):
    # Dictionary to store visited URLs
    visited = {}
    
    # Recursive function to crawl the web
    def crawl_recursive(url, depth):
        if depth == 0:
            return
        if url in visited:
            return
        visited[url] = True
        print("Crawling:", url)
        
        try:
            response = requests.get(url)
            
            # Save the full content and assets
            save_page_and_assets(url, response.text, output_dir)
            
            # Extract links from the page and crawl subpages
            links = get_links(response.text)
            for link in links:
                subpage_url = urljoin(url, link)
                if subpage_url.startswith('http'):
                    crawl_recursive(subpage_url, depth - 1)
        except Exception as e:
            print("Error:", e)
    
    # Start crawling
    crawl_recursive(url, depth)

def get_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    links = [link.get('href') for link in soup.find_all('a', href=True)]
    return links

def save_page_and_assets(url, content, output_dir):
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate filename from URL
    filename = url.replace('/', '_').replace(':', '_').replace('.', '_') + ".html"
    filepath = os.path.join(output_dir, filename)
    
    # Save the full content to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Extract and save CSS and JavaScript files
    soup = BeautifulSoup(content, 'html.parser')
    links = [link.get('href') for link in soup.find_all('link', {'rel': 'stylesheet'})]
    links += [script.get('src') for script in soup.find_all('script', {'src': True})]

    for link in links:
        if link:
            asset_url = urljoin(url, link)
            if asset_url.startswith('http'):
                save_asset(asset_url, output_dir)

def save_asset(asset_url, output_dir):
    filename = os.path.basename(asset_url)
    filepath = os.path.join(output_dir, filename)
    
    # Download the asset
    with open(filepath, 'wb') as f:
        response = requests.get(asset_url)
        f.write(response.content)

# Example usage
crawl_with_assets("https://google.com", 2, "website")
