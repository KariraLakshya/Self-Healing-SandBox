"""
Self-Healing-Sandbox Backend - FastAPI Server
Provides REST API for the React dashboard to interact with the agent.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for agent imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

from agent.workflow import ReproductionWorkflow
from agent import brain
from backend.storage import store

app = FastAPI(
    title="Self-Healing Sandbox API",
    description="Autonomous QA Agent that reproduces bugs in secure sandboxes",
    version="1.0.0"
)

# CORS for React dashboard - allow local dev and Vercel deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",  # All Vercel preview/production deployments
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Regex for Vercel subdomains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import requests

def validate_url(url: str) -> bool:
    """Check if URL is valid and reachable."""
    if not url:
        return False
    if not (url.startswith("http://") or url.startswith("https://")):
        return False
    try:
        # Simple health check
        requests.head(url, timeout=5)
        return True
    except:
        return False


class BugReport(BaseModel):
    """Input schema for bug reports."""
    description: str
    url: str  # Mandatory now
    browser: str = "chromium"  # chromium, firefox, webkit


class Session(BaseModel):
    """Session state for an investigation."""
    id: str
    status: str  # analyzing, scripting, executing, fixing, completed, failed
    bug_report: BugReport
    thoughts: list[str] = []
    logs: list[str] = []
    screenshots: list[str] = []
    dockerfile: str | None = None


@app.get("/")
async def root():
    return {"status": "ok", "message": "Self-Healing Sandbox API", "storage": "Redis"}


@app.post("/analyze", response_model=Session)
async def analyze_bug(report: BugReport, background_tasks: BackgroundTasks):
    """
    Step 1: Analyze the bug report using Gemini.
    Returns a session ID to track progress.
    """
    if not validate_url(report.url):
         raise HTTPException(status_code=400, detail="Invalid or unreachable URL provided.")

    session_id = str(uuid.uuid4())[:8]
    session = Session(
        id=session_id,
        status="analyzing",
        bug_report=report,
        thoughts=[],
        logs=[f"[{session_id}] Received bug report: {report.description[:50]}..."]
    )
    
    # Save to Redis
    store.save(session_id, session.model_dump())
    
    # Trigger async analysis
    def run_analysis():
        try:
            result = brain.analyze_bug_report(report.description)
            thoughts = result.get("thoughts", [])
            for thought in thoughts:
                store.append_thought(session_id, thought)
            store.append_log(session_id, f"Analysis complete: {result.get('response', '')[:200]}")
            store.update(session_id, {"status": "analyzed"})
        except Exception as e:
            store.update(session_id, {"status": "error"})
            store.append_log(session_id, f"Analysis failed: {str(e)}")
    
    background_tasks.add_task(run_analysis)
    
    return session


@app.get("/status/{session_id}")
async def get_status(session_id: str):
    """Get current status of an investigation session."""
    session = store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.get("/sessions")
async def list_sessions():
    """List all active sessions."""
    return {"sessions": store.list_all()}


@app.get("/thoughts/{session_id}")
async def get_thoughts(session_id: str):
    """Get all thought signatures for a session (for pause/resume)."""
    thoughts = store.get_thoughts(session_id)
    return {"session_id": session_id, "thoughts": thoughts}


@app.post("/reproduce/{session_id}")
async def start_reproduction(session_id: str, background_tasks: BackgroundTasks):
    """
    Step 2: Start the reproduction loop.
    Uses Gemini Flash for scripting + E2B for execution.
    """
    session = store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    store.update(session_id, {"status": "scripting"})
    store.append_log(session_id, "Starting Playwright script generation...")
    
    def run_reproduction():
        try:
            # Reconstruct bug report properly from stored session
            description = session["bug_report"]["description"]
            url = session["bug_report"].get("url")
            full_report = f"{description}\nURL: {url}" if url else description

            workflow = ReproductionWorkflow(session_id, full_report)
            result = workflow.run()
            
            store.update(session_id, {
                "status": result.get("status", "unknown"),
                "dockerfile": result.get("dockerfile")
            })
            for log in result.get("logs", []):
                store.append_log(session_id, log)
            for thought in result.get("thoughts", []):
                store.append_thought(session_id, thought)
        except Exception as e:
            store.update(session_id, {"status": "error"})
            store.append_log(session_id, f"Reproduction failed: {str(e)}")
    
    background_tasks.add_task(run_reproduction)
    
    return {"status": "started", "session_id": session_id}


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session from Redis."""
    store.delete(session_id)
    return {"status": "deleted", "session_id": session_id}


@app.get("/analytics/history")
async def get_history():
    """Get all sessions history."""
    sessions = store.list_all()
    # Sort by timestamp (if available) or ID
    return {"history": sessions}


@app.get("/analytics/success-rate")
async def get_success_rate():
    """Calculate success/failure rates."""
    sessions = store.list_all()
    total = len(sessions)
    if total == 0:
        return {"total": 0, "success": 0, "failed": 0, "error": 0, "success_rate": 0}
    
    counts = {"success": 0, "failed": 0, "error": 0}
    for s in sessions:
        status = s.get("status", "unknown")
        if status == "completed":
            counts["success"] += 1
        elif status == "failed":
            counts["failed"] += 1
        elif status == "error":
            counts["error"] += 1
            
    return {
        "total": total,
        **counts,
        "success_rate": round((counts["success"] / total) * 100, 1)
    }


@app.get("/analytics/browsers")
async def get_browser_stats():
    """Get reproduction stats by browser."""
    sessions = store.list_all()
    stats = {}
    
    for s in sessions:
        browser = s.get("bug_report", {}).get("browser", "unknown")
        if browser not in stats:
            stats[browser] = {"total": 0, "success": 0}
        
        stats[browser]["total"] += 1
        if s.get("status") == "completed":
            stats[browser]["success"] += 1
            
    return {"browsers": stats}


@app.post("/github/fetch-issue")
async def fetch_github_issue(payload: dict):
    """
    Fetch issue details from GitHub and extract target URL.
    Input: { "url": "https://github.com/owner/repo/issues/123" }
    Output: { "title": "...", "body": "...", "url": "..." }
    """
    github_url = payload.get("url")
    if not github_url or "github.com" not in github_url:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")

    try:
        # Parse URL to get owner, repo, issue_number
        parts = github_url.rstrip("/").split("/")
        if "issues" not in parts:
             raise HTTPException(status_code=400, detail="Not a valid issue URL")
        
        issue_idx = parts.index("issues")
        owner = parts[issue_idx - 2]
        repo = parts[issue_idx - 1]
        number = parts[issue_idx + 1]

        # Fetch from GitHub API
        api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
        resp = requests.get(api_url)
        
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch issue from GitHub")
        
        data = resp.json()
        title = data.get("title", "")
        body = data.get("body", "")
        
        # Smart URL Extraction
        # Look for first http/https link that isn't github.com or an image
        import re
        urls = re.findall(r'(https?://[^\s\)]+)', body)
        target_url = None
        
        for u in urls:
            # clean trailing punctuation
            u = u.rstrip(".,;]")
            if "github.com" not in u and "user-images.githubusercontent.com" not in u:
                target_url = u
                break
        
        return {
            "title": title,
            "body": body,
            "url": target_url
        }

    except Exception as e:
        print(f"GitHub Fetch Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
