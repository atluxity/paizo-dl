import os
import requests
import getpass
import json

# Define constants
LOGIN_URL = "https://paizo.com/cgi-bin/WebObjects/Store.woa/wa/DirectAction/signIn?path=paizo"
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
COOKIE_FILE = "paizo_cookies.json"
CREDENTIALS_FILE = "paizo_credentials.json"

def get_credentials():
    # First, check if credentials file exists
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            credentials = json.load(file)
            return credentials['email'], credentials['password']

    # Second, check environment variables
    email = os.getenv('PAIZO_EMAIL')
    password = os.getenv('PAIZO_PASSWORD')

    if email and password:
        return email, password

    # Lastly, prompt the user for credentials
    email = input("Enter your Paizo email: ")
    password = getpass.getpass("Enter your Paizo password: ")

    # Save credentials for future use
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump({'email': email, 'password': password}, file)

    return email, password

def login_and_save_cookies():
    email, password = get_credentials()

    # Setup session
    session = requests.Session()

    # Set user agent
    session.headers.update({
        'User-Agent': USER_AGENT,
        'accept': 'text/javascript, text/html, application/xml, text/xml, */*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://paizo.com',
        'referer': LOGIN_URL,
        'x-prototype-version': '1.6.1',
        'x-requested-with': 'XMLHttpRequest'
    })

    # Prepare login data
    login_data = {
        'path': 'paizo',
        'e': email,
        'zzz': password,
        'AJAX_SUBMIT_BUTTON_NAME': '0.1.15.11.3.1.3.2.3.3.7.3.2.1.3.1.1.5',
    }

    # Perform login
    response = session.post(LOGIN_URL, data=login_data)

    if response.status_code == 200:
        # Save cookies for future use
        with open(COOKIE_FILE, 'w') as file:
            json.dump(session.cookies.get_dict(), file)
        print("Login successful. Cookies saved.")
    else:
        print(f"Login failed. Status code: {response.status_code}")

def load_cookies():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, 'r') as file:
            cookies = json.load(file)
        return cookies
    return None

if __name__ == "__main__":
    # Log in and save cookies if necessary
    login_and_save_cookies()

