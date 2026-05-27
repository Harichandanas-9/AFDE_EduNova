"""
Guardrail / content-safety filter.

EduNova is restricted to: education, learning, quizzes, study planning,
resume building, skill analysis, interview prep, course recommendations,
and career growth.

This module performs:
  1) Rule-based denylist matching (politics, NSFW, hacking, medical, etc.)
  2) Allowlist topic detection (educational / career keywords)
  3) A "soft" classifier that yields an allow/block decision with reason
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

# --- Denied topic patterns (case-insensitive) ---
_DENY_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("politics", re.compile(r"\b(election|president|prime\s+minister|political\s+party|democrat|republican|vote\s+for|left[- ]wing|right[- ]wing)\b", re.I)),
    ("nsfw", re.compile(r"\b(porn|pornographic|nsfw|nude|sexual\s+content|erotic|xxx)\b", re.I)),
    ("violence", re.compile(r"\b(how\s+to\s+(kill|murder|hurt|harm)|build\s+(a\s+)?bomb|make\s+(a\s+)?weapon|shoot\s+up)\b", re.I)),
    ("hacking", re.compile(r"\b(hack\s+(into|someone'?s)|crack\s+password|ddos|exploit\s+vulnerability|write\s+malware|create\s+virus|ransomware|phishing\s+kit)\b", re.I)),
    ("drugs", re.compile(r"\b(how\s+to\s+(make|cook|synthesize)\s+(meth|cocaine|heroin|lsd|fentanyl))\b", re.I)),
    ("medical", re.compile(r"\b(diagnose\s+me|what\s+(disease|illness)\s+do\s+i\s+have|prescribe|treatment\s+for\s+my)\b", re.I)),
    ("legal", re.compile(r"\b(legal\s+advice|sue\s+(my|someone)|lawsuit\s+against)\b", re.I)),
    ("self_harm", re.compile(r"\b(suicide\s+method|how\s+to\s+(harm|hurt)\s+myself|kill\s+myself)\b", re.I)),
    ("financial_advice", re.compile(r"\b(invest\s+my\s+money|stock\s+pick|buy\s+(crypto|bitcoin)\s+now|financial\s+advice\s+for\s+me)\b", re.I)),
]

# --- Allowed topic indicators ---
_ALLOW_KEYWORDS = {
    # education / learning
    "learn", "study", "studying", "course", "tutorial", "lesson", "lecture",
    "textbook", "concept", "topic", "subject", "explain", "what is", "how does",
    "definition", "example", "exercise", "practice", "homework", "assignment",
    "education", "educational", "school", "college", "university", "degree",
    # quizzes / tests
    "quiz", "test", "exam", "mcq", "question", "answer", "score",
    "assessment", "evaluation", "grade", "mock",
    # programming / tech
    "python", "javascript", "java", "react", "node", "fastapi", "sql", "html",
    "css", "algorithm", "data structure", "code", "coding", "programming",
    "function", "class", "variable", "loop", "framework", "library", "api",
    "git", "docker", "kubernetes", "aws", "azure", "linux", "database",
    "machine learning", "ai", "ml", "deep learning", "neural network", "llm",
    "frontend", "backend", "full stack", "devops", "cloud", "data science",
    "statistics", "math", "physics", "chemistry", "biology", "engineering",
    # career / resume / interview
    "resume", "cv", "cover letter", "interview", "job", "career", "role",
    "position", "salary", "hr", "recruiter", "hiring", "internship",
    "skill", "skills", "portfolio", "linkedin", "github",
    # study planning
    "plan", "roadmap", "schedule", "timetable", "goal", "milestone",
    "track", "progress", "streak", "habit",
    # recommendations
    "recommend", "suggestion", "resource", "youtube", "udemy", "coursera",
    "certification", "documentation",
}


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str = ""
    category: str = ""
    confidence: float = 1.0

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "category": self.category,
            "confidence": self.confidence,
        }


BLOCKED_RESPONSE = (
    "I'm designed specifically for educational and career-related assistance. "
    "I can help with learning, quizzes, study plans, resumes, interview prep, "
    "skill analysis, and course recommendations. Please ask me something in those areas."
)


def check_content(text: str) -> GuardrailResult:
    """
    Returns a GuardrailResult indicating whether the input should be allowed.

    The decision is conservative: a clear denylist hit blocks the request.
    If no denylist matches, we look for any educational/career signal in the
    text; if neither denylist nor allowlist matches, we still allow but flag
    low confidence (the LLM's system prompt provides the second layer).
    """
    if not text or not text.strip():
        return GuardrailResult(allowed=False, reason="Empty input.", category="empty", confidence=1.0)

    lowered = text.lower()

    # 1) Denylist check
    for category, pattern in _DENY_PATTERNS:
        if pattern.search(lowered):
            return GuardrailResult(
                allowed=False,
                reason=f"Request matches restricted category: {category}.",
                category=category,
                confidence=0.95,
            )

    # 2) Allowlist check
    if any(kw in lowered for kw in _ALLOW_KEYWORDS):
        return GuardrailResult(allowed=True, reason="Educational/career intent detected.", category="education", confidence=0.9)

    # 3) Heuristic: short greetings are fine
    greetings = {"hi", "hello", "hey", "yo", "good morning", "good evening", "thanks", "thank you"}
    if lowered.strip().strip(".!?,") in greetings:
        return GuardrailResult(allowed=True, reason="Greeting.", category="greeting", confidence=1.0)

    # 4) Default: permit but with low confidence; agents add a second layer.
    return GuardrailResult(allowed=True, reason="No restricted content detected.", category="general", confidence=0.5)


def sanitize_output(text: str) -> str:
    """Strip obvious leaked instructions / sensitive tokens from model output."""
    if not text:
        return text
    text = re.sub(r"(?i)\bapi[_\- ]?key\s*=\s*[A-Za-z0-9_\-]+", "[REDACTED]", text)
    text = re.sub(r"(?i)\bbearer\s+[A-Za-z0-9_\-\.]+", "[REDACTED]", text)
    return text.strip()
