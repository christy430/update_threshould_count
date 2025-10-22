import os
import re
import requests
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
API_KEY = os.getenv("DATADOG_API_KEY")
APP_KEY = os.getenv("DATADOG_APP_KEY")

if not API_KEY or not APP_KEY:
    raise Exception("Missing Datadog API or APP key in environment variables.")

BASE_URL = "https://api.datadoghq.com/api/v1/monitor"


def update_monitor_query_threshold(monitor_id, new_threshold):
    """Fetch monitor query, replace old threshold, and update."""
    headers = {
        "Content-Type": "application/json",
        "DD-API-KEY": API_KEY,
        "DD-APPLICATION-KEY": APP_KEY,
    }

    # Fetch monitor details
    print(f"🔍 Fetching monitor {monitor_id} details...")
    response = requests.get(f"{BASE_URL}/{monitor_id}", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to fetch monitor details:", response.text)
        return

    monitor = response.json()
    query = monitor["query"]
    print(f"📄 Current query:\n{query}")

    # Replace the threshold number in the query (e.g. "> 2" -> "> 3")
    updated_query = re.sub(r">\s*\d+(\.\d+)?", f"> {new_threshold}", query)
    print(f"✏️ Updated query:\n{updated_query}")

    # Update the monitor with the modified query
    payload = {"query": updated_query}
    put_response = requests.put(
        f"{BASE_URL}/{monitor_id}", headers=headers, json=payload
    )

    if put_response.status_code == 200:
        print(f"✅ Monitor {monitor_id} threshold updated successfully!")
        print("🆕 New query:", put_response.json().get("query"))
    else:
        print("❌ Failed to update monitor.")
        print("Status:", put_response.status_code)
        print("Response:", put_response.text)


if __name__ == "__main__":
    monitor_id = input("Enter your Datadog Monitor ID: ").strip()
    new_threshold = input("Enter new threshold value: ").strip()

    try:
        new_threshold = float(new_threshold)
        update_monitor_query_threshold(monitor_id, new_threshold)
    except ValueError:
        print("❌ Please enter a valid number for the threshold.")
