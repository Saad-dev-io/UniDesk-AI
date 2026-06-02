"""
UniDesk AI — Knowledge Base
=============================
Curated step-by-step solutions for common university IT issues.
When the AI triage engine classifies an issue as self-resolvable,
it references a topic key that maps to a solution guide here.

This separation of concerns means:
  - AI handles natural language understanding & classification
  - Knowledge Base provides accurate, vetted solutions
  - Solutions can be updated without changing the AI prompt
"""


SOLUTIONS = {
    "wifi_troubleshoot": {
        "title": "📶 WiFi Troubleshooting Guide",
        "category": "network",
        "steps": [
            "**Step 1:** Make sure WiFi is turned **ON** on your device (check Settings → WiFi)",
            "**Step 2:** Look for the network **'UniNet-Student'** — avoid 'UniNet-Guest' as it has limited access and slower speeds",
            "**Step 3:** If you see the network but can't connect, tap **'Forget Network'** then reconnect fresh",
            "**Step 4:** When prompted for credentials, enter your **university email** as the username and your **portal password**",
            "**Step 5:** If asked about a security certificate, tap **'Trust'** or **'Accept'**",
            "**Step 6:** Open any browser — you may need to complete a **captive portal login** page",
            "**Step 7:** Still stuck? **Restart your device** completely and repeat from Step 2",
            "**Step 8:** If multiple devices fail in the same location, the access point may be down — try a **different area** of the building",
        ],
        "tips": (
            "💡 **Pro tips:**\n"
            "• WiFi access points are usually along **corridors** — move closer if you're in a corner room\n"
            "• **5GHz networks** are faster but have shorter range; **2.4GHz** reaches further\n"
            "• If your laptop connects but phone doesn't (or vice versa), the issue is device-specific"
        ),
    },
    "password_reset": {
        "title": "🔑 Password Reset Guide",
        "category": "account",
        "steps": [
            "**Step 1:** Open your browser and go to **portal.university.edu/reset**",
            "**Step 2:** Click **'Forgot Password'** on the login page",
            "**Step 3:** Enter your **Student/Faculty ID** or university email address",
            "**Step 4:** Check your **personal email** (the one you registered during admission) for the reset link",
            "**Step 5:** Click the link and create a new password with these requirements:\n"
            "   • Minimum **8 characters**\n"
            "   • At least **1 uppercase** letter\n"
            "   • At least **1 number**\n"
            "   • At least **1 special character** (!@#$%^&*)",
            "**Step 6:** Wait **5 minutes** for the password to sync across all university systems (portal, email, LMS, WiFi)",
            "**Step 7:** Try logging in with your new password",
        ],
        "tips": (
            "💡 **Important:**\n"
            "• If you don't have access to your registered personal email, visit the **IT Service Desk in person** with your student ID card\n"
            "• Passwords expire every **90 days** — set a calendar reminder!\n"
            "• Never reuse passwords from other services"
        ),
    },
    "vpn_setup": {
        "title": "🔒 VPN Setup Guide",
        "category": "network",
        "steps": [
            "**Step 1:** Download the university VPN client from **portal.university.edu/vpn**",
            "**Step 2:** Install the application (requires admin privileges on your device)",
            "**Step 3:** Open the VPN client and enter the server address: **vpn.university.edu**",
            "**Step 4:** Select **'University VPN'** from the connection profile dropdown",
            "**Step 5:** Enter your **university email** and **portal password**",
            "**Step 6:** If prompted for 2FA, approve the notification on your authenticator app",
            "**Step 7:** Wait for the connection indicator to turn **green** — you're connected!",
        ],
        "tips": (
            "💡 **When do you need VPN?**\n"
            "• Accessing **library databases** from off-campus\n"
            "• Using **research servers** or **lab machines** remotely\n"
            "• Connecting to **internal university resources**\n"
            "• VPN is NOT needed when you're on campus WiFi"
        ),
    },
    "email_setup": {
        "title": "📧 Email Setup Guide",
        "category": "email",
        "steps": [
            "**Step 1:** Your university email is: **yourID@university.edu**",
            "**Step 2:** For **webmail**, go to **mail.university.edu** and sign in with your university credentials",
            "**Step 3:** For **phone setup** (iPhone/Android):\n"
            "   • Go to Settings → Mail → Add Account → **Microsoft 365** (or Google Workspace)\n"
            "   • Enter your university email address\n"
            "   • You'll be redirected to the university login page\n"
            "   • Sign in with your portal password",
            "**Step 4:** For **Outlook desktop**, click File → Add Account → enter your university email → follow prompts",
            "**Step 5:** Email should sync within **5-10 minutes** after setup",
        ],
        "tips": (
            "💡 **Good to know:**\n"
            "• Calendar and contacts sync automatically with email setup\n"
            "• University email has **50GB** storage — no need to delete everything!\n"
            "• Check your **Junk/Spam** folder if you're missing expected emails"
        ),
    },
    "printer_setup": {
        "title": "🖨️ Printer Setup Guide",
        "category": "hardware",
        "steps": [
            "**Step 1:** Make sure you're connected to **UniNet-Student** WiFi (printers are on the campus network)",
            "**Step 2:** Go to **print.university.edu** in your browser",
            "**Step 3:** Log in with your university credentials",
            "**Step 4:** Upload your document (PDF works best) and select your settings (color, double-sided, etc.)",
            "**Step 5:** Choose the **printer nearest to you** from the dropdown list",
            "**Step 6:** Click **Print** — your job is queued and waiting",
            "**Step 7:** Go to the physical printer, **tap your student ID card** on the reader to release your print job",
        ],
        "tips": (
            "💡 **Printing tips:**\n"
            "• Each student gets **500 free pages** per semester\n"
            "• Check your balance at **print.university.edu/balance**\n"
            "• Color prints count as **3 pages** from your quota\n"
            "• Print jobs expire after **24 hours** if not released"
        ),
    },
    "software_install": {
        "title": "💻 Software Installation Guide",
        "category": "software",
        "steps": [
            "**Step 1:** Check the **University Software Portal** at **software.university.edu**",
            "**Step 2:** Log in with your university credentials",
            "**Step 3:** Browse or search for the software you need (e.g., MATLAB, AutoCAD, MS Office, SPSS)",
            "**Step 4:** Click **Download** — many titles are free for students under university licenses",
            "**Step 5:** Follow the installation wizard on your device",
            "**Step 6:** When prompted for a **license key**, use your university email to activate",
            "**Step 7:** If the software isn't in the portal, submit a **software request** through the IT Service Desk",
        ],
        "tips": (
            "💡 **Free software for students:**\n"
            "• **Microsoft Office 365** — free with university email\n"
            "• **GitHub Student Pack** — free Pro account + tools\n"
            "• **JetBrains IDEs** — free with .edu email\n"
            "• **Adobe Creative Cloud** — check if your department has licenses"
        ),
    },
    "lms_access": {
        "title": "📚 LMS Access Troubleshooting",
        "category": "lms",
        "steps": [
            "**Step 1:** Go to **lms.university.edu** (bookmark this!)",
            "**Step 2:** Click **'Login with University Account'** (don't create a separate account)",
            "**Step 3:** Enter your **university email** and **portal password**",
            "**Step 4:** If you can log in but **don't see your courses**:\n"
            "   • Wait 24-48 hours after registration — courses sync automatically\n"
            "   • Check with your instructor if the course is published\n"
            "   • Make sure you're enrolled in the correct section",
            "**Step 5:** If you get an **'Access Denied'** error, clear your browser cookies and try in an **incognito/private window**",
            "**Step 6:** Try a different browser (Chrome usually works best)",
        ],
        "tips": (
            "💡 **LMS tips:**\n"
            "• Download the **LMS mobile app** for notifications on assignments and grades\n"
            "• If a course disappears mid-semester, contact your **instructor first** — they may have unpublished it\n"
            "• Always check the LMS for announcements before emailing your professor"
        ),
    },
    "performance_tips": {
        "title": "⚡ Slow Computer Performance Tips",
        "category": "software",
        "steps": [
            "**Step 1:** **Restart your computer** — seriously, this fixes more than you'd think",
            "**Step 2:** Check what's using resources: press **Ctrl+Shift+Esc** (Windows) or **Cmd+Space → Activity Monitor** (Mac)",
            "**Step 3:** Close any **unnecessary browser tabs** — each tab uses RAM. Close tabs you're not actively using",
            "**Step 4:** Check for **pending updates** — outdated OS/drivers can cause slowdowns:\n"
            "   • Windows: Settings → Update & Security → Check for updates\n"
            "   • Mac: System Settings → Software Update",
            "**Step 5:** Clear **temporary files**:\n"
            "   • Windows: Search → 'Disk Cleanup' → Clean system files\n"
            "   • Mac: Finder → Go → Go to Folder → ~/Library/Caches → delete contents",
            "**Step 6:** Check your **storage** — if your disk is >90% full, performance drops significantly. Delete old downloads and empty the trash",
            "**Step 7:** Run a **malware scan** with your antivirus software (Windows Defender is fine for most cases)",
        ],
        "tips": (
            "💡 **Long-term performance:**\n"
            "• Keep at least **20% of disk space free** at all times\n"
            "• **Uninstall software** you don't use anymore\n"
            "• Consider adding **RAM** if your laptop supports it (most impactful upgrade)\n"
            "• If your computer is 5+ years old and still slow after these steps, it may be time for a hardware consultation"
        ),
    },
}


def get_solution(topic_key: str) -> dict | None:
    """Retrieve a solution guide by its topic key.

    Args:
        topic_key: The key identifying the solution (e.g., 'wifi_troubleshoot').

    Returns:
        The solution dict with title, steps, and tips — or None if not found.
    """
    return SOLUTIONS.get(topic_key)


def format_solution(topic_key: str) -> str | None:
    """Format a solution as a readable markdown string for chat display.

    Args:
        topic_key: The key identifying the solution.

    Returns:
        A formatted markdown string, or None if the topic isn't found.
    """
    solution = SOLUTIONS.get(topic_key)
    if not solution:
        return None

    parts = [f"### {solution['title']}"]
    for step in solution["steps"]:
        parts.append(step)
    if solution.get("tips"):
        parts.append(f"---\n\n{solution['tips']}")

    return "\n\n".join(parts)


def get_all_topics() -> list[dict]:
    """Return a summary list of all available solution topics."""
    return [
        {"key": key, "title": sol["title"], "category": sol["category"]}
        for key, sol in SOLUTIONS.items()
    ]
