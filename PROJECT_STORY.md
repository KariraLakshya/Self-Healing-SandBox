# 🤖 Self-Healing Sandbox

## Inspiration

Manual bug reproduction is the bane of every QA engineer's existence. Hours spent reading vague reports, setting up environments, and playing detective—only to hear "works on my machine." 

We envisioned a world where you paste a bug report and an AI agent *autonomously* reproduces it, heals itself when scripts break, and outputs a Dockerfile anyone can run. No more back-and-forth. No more "can't reproduce."

$$\text{Bug Report} \xrightarrow{\text{AI Agent}} \text{Reproducible Dockerfile}$$

---

## What it does

**Self-Healing Sandbox** is an autonomous QA agent that:

1. **Analyzes** bug reports using Gemini AI to extract reproduction steps
2. **Generates** Playwright scripts to automate browser testing
3. **Executes** scripts in isolated E2B cloud sandboxes
4. **Self-Heals** when tests fail—using Vision AI to analyze screenshots and fix selectors
5. **Captures** JavaScript console errors from target applications
6. **Persists** all sessions in Redis for reliable storage and real-time log streaming
7. **Exports** a Dockerfile that reliably reproduces the bug

Plus: Import bugs directly from **GitHub Issues** with one click!

---

## How we built it

| Layer | Technology |
|-------|------------|
| **Frontend** | React + Vite (modern dark theme dashboard) |
| **Backend** | FastAPI (Python async API) |
| **AI Brain** | Gemini 2.5 Flash (analysis + scripting) |
| **Vision** | Gemini Pro Vision (screenshot analysis) |
| **Sandbox** | E2B Desktop (isolated cloud VMs) |
| **Automation** | Playwright (browser testing) |
| **Storage** | Redis with in-memory fallback |

**Architecture Flow:**
```
User → React Dashboard → FastAPI → Gemini AI → E2B Sandbox → Dockerfile
                                      ↑
                              Vision AI (self-healing loop)
```

---

## Challenges we ran into

### E2B Sandbox Challenges

1. **Playwright Installation Failures**: The E2B Desktop sandbox runs as non-root user, causing `pip install playwright` to fail with permission errors. We had to implement a fallback chain:
   ```python
   # Try user install first, then sudo
   result = sandbox.commands.run("pip install --user playwright")
   if result.exit_code != 0:
       sandbox.commands.run("sudo pip install playwright")
   ```

2. **Browser Binary Downloads**: Even after pip install, Playwright needs browser binaries. The `playwright install chromium` command times out on slow sandbox startup. We increased timeout to 120 seconds and added retry logic.

3. **Screenshot Capture Timing**: E2B's `sandbox.screenshot()` API sometimes returns blank images if called too quickly after page load. Had to add `page.wait_for_load_state("networkidle")` before captures.

4. **Sandbox Cold Start Latency**: First sandbox creation takes 15-20 seconds. Subsequent ones are faster, but this adds significant delay to the user experience.

### Gemini API Challenges

1. **Inconsistent Output Formatting**: Gemini sometimes wraps code in markdown blocks, sometimes doesn't. Same prompt, different runs = different formats. Required robust stripping logic for ```python``` blocks.

2. **Hallucinated Selectors**: Gemini confidently generates CSS selectors like `#login-button` for pages it's never seen. The selectors often don't exist, triggering our self-healing loop.

3. **Token Limits on Long Pages**: When feeding large DOM structures for vision analysis, we hit context limits. Had to truncate error logs to 500 chars: `result['stderr'][:500]`

4. **Vision API Latency**: Screenshot analysis with Gemini Vision takes 3-5 seconds per image, making the self-healing loop slower than expected.

5. **Rate Limiting**: During rapid testing, we hit Gemini's rate limits. Added exponential backoff but it slows down batch operations.

---

## Accomplishments that we're proud of

- ✅ **True Self-Healing**: The agent actually fixes its own broken scripts using vision analysis
- ✅ **Console Error Detection**: Captures JavaScript errors invisible to users
- ✅ **One-Click GitHub Import**: Paste issue URL → auto-extract description + target URL
- ✅ **Beautiful Dashboard**: Modern dark theme with real-time log streaming
- ✅ **Production-Ready Artifacts**: Outputs Dockerfiles anyone can run

---

## What we learned

1. **LLMs need guardrails**: Raw model output is messy—always post-process
2. **Vision completes the loop**: Error logs alone aren't enough; the AI needs to *see* the page
3. **Sandboxing is essential**: Never run AI-generated code on your own machine
4. **Self-healing > one-shot**: Retry loops with feedback dramatically improve success rates

---

## What's next for Self-Healing Sandbox

- 🎥 **Video Recording**: Capture bug reproductions as video evidence
- 🌐 **Multi-Browser**: Parallel testing on Chrome, Firefox, Safari
- 🔗 **CI/CD Integration**: GitHub Actions plugin for automatic regression detection
- 🤖 **Auto-Fix PRs**: Not just reproduce bugs—generate fix suggestions
- 📊 **Analytics Dashboard**: Track reproduction success rates over time

---

*Built with Gemini AI, FastAPI, React, E2B, and Playwright* ❤️
