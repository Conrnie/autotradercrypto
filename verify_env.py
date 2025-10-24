#!/usr/bin/env python3
"""
Quick script to verify your .env file is set up correctly
"""

import os
from dotenv import load_dotenv
from termcolor import cprint

# Load .env file
load_dotenv()

cprint("\n🔍 Verifying Environment Variables...\n", "cyan", attrs=['bold'])

# Check required keys
required_keys = {
    'DEEPSEEK_KEY': 'DeepSeek AI API (REQUIRED for trading)',
    'HYPER_LIQUID_KEY': 'Hyperliquid Testnet Key (REQUIRED for trading)'
}

# Check optional keys
optional_keys = {
    'MOONDEV_API_KEY': 'Moon Dev API (for liquidation data)',
    'ANTHROPIC_KEY': 'Anthropic Claude (not used currently)',
    'OPENAI_KEY': 'OpenAI GPT (not used currently)',
    'GROQ_API_KEY': 'Groq (not used currently)',
}

all_good = True

# Check required keys
cprint("Required Keys:", "cyan", attrs=['bold'])
for key, description in required_keys.items():
    value = os.getenv(key)
    if value and len(value.strip()) > 20 and 'your_' not in value.lower():
        cprint(f"  ✅ {key}: Found ({len(value)} chars)", "green")
        cprint(f"     {description}", "white")
    else:
        cprint(f"  ❌ {key}: NOT FOUND or PLACEHOLDER", "red")
        cprint(f"     {description}", "white")
        all_good = False

cprint("\nOptional Keys:", "cyan", attrs=['bold'])
for key, description in optional_keys.items():
    value = os.getenv(key)
    if value and len(value.strip()) > 20 and 'your_' not in value.lower():
        cprint(f"  ✅ {key}: Found ({len(value)} chars)", "green")
    else:
        cprint(f"  ⚠️  {key}: Not set", "yellow")
    cprint(f"     {description}", "white")

cprint("\n" + "="*60, "cyan")

if all_good:
    cprint("✅ ALL REQUIRED KEYS ARE SET!", "green", attrs=['bold'])
    cprint("🚀 You're ready to run the trading system!", "green")
    cprint("\nRun: python src/main.py", "cyan")
else:
    cprint("❌ MISSING REQUIRED KEYS!", "red", attrs=['bold'])
    cprint("⚠️  Please add the missing keys to your .env file", "yellow")
    cprint("\nLocation: /home/user/autotradeclone/.env", "cyan")

cprint("="*60 + "\n", "cyan")
