#!/usr/bin/env python3
"""
Test script to verify which models are actually available via Azure AI API.
Tests each model and saves only working ones to available_models.txt
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
BASE_URL = os.getenv("BASE_URL", "https://llmapihackathon.services.ai.azure.com/")
API_KEY = os.getenv("API_KEY", "")
API_VERSION = os.getenv("API_VERSION", "2024-12-01-preview")

if not API_KEY:
    print("ERROR: API_KEY not set in environment variables")
    exit(1)

print(f"Testing Azure AI API Models")
print(f"Base URL: {BASE_URL}")
print(f"API Version: {API_VERSION}\n")

# Read current models list
with open('available_models.txt', 'r') as f:
    all_models = [line.strip() for line in f.readlines() if line.strip()]

print(f"Testing {len(all_models)} models...\n")

working_models = []
failed_models = []

# Test each model with a simple deployment call
for i, model in enumerate(all_models, 1):
    try:
        # Test with chat endpoint via Azure API
        url = f"{BASE_URL}deployments/{model}/chat/completions?api-version={API_VERSION}"
        
        headers = {
            "api-key": API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 10
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=2)
        
        if response.status_code in [200, 400, 429]:  # 200=success, 400=bad request, 429=rate limited (but model exists)
            print(f"✓ [{i}/{len(all_models)}] {model}")
            working_models.append(model)
        elif response.status_code == 404:
            print(f"✗ [{i}/{len(all_models)}] {model} - 404 Not Found (model not deployed)")
            failed_models.append((model, 404))
        else:
            print(f"? [{i}/{len(all_models)}] {model} - HTTP {response.status_code}")
            # Try to get error details
            try:
                error = response.json().get('error', {})
                if 'deployment' in str(error).lower() or 'not found' in str(error).lower():
                    failed_models.append((model, response.status_code))
                else:
                    working_models.append(model)  # Other errors might mean model exists
                    print(f"  → Keeping (not a deployment error)")
            except:
                # If can't parse, assume model might work
                working_models.append(model)
                print(f"  → Keeping (couldn't parse error)")
                
    except requests.Timeout:
        print(f"✗ [{i}/{len(all_models)}] {model} - Timeout (model unreachable)")
        failed_models.append((model, "Timeout"))
    except Exception as e:
        print(f"✗ [{i}/{len(all_models)}] {model} - {type(e).__name__}: {str(e)[:40]}")
        failed_models.append((model, type(e).__name__))

print(f"\n{'='*70}")
print(f"RESULTS: {len(working_models)} WORKING, {len(failed_models)} FAILED")
print(f"{'='*70}\n")

if working_models:
    print(f"✓ WORKING MODELS ({len(working_models)}):")
    for model in working_models:
        print(f"  - {model}")
else:
    print("✗ NO WORKING MODELS FOUND")

if failed_models:
    print(f"\n✗ FAILED MODELS ({len(failed_models)}):")
    for model, error in failed_models[:10]:
        print(f"  - {model} ({error})")
    if len(failed_models) > 10:
        print(f"  ... and {len(failed_models) - 10} more")

# Save working models to file
print(f"\n{'='*70}")
print(f"Saving {len(working_models)} working models to available_models.txt...")
print(f"{'='*70}\n")

with open('available_models.txt', 'w') as f:
    for model in working_models:
        f.write(f"{model}\n")

print(f"✓ Updated available_models.txt with {len(working_models)} working models")
print(f"\nRun this script periodically to keep the list current!")
