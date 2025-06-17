#!/usr/bin/env python3

import requests
import json

def fetch_data(url):
    response = requests.get(url, timeout=10)
    return response.json()

def get_user_info(user_id):
    url = f"https://api.example.com/users/{user_id}"
    response = requests.get(url, timeout=10)
    return response.json()

def get_post_data(post_id):
    url = f"https://api.example.com/posts/{post_id}"
    response = requests.get(url, timeout=10)
    return response.json()

class UserService:
    def load_user(self, user_id):
        response = requests.get(f"https://api.example.com/users/{user_id}", timeout=10)
        return response.json()
    
    def save_user(self, user_data):
        response = requests.post("https://api.example.com/users", json=user_data)
        return response.json()

# Old-style error handling
try:
    data = fetch_data("https://example.com/api")
except Exception:
    print("Error occurred")

if __name__ == "__main__":
    print("Starting application")
    user = get_user_info(123)
    post = get_post_data(456)

