"""
Agent Sandbox - E2B Integration
Manages secure cloud browser sandboxes for test execution.
Uses E2B Desktop template which has browsers pre-installed.
"""

import os
from e2b_desktop import Sandbox as DesktopSandbox


class SandboxManager:
    """Manages E2B sandbox lifecycle and Playwright execution."""
    
    def __init__(self):
        self.sandbox: DesktopSandbox | None = None
        self.sandbox_id: str | None = None
    
    def create(self) -> str:
        """Spawn a new E2B Desktop sandbox with browser pre-installed."""
        api_key = os.environ.get("E2B_API_KEY")
        if not api_key:
            raise ValueError("E2B_API_KEY environment variable required")
        
        # Use Desktop sandbox which has browsers pre-installed
        # E2B reads API key from E2B_API_KEY environment variable
        self.sandbox = DesktopSandbox.create()
        self.sandbox_id = self.sandbox.sandbox_id
        
        # Install Playwright Python package with --user flag to avoid permission issues
        result = self.sandbox.commands.run(
            "pip install --user playwright",
            timeout=60
        )
        
        # Check if installation succeeded
        if result.exit_code != 0:
            # Try alternative: use sudo
            self.sandbox.commands.run(
                "sudo pip install playwright",
                timeout=60
            )
        
        # Download Chromium browser binary
        self.sandbox.commands.run(
            "python3 -m playwright install chromium",
            timeout=120
        )
        
        return self.sandbox_id
    
    def run_script(self, script: str) -> dict:
        """
        Execute a Playwright script in the sandbox.
        
        Returns:
            dict with keys: stdout, stderr, exit_code
        """
        if not self.sandbox:
            raise RuntimeError("Sandbox not created. Call create() first.")
        
        # Write script to sandbox
        script_path = "/home/user/test_script.py"
        self.sandbox.files.write(script_path, script)
        
        # Execute with longer timeout for browser operations
        result = self.sandbox.commands.run(f"python3 {script_path}", timeout=180)
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code
        }
    
    def take_screenshot(self) -> bytes:
        """Capture current desktop state."""
        if not self.sandbox:
            raise RuntimeError("Sandbox not created")
        
        try:
            # E2B Desktop can take screenshots directly
            return self.sandbox.screenshot()
        except Exception:
            # Fallback to Playwright-saved screenshot
            try:
                screenshot_data = self.sandbox.files.read("/home/user/screenshot.png")
                return screenshot_data
            except Exception:
                return b""
    
    def get_logs(self) -> list[str]:
        """Retrieve execution logs from sandbox."""
        if not self.sandbox:
            return []
        
        try:
            result = self.sandbox.commands.run("cat /home/user/test.log", timeout=10)
            return result.stdout.split("\n")
        except Exception:
            return []
    
    def destroy(self):
        """Terminate the sandbox."""
        if self.sandbox:
            try:
                self.sandbox.kill()
            except Exception:
                pass
            self.sandbox = None
            self.sandbox_id = None
