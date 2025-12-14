#!/usr/bin/env python3
"""
Discover deployed models using OpenAI SDK with Azure Foundry endpoint.
Tests each deployment and saves working models to available_models.txt
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

if not BASE_URL or not API_KEY:
    print("ERROR: Missing BASE_URL or API_KEY in .env file")
    sys.exit(1)

# Ensure correct endpoint format
if not BASE_URL.endswith("/openai/v1/"):
    BASE_URL = BASE_URL.rstrip("/") + "/openai/v1/"

print(f"🔍 Connecting to Azure Foundry...")
print(f"   Base URL: {BASE_URL}")
print()

# Initialize OpenAI-compatible client for Foundry
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

working_models = []
failed_models = []

# Try to list models
print("📋 Attempting to discover models...")
print()

try:
    models_response = client.models.list()
    
    model_list = []
    for model in models_response.data:
        model_name = model.id if hasattr(model, 'id') else str(model)
        model_list.append(model_name)
    
    print(f"✓ Found {len(model_list)} models via API")
    print()
    print("🧪 Testing each model with chat completion...")
    print()
    
    for i, model_name in enumerate(model_list, 1):
        try:
            print(f"[{i}/{len(model_list)}] Testing {model_name}...", end=" ", flush=True)
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'working'"}
                ],
                max_tokens=10,
                timeout=10
            )
            
            print(f"✓ WORKING")
            working_models.append(model_name)
            
        except Exception as e:
            error_msg = str(e).lower()
            # if "404" in error_msg or "not found" in error_msg:
            #     print(f"✗ NOT DEPLOYED (404)")
            # elif "400" in error_msg:
            #     print(f"✗ BAD REQUEST (400)")
            # elif "401" in error_msg or "unauthorized" in error_msg:
            #     print(f"✗ AUTH FAILED (401)")
            # elif "429" in error_msg:
            #     print(f"✗ RATE LIMITED (429)")
            # elif "vision" in error_msg or "not support" in error_msg:
            #     print(f"✗ INCOMPATIBLE")
            # else:
            #     print(f"✗ ERROR")
            failed_models.append((model_name, str(e)[:60]))

except Exception as e:
    print(f"✗ Could not retrieve models list: {e}")
    print()
    print("💡 Falling back to testing known models from screenshot...")
    print()
    
    # Fallback: test models from screenshot
    known_models = [
        "text-embedding-3-large",
        "Phi-4-multimodal-instruct",
        "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "gpt-oss-120b",
        "gpt-5",
        "gpt-5-mini",
        "gpt-4.1",
        "DeepSeek-R1",
        "claude-sonnet-4-5",
        "claude-opus-4-1",
    ]
    
    for i, model_name in enumerate(known_models, 1):
        try:
            # print(f"[{i}/{len(known_models)}] Testing {model_name}...", end=" ", flush=True)
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'working'"}
                ],
                max_tokens=10,
                timeout=10
            )
            
            print(f"[{i}/{len(known_models)}] Testing {model_name}...", end=" ", flush=True)
            print(f"✓ WORKING")
            working_models.append(model_name)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "404" in error_msg or "not found" in error_msg:
                print(f"✗ NOT DEPLOYED (404)")
            elif "400" in error_msg:
                print(f"✗ BAD REQUEST (400)")
            elif "401" in error_msg or "unauthorized" in error_msg:
                print(f"✗ AUTH FAILED (401)")
            elif "429" in error_msg:
                print(f"✗ RATE LIMITED (429)")
            elif "vision" in error_msg or "not support" in error_msg:
                print(f"✗ INCOMPATIBLE")
            else:
                print(f"✗ ERROR")
            failed_models.append((model_name, str(e)[:60]))


print()
print("=" * 70)
print(f"RESULTS: {len(working_models)} WORKING, {len(failed_models)} FAILED")
print("=" * 70)

if working_models:
    print()
    print(f"✓ WORKING MODELS ({len(working_models)}):")
    for model in working_models:
        print(f"  - {model}")
else:
    print()
    print("✗ NO WORKING MODELS FOUND")

print()
print("=" * 70)
print(f"Saving {len(working_models)} working models to available_models.txt...")
print("=" * 70)

# Write working models to file
with open("available_models.txt", "w") as f:
    for model in sorted(working_models):
        f.write(model + "\n")

if working_models:
    print(f"✓ Updated available_models.txt with {len(working_models)} working models")
else:
    print("✓ available_models.txt cleared (no working models found)")

print()
print("Run this script periodically to keep the list current!")
