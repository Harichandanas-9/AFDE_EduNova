"""
LLM service layer.

Provides a single async interface to call OpenAI / Gemini, with a built-in
deterministic mock provider used when no API key is configured. This lets
the entire platform run end-to-end in local dev without external credentials.
"""
from __future__ import annotations

import asyncio
import json
import random
import re
from typing import Optional

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("edunova.llm")


class LLMService:
    """Unified async LLM interface."""

    def __init__(self):
        self.provider = (settings.LLM_PROVIDER or "mock").lower()
        if self.provider == "openai" and not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set - falling back to mock provider.")
            self.provider = "mock"
        if self.provider == "gemini" and not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set - falling back to mock provider.")
            self.provider = "mock"
        logger.info("LLM provider initialized: %s", self.provider)

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> str:
        """Return a completion for the given prompt."""
        temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        max_tokens = max_tokens or settings.LLM_MAX_TOKENS

        try:
            if self.provider == "openai":
                return await self._openai_complete(system_prompt, user_prompt, temperature, max_tokens, json_mode)
            if self.provider == "gemini":
                return await self._gemini_complete(system_prompt, user_prompt, temperature, max_tokens, json_mode)
        except Exception as e:
            logger.exception("LLM call failed (%s), falling back to mock: %s", self.provider, e)

        return self._mock_complete(system_prompt, user_prompt, json_mode)

    async def _openai_complete(self, system_prompt, user_prompt, temperature, max_tokens, json_mode):
        try:
            from openai import AsyncOpenAI
        except ImportError as e:
            raise RuntimeError("openai package not installed") from e
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        kwargs = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = await client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""

    async def _gemini_complete(self, system_prompt, user_prompt, temperature, max_tokens, json_mode):
        try:
            import google.generativeai as genai
        except ImportError as e:
            raise RuntimeError("google-generativeai not installed") from e
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            system_instruction=system_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "response_mime_type": "application/json" if json_mode else "text/plain",
            },
        )
        resp = await asyncio.to_thread(model.generate_content, user_prompt)
        return resp.text or ""

    def _mock_complete(self, system_prompt: str, user_prompt: str, json_mode: bool) -> str:
        """Deterministic offline-friendly mock LLM. Routes by agent marker."""
        sp = (system_prompt or "").lower()
        up = (user_prompt or "").strip()

        # Order matters: router check first because all other system prompts
        # contain the EDU_CONTRACT (which mentions "quizzes", "resumes", etc.).
        if "router agent" in sp:
            return self._mock_router(up)
        if "quiz agent" in sp:
            return self._mock_quiz(up)
        if "study planner" in sp:
            return self._mock_study_plan(up)
        if "resume builder" in sp:
            return self._mock_resume(up)
        if "skill gap" in sp:
            return self._mock_skill_gap(up)
        if "recommendation agent" in sp:
            return self._mock_recommendations(up)
        if "chat assistant" in sp:
            return self._mock_chat(up)

        lowered = up.lower()
        if "quiz" in lowered:
            return self._mock_quiz(up)
        if "study plan" in lowered or "roadmap" in lowered:
            return self._mock_study_plan(up)
        return self._mock_chat(up)

    def _mock_router(self, text: str) -> str:
        lowered = text.lower()
        mapping = [
            (("quiz", "mcq", "test me", "questions on"), "quiz"),
            (("study plan", "roadmap", "schedule", "learning plan"), "study_plan"),
            (("resume", "cv", "cover letter"), "resume"),
            (("skill gap", "missing skills", "skills for"), "skill_gap"),
            (("recommend", "course", "tutorial", "resources"), "recommendation"),
            (("interview", "behavioral", "system design"), "chat"),
        ]
        for keywords, intent in mapping:
            if any(k in lowered for k in keywords):
                return json.dumps({"intent": intent, "confidence": 0.85})
        return json.dumps({"intent": "chat", "confidence": 0.6})

    def _mock_chat(self, text: str) -> str:
        return (
            f"Here's a structured take on **{text[:80]}**:\n\n"
            "1. **Core idea** - Start with the fundamentals and build a strong mental model.\n"
            "2. **Practice** - Apply the concept on small problems before moving on.\n"
            "3. **Review** - Summarize what you learned in your own words.\n\n"
            "Would you like a quiz, study plan, or resource recommendations on this?"
        )

    def _mock_quiz(self, text: str) -> str:
        topic_match = re.search(r"topic[:\s]+([\w\s\-\+\.#]+?)(?:[,\.\n]|$)", text, re.I)
        topic = (topic_match.group(1).strip() if topic_match else "the requested topic")[:60]
        count_match = re.search(r"(\d+)\s+(?:question|q)s?", text, re.I)
        count = int(count_match.group(1)) if count_match else 5
        count = max(1, min(20, count))
        templates = [
            ("Which of the following best describes {t}?",
             ["A foundational concept", "An unrelated framework", "A deprecated library", "None of the above"],
             "A foundational concept",
             "Foundational, widely cited as a building block."),
            ("What is a common use case of {t}?",
             ["Image rendering", "Building real-world applications", "Soldering circuits", "Cooking"],
             "Building real-world applications",
             "Real-world applications are the most cited use case."),
            ("Which statement about {t} is TRUE?",
             ["It cannot be learned", "It requires practice", "It is only theoretical", "It is illegal"],
             "It requires practice",
             "Deliberate practice is the proven path to mastery."),
            ("Which tool is commonly associated with {t}?",
             ["MS Paint", "An industry-standard tool", "A spoon", "Nothing"],
             "An industry-standard tool",
             "Industry-standard tools dominate tutorials and docs."),
            ("Which is the BEST way to learn {t}?",
             ["Avoid practicing", "Only watch videos", "Combine theory + projects", "Memorize without context"],
             "Combine theory + projects",
             "Theory plus applied projects yields the deepest understanding."),
        ]
        questions = []
        for i in range(count):
            q_text, options, correct, explanation = templates[i % len(templates)]
            questions.append({
                "id": i + 1,
                "question": q_text.format(t=topic),
                "options": options,
                "correct_answer": correct,
                "explanation": explanation,
                "type": "mcq",
                "difficulty": "medium",
            })
        return json.dumps({"questions": questions})

    def _mock_study_plan(self, text: str) -> str:
        weeks_match = re.search(r"(\d+)\s*weeks?", text, re.I)
        weeks = int(weeks_match.group(1)) if weeks_match else 8
        weeks = max(1, min(weeks, 52))
        goal_match = re.search(r"goal[:\s]+([^\n,]+)", text, re.I)
        goal = goal_match.group(1).strip()[:80] if goal_match else "your learning goal"
        focus_pool = [
            "Foundations", "Core concepts", "Hands-on practice", "Real-world project",
            "Advanced topics", "System design", "Mock interviews", "Portfolio polish",
        ]
        schedule = []
        for w in range(1, weeks + 1):
            focus = focus_pool[(w - 1) % len(focus_pool)]
            schedule.append({
                "week": w,
                "title": f"Week {w}: {focus}",
                "focus_areas": [focus, "Daily practice"],
                "topics": [f"{focus} - module A", f"{focus} - module B"],
                "resources": ["Official documentation", "Curated playlist", "Practice problems"],
                "practice": ["Solve 5 problems", "Build 1 mini-feature"],
                "milestone": f"Complete a checkpoint for {focus.lower()}",
            })
        return json.dumps({
            "overview": f"A {weeks}-week roadmap toward {goal}.",
            "schedule": schedule,
            "milestones": [f"Week {w} milestone reached" for w in range(1, weeks + 1)],
        })

    def _mock_resume(self, text: str) -> str:
        return json.dumps({
            "summary": "Results-driven professional with hands-on experience delivering scalable solutions and measurable impact.",
            "ats_score": round(random.uniform(72.0, 92.0), 1),
            "suggestions": [
                "Quantify achievements with metrics (e.g., 'reduced load time by 35%').",
                "Mirror keywords from the target job description.",
                "Lead each bullet with a strong action verb.",
                "Keep formatting ATS-friendly (no tables/columns).",
            ],
            "rewritten_bullets": [
                "Architected and shipped a production-grade feature serving 10k+ daily users.",
                "Improved end-to-end test coverage from 42% to 87%, eliminating 3 recurring incidents.",
                "Mentored 4 junior engineers; 2 promoted within 12 months.",
            ],
        })

    def _mock_skill_gap(self, text: str) -> str:
        role_match = re.search(r"role[:\s]+([^\n,]+)", text, re.I)
        role = role_match.group(1).strip()[:60] if role_match else "the target role"
        current = []
        cur_match = re.search(r"current\s+skills?[:\s]+([^\n]+)", text, re.I)
        if cur_match:
            current = [s.strip() for s in re.split(r"[,;]", cur_match.group(1)) if s.strip()]
        current_lower = {c.lower() for c in current}
        role_to_skills = {
            "data scientist": ["python", "pandas", "numpy", "sql", "statistics", "machine learning", "data visualization", "scikit-learn"],
            "full stack": ["javascript", "react", "node.js", "html", "css", "rest api", "sql", "git"],
            "backend": ["python", "fastapi", "sql", "rest api", "docker", "redis", "git", "system design"],
            "frontend": ["javascript", "react", "css", "html", "typescript", "tailwind", "git", "testing"],
            "ml engineer": ["python", "pytorch", "tensorflow", "sql", "docker", "mlops", "linear algebra", "data engineering"],
            "devops": ["linux", "docker", "kubernetes", "aws", "terraform", "ci/cd", "monitoring", "bash"],
        }
        key = next((k for k in role_to_skills if k in role.lower()), "data scientist")
        target_skills = role_to_skills[key]
        matched = [s for s in target_skills if s in current_lower]
        missing = [s for s in target_skills if s not in current_lower]
        readiness = round(100.0 * len(matched) / max(1, len(target_skills)), 1)
        breakdown = [{
            "skill": s,
            "has": s in current_lower,
            "importance": round(random.uniform(0.6, 1.0), 2),
            "category": "core" if random.random() > 0.3 else "nice-to-have",
        } for s in target_skills]
        return json.dumps({
            "target_role": role,
            "readiness_percent": readiness,
            "matched_skills": matched,
            "missing_skills": missing,
            "skill_breakdown": breakdown,
            "learning_roadmap": [
                f"Week 1-2: Strengthen fundamentals in {missing[0] if missing else target_skills[0]}",
                "Week 3-4: Hands-on mini-projects covering missing skills",
                "Week 5-6: Build a portfolio-grade end-to-end project",
                "Week 7-8: Mock interviews and resume tailoring",
            ],
            "project_ideas": [
                f"Build a {key} project demonstrating the top 3 missing skills.",
                "Contribute a feature to an open-source repo in the relevant ecosystem.",
                "Publish a write-up of the project as a blog post.",
            ],
            "estimated_weeks_to_ready": max(4, len(missing) * 2),
        })

    def _mock_recommendations(self, text: str) -> str:
        items = [
            {"title": "CS50: Introduction to Computer Science", "type": "course", "provider": "Harvard / edX",
             "url": "https://cs50.harvard.edu/x/", "reason": "Strong foundations in CS concepts.",
             "duration": "10 weeks", "level": "beginner"},
            {"title": "freeCodeCamp Full Stack Path", "type": "course", "provider": "freeCodeCamp",
             "url": "https://www.freecodecamp.org/", "reason": "Project-based, free, well-rounded.",
             "duration": "300+ hrs", "level": "beginner"},
            {"title": "The Net Ninja - React Crash Course", "type": "youtube", "provider": "YouTube",
             "url": "https://www.youtube.com/c/TheNetNinja", "reason": "Excellent React fundamentals.",
             "duration": "10 hrs", "level": "beginner"},
            {"title": "Official Python Documentation", "type": "doc", "provider": "python.org",
             "url": "https://docs.python.org/3/", "reason": "Authoritative reference.",
             "duration": "self-paced", "level": "all"},
            {"title": "LeetCode Top Interview 150", "type": "practice", "provider": "LeetCode",
             "url": "https://leetcode.com/", "reason": "Highly-rated interview prep problem set.",
             "duration": "6-8 weeks", "level": "intermediate"},
            {"title": "AWS Cloud Practitioner Certification", "type": "certification", "provider": "AWS",
             "url": "https://aws.amazon.com/certification/certified-cloud-practitioner/",
             "reason": "Industry-recognized cloud foundation.", "duration": "4 weeks", "level": "beginner"},
        ]
        return json.dumps({"items": items, "notes": "Curated picks tuned to your interests and target role."})


# Module-level singleton
llm_service = LLMService()
