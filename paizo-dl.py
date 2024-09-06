import requests
import time
import os
import argparse
import zipfile
from bs4 import BeautifulSoup

# Define constants
ASSETS_URL = "https://paizo.com/paizo/account/assets"
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
DOWNLOAD_DIR = "downloads"  # Directory to save the downloaded files
MAX_RETRIES = 3  # Number of retries if download fails

# Headers extracted from the curl command
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,nb;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://paizo.com/paizo/account/assets',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': USER_AGENT
}

# Cookies extracted from the curl command
COOKIES = {
    'sessionId': 'CHANGEME',  # Replace with your actual sessionId from the browser
    '_pk_id.1.638a': '156ac78b02e09b8e.1725558046.',
    '_pk_ses.1.638a': '1'
}

def fetch_assets(session, debug=False):
    """Fetch the list of digital assets and their download packages from Paizo."""
    print(f"Fetching assets from: {ASSETS_URL}")
    response = session.get(ASSETS_URL)

    if debug:
        print(f"Response Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Failed to load assets page. Status code: {response.status_code}")
        return []

    # Debug: Print a portion of the HTML response for inspection
    if debug:
        print("Snippet of fetched HTML (first 1000 characters):")
        print(response.text[:1000])  # Print the first 1000 characters of the HTML for debugging

    # Parse the HTML response
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find and extract asset information
    assets = []
    tbodies = soup.find_all('tbody')

    if debug:
        print(f"Number of <tbody> elements found: {len(tbodies)}")

    for tbody in tbodies:
        asset_link = tbody.find('a')
        if asset_link and 'digitalAsset' in asset_link['href']:
            hex_id = asset_link['href'].split('digitalAsset=')[1].split('&')[0]
            asset_name = asset_link.find('b').text.strip()

            # Extract format or version (e.g., "Single File" or "File Per Chapter")
            version_span = tbody.find('span', class_='tiny no-wrap')
            asset_version = version_span.text.strip() if version_span else "Unknown Format"
            asset_name_with_version = f"{asset_name} ({asset_version})"

            download_package = extract_download_package(tbody)  # Dynamically extract the correct download package

            assets.append({
                'hex_id': hex_id,
                'name': asset_name_with_version,
                'download_package': download_package
            })

    return assets

def extract_download_package(tbody):
    """Extract the download package dynamically from the HTML."""
    download_link = tbody.find('a', href=True)
    if download_link and 'downloadPackage=' in download_link['href']:
        download_package = download_link['href'].split('downloadPackage=')[1].split('&')[0]
        return download_package
    return None  # Fallback if not found

def get_unique_filename(file_path):
    """Check if the file exists and generate a unique file name by appending a number."""
    base, ext = os.path.splitext(file_path)
    counter = 1
    while os.path.exists(file_path):
        file_path = f"{base}-({counter}){ext}"
        counter += 1
    return file_path

def start_personalization_process(session, hex_id, download_package, debug=False):
    """Send a request to start the personalization process for the asset."""
    personalization_url = f"https://paizo.com/cgi-bin/WebObjects/Store.woa/wa/Personalizer/downloadDigitalAsset?digitalAsset={hex_id}&downloadPackage={download_package}&_r=true"
    
    # Send the request to initiate personalization
    if debug:
        print(f"Initiating personalization for asset {hex_id}...")
    response = session.get(personalization_url)

    if response.status_code == 200:
        if debug:
            print(f"Personalization started for {hex_id}. Waiting for server to prepare the asset.")
        time.sleep(40)  # Adjust this delay to ensure server has time to personalize the asset
    else:
        print(f"Failed to start personalization for {hex_id}. Status code: {response.status_code}")

def download_asset(session, hex_id, download_package, asset_name, debug=False):
    """Download the asset after personalization completes with retries."""
    retry_count = 0
    while retry_count < MAX_RETRIES:
        download_check_url = f"https://paizo.com/cgi-bin/WebObjects/Store.woa/wa/Personalizer/downloadDigitalAsset?digitalAsset={hex_id}&downloadPackage={download_package}&_r=true"
        if debug:
            print(f"Fetching and downloading asset for {hex_id} (Attempt {retry_count + 1}/{MAX_RETRIES})...")

        # Send the request to fetch the asset
        response = session.get(download_check_url, stream=True)

        content_type = response.headers.get('Content-Type', '')
        
        if response.status_code == 200:
            # Determine the file extension based on the content type
            if 'application/pdf' in content_type:
                file_extension = '.pdf'
            elif 'application/zip' in content_type or 'application/octet-stream' in content_type:
                file_extension = '.zip'
            elif 'html' in content_type:
                print(f"Received HTML page instead of the file for {asset_name}. Retrying...")
                retry_count += 1
                time.sleep(10)  # Wait before retrying
                continue  # Retry the download
            else:
                file_extension = '.bin'  # Fallback to binary if unsure

            if debug:
                print(f"Downloading file for asset {hex_id} (Content-Type: {content_type})...")
            
            # Ensure the download directory exists
            if not os.path.exists(DOWNLOAD_DIR):
                os.makedirs(DOWNLOAD_DIR)
            
            # Generate a unique file name
            file_name = f"{asset_name}{file_extension}"
            file_path = os.path.join(DOWNLOAD_DIR, file_name)
            file_path = get_unique_filename(file_path)  # Ensure unique file name

            # Save the file
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive new chunks
                        file.write(chunk)
            print(f"{asset_name} downloaded successfully and saved to {file_path}")

            # Unzip if it's a zip file and rename contents
            if file_extension == '.zip':
                unzip_and_rename(file_path, asset_name)
            return  # Exit after a successful download
        else:
            print(f"Failed to download {asset_name}. Status code: {response.status_code}")
            print(f"Content-Type: {content_type}")
            retry_count += 1
            time.sleep(10)  # Wait before retrying

    print(f"Failed to download {asset_name} after {MAX_RETRIES} attempts. Skipping.")

def unzip_and_rename(zip_path, asset_name):
    """Unzip the downloaded zip file and rename its contents based on the asset name."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        extract_dir = os.path.splitext(zip_path)[0]
        zip_ref.extractall(extract_dir)

        # Rename all extracted files based on the asset name
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                old_path = os.path.join(root, file)
                new_name = f"{asset_name}_{file}"
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)

        print(f"Unzipped and renamed files in: {extract_dir}")

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Paizo Digital Assets Downloader")
    parser.add_argument('--list-assets', action='store_true', help="List all available assets without downloading.")
    parser.add_argument('--debug', action='store_true', help="Enable debug output.")
    args = parser.parse_args()

    # Initialize session
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)

    # Fetch all assets
    assets = fetch_assets(session, debug=args.debug)
    if not assets:
        print("No digital assets found.")
        return

    # If listing assets, print them and exit
    if args.list_assets:
        print("Available Digital Assets:")
        for idx, asset in enumerate(assets):
            print(f"{idx + 1}. Hex ID: {asset['hex_id']} - Name: {asset['name']}")
        return

    # Iterate over each asset and download one at a time
    for asset in assets:
        start_personalization_process(session, asset['hex_id'], asset['download_package'], debug=args.debug)
        print(f"Waiting for asset {asset['name']} to be ready for download...")
        time.sleep(40)  # Adjust delay if needed to wait for personalization to complete

        download_asset(session, asset['hex_id'], asset['download_package'], asset['name'], debug=args.debug)

if __name__ == "__main__":
    main()

