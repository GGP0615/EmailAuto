import requests
from config import OPENAI_API_KEY

def print_openai_usage():
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        response = requests.get(
            "https://api.openai.com/v1/dashboard/billing/usage",
            headers=headers
        )
        if response.status_code == 200:
            usage = response.json()
            print(f"OpenAI API usage this period: ${usage['total_usage']/100:.2f} USD")
        else:
            print("Could not fetch OpenAI usage info.")
    except Exception as e:
        print(f"Error fetching OpenAI usage: {e}")
