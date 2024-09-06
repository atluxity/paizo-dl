import requests
import time
import os
from bs4 import BeautifulSoup

# Define constants
ASSETS_URL = "https://paizo.com/paizo/account/assets"
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
DOWNLOAD_DIR = "downloads"  # Directory to save the downloaded files

# Headers extracted from the curl command
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,nb;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://paizo.com/paizo/account/assets',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-request': '1',
    'user-agent': USER_AGENT,
}

# Cookies extracted from the curl command
COOKIES = {
    'sessionId': 'ChbbbbbcN40ysCxMNZZVw0',  # Replace with your actual sessionId from the browser
    '_pk_id.1.638a': '156ac78b02e09b8e.1725558046.',
    '_pk_ses.1.638a': '1'
}

def fetch_assets(session):
    """Fetch the list of digital assets from Paizo."""
    print(f"Fetching assets from: {ASSETS_URL}")
    response = session.get(ASSETS_URL)

    print(f"Response Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Failed to load assets page. Status code: {response.status_code}")
        return []

    # Debug: Print a portion of the HTML response for inspection
    print("Snippet of fetched HTML (first 1000 characters):")
    print(response.text[:1000])  # Print the first 1000 characters of the HTML for debugging

    # Parse the HTML response
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find and extract asset information
    assets = []
    tbodies = soup.find_all('tbody')

    print(f"Number of <tbody> elements found: {len(tbodies)}")

    for tbody in tbodies:
        asset_link = tbody.find('a')
        if asset_link and 'digitalAsset' in asset_link['href']:
            hex_id = asset_link['href'].split('digitalAsset=')[1].split('&')[0]
            asset_name = asset_link.find('b').text.strip()
            download_package = "v5748q6o2wrkm"  # You may want to scrape or set a proper download package per asset

            assets.append({
                'hex_id': hex_id,
                'name': asset_name,
                'download_package': download_package
            })

    return assets

def start_personalization_process(session, hex_id, download_package):
    """Send a request to start the personalization process for the asset."""
    personalization_url = f"https://paizo.com/cgi-bin/WebObjects/Store.woa/wa/Personalizer/downloadDigitalAsset?digitalAsset={hex_id}&downloadPackage={download_package}&_r=true"
    
    # Send the request to initiate personalization
    print(f"Initiating personalization for asset {hex_id}...")
    response = session.get(personalization_url)

    if response.status_code == 200:
        print(f"Personalization started for {hex_id}.")
    else:
        print(f"Failed to start personalization for {hex_id}. Status code: {response.status_code}")

def download_asset(session, hex_id, download_package, asset_name):
    """Download the asset after personalization completes."""
    download_check_url = f"https://paizo.com/cgi-bin/WebObjects/Store.woa/wa/Personalizer/downloadDigitalAsset?digitalAsset={hex_id}&downloadPackage={download_package}&_r=true"
    print(f"Fetching and downloading asset for {hex_id}...")

    # Send the request to fetch the asset
    response = session.get(download_check_url, stream=True)

    if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('application/octet-stream'):
        # The server is returning the file directly
        print(f"Downloading file for asset {hex_id}...")
        
        # Ensure the download directory exists
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        
        # Save the file to the downloads directory
        file_name = f"{asset_name}.pdf"  # You can adjust this based on the actual file type
        file_path = os.path.join(DOWNLOAD_DIR, file_name)

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    file.write(chunk)
        print(f"{asset_name} downloaded successfully and saved to {file_path}")
    else:
        print(f"Failed to download {asset_name}. Status code: {response.status_code}")
        if response.headers.get('Content-Type'):
            print(f"Content-Type: {response.headers['Content-Type']}")

def main():
    # Initialize session
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)

    # Step 1: Fetch all assets
    assets = fetch_assets(session)
    if not assets:
        print("No digital assets found.")
        return

    # Step 2: Initiate personalization for each asset
    for asset in assets:
        start_personalization_process(session, asset['hex_id'], asset['download_package'])
        time.sleep(0.5)  # Short delay between requests

    # Step 3: Wait for personalization to complete (approx 30 seconds)
    print("Waiting 30 seconds for personalization to complete...")
    time.sleep(30)  # Adjust delay if needed

    # Step 4: Fetch and download each asset
    for asset in assets:
        download_asset(session, asset['hex_id'], asset['download_package'], asset['name'])

if __name__ == "__main__":
    main()

