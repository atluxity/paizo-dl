
# Paizo Digital Asset Downloader

This Python script allows you to automate the process of downloading digital assets from Paizo.com. It handles logging in, asset personalization, and downloading all available digital content, including PDFs and ZIP files. It also supports retrying failed downloads and properly naming downloaded files, avoiding overwrites.

## Features

- **Asset Listing**: Lists all available assets and allows you to choose which assets to download.
- **Personalization**: Automates the asset personalization process before downloading.
- **Dynamic File Naming**: Ensures that files are saved with unique names, appending numbers to filenames if necessary.
- **ZIP Extraction**: Automatically unzips downloaded ZIP files and renames their contents.
- **Error Handling**: Retries downloads up to 3 times in case of errors.
- **Debug Output**: Provides detailed information during the download process for troubleshooting.

## Installation

1. Clone the repository:
    \`\`\`bash
    git clone https://github.com/yourusername/paizo-dl.git
    cd paizo-dl
    \`\`\`

2. Install the required Python packages:
    \`\`\`bash
    pip install -r requirements.txt
    \`\`\`

## Usage

### Listing Available Assets

To list all available digital assets on your Paizo account without downloading them:

\`\`\`bash
python3 paizo-dl.py --list-assets
\`\`\`

### Downloading All Assets

To download all available digital assets:

\`\`\`bash
python3 paizo-dl.py
\`\`\`

### Debug Mode

To enable debug output for more detailed information:

\`\`\`bash
python3 paizo-dl.py --debug
\`\`\`

### Command Line Arguments

- \`--list-assets\`: List all available assets without downloading.
- \`--debug\`: Enable debug output for detailed information.

## Requirements

- Python 3.6+
- \`requests\`
- \`beautifulsoup4\`
- \`zipfile\`

To install the dependencies:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Configuration

### Cookies

The script uses session cookies to log into Paizo.
First open your browser, navigate to paizo.com, authenticate
Use web developer tools to grab the sessionID cookie
Put it in the source code.
Repeat with any other cookie for good measure.
Keep the browser window open, if script cant load assets recheck that the browser is still logged in

### Credentials

Line 35 in the code, where you configure the COOKIES, put a working sessionID.

## Known Issues

- Auth could be handled better... A bit ugly to use SessionID like this
- Some assets may require multiple retries due to server-side delays in personalization. The script will retry downloads up to 3 times.
- If the paizo.com website ever changes, even slightly, this script will probably break. Its a whack a mole game. Good luck.

## Contributing

Feel free to open issues or submit pull requests to improve the script!

1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Commit your changes.
4. Push your branch and open a pull request.

## License

This project is licensed under the MIT License.

---

## Author

[Hans-Petter Fjeld aka atluxity](https://github.com/atluxity)

---

### Example

Here’s an example of running the script to download all assets:

\`\`\`bash
python3 paizo-dl.py --debug
\`\`\`

The script will handle personalization, download assets, and rename files to prevent overwrites.
