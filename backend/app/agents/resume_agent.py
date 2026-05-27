"""Resume builder agent."""
from __future__ import annotations

import json

from app.agents.prompts import RESUME_SYSTEM
from app.agents.state import AgentState
from app.services.llm_service import llm_service
from app.utils.logger import get_logger

logger = get_logger("edunova.agent.resume")


def _render_markdown(payload: dict, request: dict) -> str:
    name = request.get("full_name", "Your Name")
    role = request.get("target_role", "Target Role")
    summary = payload.get("summary", "")
    skills = request.get("skills", [])
    experience = request.get("experience", [])
    education = request.get("education", [])
    projects = request.get("projects", [])
    bullets = payload.get("rewritten_bullets", [])

    md = [f"# {name}", f"**Target Role:** {role}", ""]
    if request.get("email") or request.get("phone"):
        contact = " | ".join([s for s in [request.get("email"), request.get("phone")] if s])
        md.append(contact)
        md.append("")
    if summary:
        md += ["## Professional Summary", summary, ""]
    if skills:
        md += ["## Skills", ", ".join(skills), ""]
    if experience:
        md.append("## Experience")
        for e in experience:
            md.append(f"### {e.get('role')} — {e.get('company')}")
            md.append(f"_{e.get('duration')}_")
            if e.get("description"):
                md.append(e["description"])
            for a in e.get("achievements", []):
                md.append(f"- {a}")
            md.append("")
    if bullets:
        md += ["## Highlighted Achievements"]
        md += [f"- {b}" for b in bullets]
        md.append("")
    if projects:
        md.append("## Projects")
        for p in projects:
            md.append(f"### {p.get('name')}")
            md.append(p.get("description", ""))
            if p.get("tech_stack"):
                md.append(f"_Tech:_ {', '.join(p['tech_stack'])}")
            if p.get("link"):
                md.append(f"[Link]({p['link']})")
            md.append("")
    if education:
        md.append("## Education")
        for ed in education:
            md.append(f"- **{ed.get('degree')}** — {ed.get('institution')} ({ed.get('duration')})")
        md.append("")
    return "\n".join(md).strip()


async def build_resume(payload: dict) -> dict:
    user_prompt = (
        f"Target role: {payload.get('target_role')}\nTemplate: {payload.get('template')}\n"
        f"Skills: {', '.join(payload.get('skills', []))}\n"
        f"Experience count: {len(payload.get('experience', []))}\n"
        f"Projects count: {len(payload.get('projects', []))}\n"
        "Rewrite achievements with strong action verbs and quantification."
    )
    raw = await llm_service.complete(RESUME_SYSTEM, user_prompt, json_mode=True, max_tokens=1500)
    try:
        data = json.loads(raw)
    except Exception as e:
        logger.warning("resume parse failed: %s", e)
        data = {
            "summary": "Motivated professional ready for impactful work.",
            "ats_score": 75.0,
            "suggestions": ["Add quantified metrics.", "Mirror the JD's keywords."],
            "rewritten_bullets": [],
        }
    data["markdown"] = _render_markdown(data, payload)
    return data


async def resume_node(state: AgentState) -> AgentState:
    if state.get("final"):
        return state
    text = state.get("user_input", "")
    raw = await llm_service.complete(RESUME_SYSTEM, text, json_mode=True, max_tokens=1500)
    try:
        data = json.loads(raw)
    except Exception:
        data = {"summary": "", "rewritten_bullets": [], "ats_score": 0, "suggestions": []}
    state["structured_payload"] = data
    state["response"] = data.get("summary") or "Drafted a resume outline."
    return state
