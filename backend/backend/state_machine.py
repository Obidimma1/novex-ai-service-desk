import json
import os
from typing import Dict, Any

# In-memory session store (MVP). We’ll replace with SQLite next.
SESSIONS: Dict[str, Dict[str, Any]] = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MACHINES_DIR = os.path.join(os.path.dirname(BASE_DIR), "machines")

ROUTE_KEYWORDS = {
    "passwords": ["password", "login", "sign in", "signin", "locked", "lockout", "mfa"],
    "teams": ["teams", "channel", "chat", "meeting", "call", "teams app"],
    "outlook": ["outlook", "email", "mail", "inbox", "send", "receive"]
}

def _load_machine(machine_name: str) -> Dict[str, Any]:
    path = os.path.join(MACHINES_DIR, f"{machine_name}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _route_issue(user_message: str) -> str:
    msg = user_message.lower().strip()
    # direct numeric routing
    if msg == "1":
        return "passwords"
    if msg == "2":
        return "teams"
    if msg == "3":
        return "outlook"

    # keyword routing
    for machine, keywords in ROUTE_KEYWORDS.items():
        if any(k in msg for k in keywords):
            return machine

    return "passwords"  # safe default

def _match_any(user_message: str, patterns) -> bool:
    msg = user_message.lower().strip()
    for p in patterns:
        if p.lower() in msg:
            return True
    return False

def _step_machine(machine: Dict[str, Any], state: str, user_message: str) -> Dict[str, Any]:
    states = machine["states"]
    if state not in states:
        # Fail-safe: escalate if state is missing
        return {"reply": "I’m escalating this to second line with full context.", "state": "END"}

    node = states[state]
    node_type = node.get("type")

    # Terminal state
    if node_type == "terminal":
        return {"reply": "Session ended.", "state": "END"}

    # Message state: return message + move to next
    if node_type == "message":
        next_state = node.get("next", "END")
        return {"reply": node.get("message", ""), "state": next_state}

    # Decision state: evaluate routes based on user message
    if node_type == "decision":
        routes = node.get("routes", [])
        for r in routes:
            if _match_any(user_message, r.get("match_any", [])):
                return {"reply": None, "state": r.get("next", "END")}
        return {"reply": None, "state": node.get("default_next", "END")}

    # Unknown type -> safe escalate
    return {"reply": "I’m escalating this to second line with full context.", "state": "END"}

def handle_message(session_id: str, message: str):
    """
    Deterministic engine:
    - If new session: ask which issue category (1/2/3)
    - If session has selected machine: run that machine step-by-step
    """
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "stage": "ROUTING",
            "machine_name": None,
            "state": None
        }

    session = SESSIONS[session_id]

    # Stage 1: routing
    if session["stage"] == "ROUTING":
        # First interaction: prompt user
        if session["state"] is None:
            session["state"] = "ASK_ROUTE"
            return {
                "reply": "Hi, I’m Novex. Is this about (1) password access, (2) Microsoft Teams, or (3) Outlook? Reply 1/2/3.",
                "state": "ASK_ROUTE"
            }

        # Second interaction: choose machine based on answer
        chosen = _route_issue(message)
        session["machine_name"] = chosen
        machine = _load_machine(chosen)
        session["stage"] = "IN_MACHINE"
        session["state"] = machine.get("entry_state", "START")

        # Immediately return first machine message
        step = _step_machine(machine, session["state"], user_message="")
        session["state"] = step["state"]
        return {"reply": step["reply"], "state": session["state"]}

    # Stage 2: inside machine
    machine = _load_machine(session["machine_name"])
    current_state = session["state"]

    # Run decision nodes until we hit a message/terminal node
    while True:
        step = _step_machine(machine, current_state, message)
        current_state = step["state"]

        # If decision returned no reply, keep stepping until message/terminal
        if step["reply"] is None:
            continue

                session["state"] = current_state
        return {"reply": step["reply"], "state": current_state}
