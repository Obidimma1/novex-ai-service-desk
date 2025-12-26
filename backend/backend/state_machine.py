SESSIONS = {}

def handle_message(session_id: str, message: str):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "state": "START",
            "confidence": 90,
            "attempts": 0
        }

    session = SESSIONS[session_id]
    state = session["state"]
    msg = message.lower()

    if state == "START":
        session["state"] = "ASK_ISSUE"
        return {
            "reply": "Hi, I’m Novex. Is this about (1) password access, (2) Microsoft Teams, or (3) Outlook?",
            "state": "ASK_ISSUE"
        }

    if state == "ASK_ISSUE":
        if msg == "1" or "password" in msg:
            session["state"] = "PASSWORD_FLOW"
            return {
                "reply": "Got it. Are you locked out or did you forget your password?",
                "state": "PASSWORD_FLOW"
            }

        if msg == "2" or "teams" in msg:
            session["state"] = "TEAMS_FLOW"
            return {
                "reply": "Understood. Are you using Teams on the desktop app or in a browser?",
                "state": "TEAMS_FLOW"
            }

        if msg == "3" or "outlook" in msg:
            session["state"] = "OUTLOOK_FLOW"
            return {
                "reply": "Okay. Is Outlook not opening, not sending, or not receiving emails?",
                "state": "OUTLOOK_FLOW"
            }

        return {
            "reply": "Please reply with 1, 2, or 3 so I can route this correctly.",
            "state": state
        }

    return {
        "reply": "This requires second-line support. I’m escalating this with full context.",
        "state": "ESCALATED"
    }
