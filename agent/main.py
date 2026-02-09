"""
Self-Healing-Sandbox Agent - Autonomous QA Agent
Demonstrates Gemini AI with thinking + E2B sandbox + Playwright.

Required environment variables:
  - GEMINI_API_KEY: Get from https://aistudio.google.com/apikey
  - E2B_API_KEY: Get from https://e2b.dev/dashboard
"""

import asyncio
import os
from google import genai
from google.genai import types
from e2b import Sandbox

# Configuration from GEMINI.md
GEMINI_MODEL = "gemini-3-pro-preview"
THINKING_LEVEL = "high"  # Budget for thinking tokens


def init_gemini_client():
    """Initialize Gemini client with thinking enabled."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    client = genai.Client(api_key=api_key)
    return client


def analyze_bug_report(client, bug_report: str) -> dict:
    """Use Gemini to analyze a bug report and extract reproduction steps."""
    print("🧠 Analyzing bug report with Gemini (thinking enabled)...")
    
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=bug_report,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=10000  # High thinking budget
            ),
            system_instruction="""You are an autonomous QA agent. Analyze the bug report 
            and extract: 1) URL to test, 2) Steps to reproduce, 3) Expected vs actual behavior.
            Return as JSON with keys: url, steps, expected, actual."""
        )
    )
    
    # Extract thoughts (thinking process) and final response
    result = {
        "thoughts": [],
        "response": ""
    }
    
    for part in response.candidates[0].content.parts:
        if part.thought:
            result["thoughts"].append(part.text)
            print(f"  💭 Thought: {part.text[:100]}...")
        else:
            result["response"] = part.text
    
    return result


async def main():
    print("=" * 60)
    print("🤖 Self-Healing-Sandbox Agent")
    print("=" * 60)
    
    # Step 1: Initialize Gemini AI
    print("\n📡 Initializing Gemini AI (gemini-3-pro-preview)...")
    client = init_gemini_client()
    print("✅ Gemini client ready with thinking_level=high")
    
    # Step 2: Demo - Analyze a sample bug report
    sample_bug = """
    Bug: Login button doesn't work on mobile.
    User says: "I tried clicking login on my phone but nothing happens."
    URL: https://example.com/login
    """
    
    analysis = analyze_bug_report(client, sample_bug)
    print(f"\n📋 Analysis Result:\n{analysis['response'][:500]}")
    
    # Step 3: Start E2B Sandbox
    print("\n🚀 Starting E2B Sandbox...")
    sandbox = Sandbox()
    print(f"✅ Sandbox created with ID: {sandbox.id}")
    
    # Install playwright inside the sandbox
    print("📦 Installing Playwright in sandbox...")
    sandbox.commands.run("pip install playwright && playwright install chromium")
    
    # Create a simple Playwright script to navigate to a URL
    playwright_script = """
import asyncio
from playwright.async_api import async_playwright

async def navigate():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://example.com")
        title = await page.title()
        print(f"Page Title: {title}")
        await browser.close()
        return title

asyncio.run(navigate())
"""
    
    # Write and execute the script in the sandbox
    sandbox.files.write("/home/user/navigate.py", playwright_script)
    print("🌐 Navigating to https://example.com...")
    
    result = sandbox.commands.run("python /home/user/navigate.py")
    print(f"📄 Result: {result.stdout}")
    
    # Keep sandbox alive for demonstration
    print("⏳ Sandbox is alive. Press Ctrl+C to terminate.")
    try:
        await asyncio.sleep(60)  # Keep alive for 60 seconds
    except KeyboardInterrupt:
        pass
    
    # Cleanup
    sandbox.kill()
    print("🛑 Sandbox terminated.")

if __name__ == "__main__":
    asyncio.run(main())
