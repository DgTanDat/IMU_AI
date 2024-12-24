import requests
import json

# Firebase database URL (replace with your own URL)
DATABASE_URL = "https://imucar-default-rtdb.asia-southeast1.firebasedatabase.app/"

# Node to access (e.g., "users.json")
NODE = "instruction.json"

# Optional: Auth token or API key if required
AUTH = "'AIzaSyAJ9NWzrhKBnos2XqpvJes507JcA_sgMog'"

# Construct the URL
url = f"{DATABASE_URL}/{NODE}?auth={AUTH}"  # Add `?auth=` only if auth is required

# Send GET request
response = requests.get(url)

# Handle the response
if response.status_code == 200:
    datas = response.json()
    print("Data retrieved successfully:", datas)
    print(type(datas))
else:
    print("Failed to retrieve data. HTTP Status Code:", response.status_code)
    print("Error message:", response.text)


