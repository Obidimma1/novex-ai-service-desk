# Architecture (MVP)

## Overview
Novex is an AI-powered Tier-1 Service Desk Engineer focused on Microsoft 365. Unlike typical “chatbot” support tools, Novex uses deterministic state machines to control troubleshooting flow, enforce safety boundaries, and generate consistent L2 escalation packages.

## Why state machines (not free-form chat)
Most AI support bots rely heavily on open-ended prompting, which can lead to inconsistent troubleshooting, repeated steps, and risky recommendations. Novex uses deterministic state machines so that:
- the troubleshooting path is explicit and auditable
- sensitive actions require explicit user consent
- escalation is triggered by confidence thresholds and attempt/time limits
- L2 receives structured handover notes (issue summary, checks performed, actions taken)

## MVP scope
- Password and account access issues
- Microsoft Teams client issues
- Microsoft Outlook client issues
- Ticket creation and escalation to second line

## System components
- **API layer (FastAPI)**: exposes `/chat` endpoint for chat clients
- **State machine engine**: holds session context and advances the user through troubleshooting states
- **Knowledge base + runbooks**: defines approved fixes and escalation triggers (no guessing)
- **Tool layer (future in MVP)**: controlled integrations with Microsoft Graph (password reset, session revoke, service health, license checks)
- **Audit logging (future in MVP)**: records actions and decisions for compliance and incident review

## Safety and governance (MVP principles)
- least privilege by default
- no unsafe actions (no registry edits, no MFA bypass)
- explicit consent gates for sensitive operations
- confidence-based escalation to protect user experience and reduce L2 rework
