"""
Agent Brain - Gemini AI Integration
Handles Analysis (Pro) and Scripting/Vision (Flash) layers.
Uses google.generativeai library.
"""

import os
import google.generativeai as genai

# Model configuration - Using Gemini 2.5 Flash
GEMINI_FLASH = "gemini-2.5-flash"    # Latest - for analysis and scripting
GEMINI_VISION = "gemini-2.5-flash"   # Latest - for screenshot analysis (vision)


def configure_client():
    """Configure Gemini API key."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable required")
    genai.configure(api_key=api_key)


def analyze_bug_report(bug_description: str) -> dict:
    """
    Analysis Layer: Use Gemini to deeply understand the bug report
    and plan reproduction steps.
    
    Returns:
        dict with keys: thoughts, response
    """
    configure_client()
    
    model = genai.GenerativeModel(
        model_name=GEMINI_FLASH,
        system_instruction="""You are an expert QA engineer analyzing a bug report.
            
Your task:
1. Extract the URL or application to test
2. List 3-5 specific steps to reproduce the bug
3. Identify expected vs actual behavior
4. Suggest which browser(s) to test

Return JSON:
{
    "url": "string or null",
    "steps": ["step1", "step2", ...],
    "expected": "what should happen",
    "actual": "what actually happens",
    "browsers": ["chromium", "webkit"],
    "confidence": 0.0-1.0
}"""
    )
    
    response = model.generate_content(bug_description)
    
    return {"thoughts": [], "response": response.text}


def generate_playwright_script(analysis: dict) -> str:
    """
    Scripting Layer: Use Gemini Flash to generate a Playwright script
    that reproduces the bug based on the analysis.
    """
    configure_client()
    
    prompt = f"""Based on this bug analysis, generate a Playwright Python script:

URL: {analysis.get('url', 'unknown')}
Steps: {analysis.get('steps', [])}
Expected: {analysis.get('expected', '')}
Actual: {analysis.get('actual', '')}

IMPORTANT REQUIREMENTS:
1. Use headless=True when launching browsers (for server environment).
2. Use synchronous Playwright API (from playwright.sync_api import sync_playwright).
3. CAPTURE CONSOLE ERRORS - Add listeners for JavaScript errors:
   - Use page.on("console", handler) to capture console.log/warn/error
   - Use page.on("pageerror", handler) to capture uncaught exceptions
   - Log all errors with [CONSOLE] or [PAGE_ERROR] prefix
4. Take screenshots at key moments (save to /home/user/screenshot.png)
5. Log observations with print() statements

EXAMPLE CONSOLE CAPTURE:
```python
console_errors = []
def handle_console(msg):
    if msg.type in ['error', 'warning']:
        console_errors.append(f"[CONSOLE {{msg.type.upper()}}] {{msg.text}}")
        print(f"[CONSOLE {{msg.type.upper()}}] {{msg.text}}")

def handle_pageerror(err):
    console_errors.append(f"[PAGE_ERROR] {{err}}")
    print(f"[PAGE_ERROR] {{err}}")

page.on("console", handle_console)
page.on("pageerror", handle_pageerror)
```

Generate a complete, runnable script that:
1. Navigates to the URL
2. Sets up console error listeners BEFORE navigation
3. Performs each reproduction step
4. Logs what it observes including any console errors
5. At the end, prints a summary of all console errors found

Return ONLY the raw Python code without any markdown formatting or code blocks."""

    model = genai.GenerativeModel(model_name=GEMINI_FLASH)
    response = model.generate_content(prompt)
    
    # Clean the response
    code = response.text.strip()
    
    # Remove markdown code blocks
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    
    # Remove any control characters and non-printable chars
    import re
    code = re.sub(r'<ctrl\d+>', '', code)  # Remove <ctrl##> sequences
    code = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', code)  # Remove control chars
    
    return code.strip()


def analyze_screenshot(image_bytes: bytes, context: str) -> dict:
    """
    Vision Layer: Use Gemini Pro to analyze a screenshot
    and determine why a script step failed (Self-Healing).
    
    Returns:
        dict with keys: observation, suggested_fix, new_selector
    """
    configure_client()
    
    model = genai.GenerativeModel(
        model_name=GEMINI_VISION,
        system_instruction="""You are an expert at visual debugging.
            
Analyze the screenshot and return JSON:
{
    "observation": "what you see on the page",
    "problem": "why the test step might have failed",
    "suggested_fix": "how to fix the selector or action",
    "new_selector": "CSS or XPath selector that would work"
}"""
    )
    
    # Create image part for vision
    image_part = {
        "mime_type": "image/png",
        "data": image_bytes
    }
    
    response = model.generate_content([
        f"Context: {context}\n\nAnalyze this screenshot and help fix the failing test.",
        image_part
    ])
    
    return {"analysis": response.text}


def heal_script(original_script: str, error_log: str, vision_analysis: dict) -> str:
    """
    Self-Healing: Use Gemini to rewrite a broken Playwright script
    based on error messages and visual analysis.
    
    Args:
        original_script: The script that failed
        error_log: stderr output from the failed execution
        vision_analysis: Output from analyze_screenshot()
    
    Returns:
        A corrected Playwright script
    """
    configure_client()
    
    prompt = f"""You are a senior QA engineer fixing a broken Playwright test.

ORIGINAL SCRIPT:
```python
{original_script}
```

ERROR:
{error_log}

VISUAL ANALYSIS (from screenshot):
{vision_analysis.get('analysis', 'No visual analysis available')}

TASK:
1. Identify WHY the script failed (wrong selector, timing issue, element not visible, etc.)
2. Rewrite the script with the fix applied
3. Add better error handling and waits if needed

Return ONLY the corrected Python code without any markdown formatting or code blocks."""

    model = genai.GenerativeModel(model_name=GEMINI_FLASH)
    response = model.generate_content(prompt)
    
    # Strip markdown if present
    code = response.text.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    
    return code.strip()

