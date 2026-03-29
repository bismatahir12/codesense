import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """You are a senior software engineer doing a code review.
Focus areas: {focus_areas} | Depth: {depth} | Max comments: {max_comments}

Respond ONLY with valid JSON in this exact format, nothing else:
{{
  "summary": "2-4 sentence overall summary of the PR",
  "score": 7,
  "comments": [
    {{"severity": "critical", "file": "app.py", "comment": "explanation of issue"}},
    {{"severity": "warning",  "file": "utils.py", "comment": "explanation"}},
    {{"severity": "suggestion", "file": "", "comment": "general suggestion"}},
    {{"severity": "praise", "file": "models.py", "comment": "something done well"}}
  ]
}}

Severity rules:
- critical   = bugs, security vulnerabilities, broken logic
- warning    = bad practices, missing error handling, performance
- suggestion = style, readability, naming improvements
- praise     = genuinely good patterns worth highlighting

Be specific. Reference actual filenames and code. Do not invent issues."""

USER_PROMPT = """PR Title: {title}
Author: {author} | {head_branch} → {base_branch}
Files changed: {changed_files} (+{additions} -{deletions})

--- DIFF ---
{diff}
--- END DIFF ---

Return your review as JSON only."""


class CodeReviewAgent:
    DEPTH_CONFIG = {
        "Quick":    {"model": "llama-3.1-8b-instant",   "max_comments": 5,  "temperature": 0.2},
        "Standard": {"model": "llama-3.3-70b-versatile", "max_comments": 10, "temperature": 0.3},
        "Deep":     {"model": "llama-3.3-70b-versatile", "max_comments": 20, "temperature": 0.3},
    }

    def __init__(self, openai_api_key: str, depth: str = "Standard", focus_areas: list = None):
        cfg = self.DEPTH_CONFIG.get(depth, self.DEPTH_CONFIG["Standard"])
        self.llm = ChatGroq(
            model=cfg["model"],
            temperature=cfg["temperature"],
            groq_api_key=openai_api_key,
        )
        self.max_comments = cfg["max_comments"]
        self.focus_areas = ", ".join(focus_areas) if focus_areas else "security, performance, code style"
        self.depth = depth
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human",  USER_PROMPT),
        ])
        self.chain = self.prompt | self.llm

    def review(self, pr_data: dict) -> dict:
        response = self.chain.invoke({
            "focus_areas":   self.focus_areas,
            "depth":         self.depth,
            "max_comments":  self.max_comments,
            "title":         pr_data["title"],
            "author":        pr_data["author"],
            "head_branch":   pr_data["head_branch"],
            "base_branch":   pr_data["base_branch"],
            "changed_files": pr_data["changed_files"],
            "additions":     pr_data["additions"],
            "deletions":     pr_data["deletions"],
            "diff":          self._build_diff(pr_data),
        })
        return self._parse(response.content)

    def _build_diff(self, pr_data: dict) -> str:
        parts = [
            f"### {f['filename']}\n{f['patch'][:3000]}"
            for f in pr_data.get("files", []) if f.get("patch")
        ]
        return ("\n\n".join(parts) or pr_data.get("diff", "No diff."))[:8000]

    def _parse(self, raw: str) -> dict:
        try:
            text = raw.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except Exception:
            return {
                "summary": "Review complete.",
                "score": "N/A",
                "comments": [{"severity": "suggestion", "file": "", "comment": raw}]
            }