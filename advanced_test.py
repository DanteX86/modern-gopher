#!/usr/bin/env python3

import requests
import json

def fetch_data(url):
    response = requests.get(url)
    return response.json()

def process_user(user_id):
    user_data = fetch_data(f"https://api.example.com/users/{user_id}")
    return user_data

class APIClient:
    def __init__(self):
        self.base_url = "https://api.example.com"
    
    def get_user(self, user_id):
        url = f"{self.base_url}/users/{user_id}"
        response = requests.get(url)
        return response.json()
    
    def get_posts(self, user_id):
        url = f"{self.base_url}/users/{user_id}/posts"
        response = requests.get(url)
        return response.json()

# Configuration
config = {
    "api_key": "secret123",
    "timeout": 30,
    "retries": 3
}

def main():
    client = APIClient()
    user = client.get_user(123)
    posts = client.get_posts(123)
    print(f"User: {user}")
    print(f"Posts: {posts}")

if __name__ == "__main__":
    main()

