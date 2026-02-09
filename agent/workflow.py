"""
Agent Workflow - The Self-Healing Loop
Orchestrates: Analysis -> Scripting -> Execution -> Vision Fix -> Export
"""

from agent import brain, sandbox


class ReproductionWorkflow:
    """
    The main agent loop that attempts to reproduce a bug.
    
    Workflow:
    1. ANALYZE: Use Gemini Pro to understand the bug report
    2. SCRIPT: Use Gemini Flash to generate Playwright code
    3. EXECUTE: Run script in E2B sandbox
    4. FIX (if needed): Use Vision to analyze failures and self-heal
    5. EXPORT: Generate Dockerfile that reproduces the bug
    """
    
    def __init__(self, session_id: str, bug_report: str):
        self.session_id = session_id
        self.bug_report = bug_report
        self.sandbox_mgr = sandbox.SandboxManager()
        self.max_fix_attempts = 3
        
        # State
        self.analysis: dict = {}
        self.script: str = ""
        self.logs: list[str] = []
        self.thoughts: list[str] = []
        self.screenshots: list[bytes] = []
    
    def log(self, message: str):
        """Add to session logs."""
        self.logs.append(f"[{self.session_id}] {message}")
        print(f"[{self.session_id}] {message}")
    
    def run(self) -> dict:
        """Execute the full reproduction workflow."""
        try:
            # Step 1: Analyze
            self.log("🧠 ANALYSIS: Starting deep analysis...")
            self.analysis = brain.analyze_bug_report(self.bug_report)
            self.thoughts.extend(self.analysis.get("thoughts", []))
            self.log(f"Analysis complete. Found {len(self.analysis.get('steps', []))} steps.")
            
            # Step 2: Generate Script
            self.log("📝 SCRIPTING: Generating Playwright script...")
            self.script = brain.generate_playwright_script(self.analysis)
            self.log(f"Generated script ({len(self.script)} chars)")
            
            # Step 3: Create Sandbox & Execute
            self.log("🚀 EXECUTION: Spawning E2B sandbox...")
            self.sandbox_mgr.create()
            self.log(f"Sandbox ready: {self.sandbox_mgr.sandbox_id}")
            
            result = self.sandbox_mgr.run_script(self.script)
            
            # Step 4: Check & Self-Heal
            fix_attempts = 0
            while result["exit_code"] != 0 and fix_attempts < self.max_fix_attempts:
                fix_attempts += 1
                self.log(f"⚠️ SELF-HEALING: Attempt {fix_attempts}/{self.max_fix_attempts}")
                self.thoughts.append(f"Script failed. Starting self-healing attempt {fix_attempts}...")
                
                # Capture screenshot of failure state
                screenshot = self.sandbox_mgr.take_screenshot()
                vision_analysis = {}
                
                if screenshot:
                    self.screenshots.append(screenshot)
                    self.log("📸 Captured failure screenshot")
                    
                    # Vision analysis: Ask AI what went wrong
                    self.log("👁️ Analyzing screenshot with Vision AI...")
                    vision_analysis = brain.analyze_screenshot(
                        screenshot, 
                        f"Script failed with error: {result['stderr'][:500]}"
                    )
                    self.thoughts.append(f"Vision Analysis: {vision_analysis.get('analysis', 'N/A')[:200]}")
                    self.log(f"Vision insight: {vision_analysis.get('analysis', 'N/A')[:100]}...")
                
                # Heal: Use AI to fix the script
                self.log("🔧 Generating fixed script...")
                self.script = brain.heal_script(
                    original_script=self.script,
                    error_log=result["stderr"],
                    vision_analysis=vision_analysis
                )
                self.thoughts.append(f"Generated healed script (attempt {fix_attempts})")
                self.log(f"Fixed script generated ({len(self.script)} chars)")
                
                # Retry with the healed script
                self.log("🔄 Re-running with fixed script...")
                result = self.sandbox_mgr.run_script(self.script)
                
                if result["exit_code"] == 0:
                    self.log("✅ Self-healing successful!")
                    self.thoughts.append("Self-healing succeeded on attempt " + str(fix_attempts))
                else:
                    self.log(f"❌ Fix attempt {fix_attempts} failed: {result['stderr'][:100]}...")
            
            # Step 5: Generate Dockerfile
            self.log("📦 EXPORT: Generating Dockerfile...")
            dockerfile = self._generate_dockerfile()
            
            self.sandbox_mgr.destroy()
            
            return {
                "status": "completed" if result["exit_code"] == 0 else "failed",
                "thoughts": self.thoughts,
                "logs": self.logs,
                "dockerfile": dockerfile,
                "fix_attempts": fix_attempts
            }
            
        except Exception as e:
            self.log(f"❌ ERROR: {str(e)}")
            self.sandbox_mgr.destroy()
            return {
                "status": "error",
                "error": str(e),
                "logs": self.logs
            }
    
    def _generate_dockerfile(self) -> str:
        """Generate a Dockerfile that reproduces the bug."""
        return f'''# Auto-generated by Self-Healing-Sandbox
# Session: {self.session_id}
# Bug: {self.bug_report[:100]}...

FROM python:3.11-slim

# Install dependencies
RUN pip install playwright && playwright install chromium --with-deps

WORKDIR /app

# Copy the reproduction script
COPY reproduce.py .

CMD ["python", "reproduce.py"]
'''
