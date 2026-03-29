# 🔍 AI Code Reviewer

An LLM-powered GitHub PR review agent built with LangChain, OpenAI, and Streamlit.

Paste any public (or private, with a token) GitHub Pull Request URL and get instant structured code review — bugs, security issues, performance problems, style suggestions, and an overall quality score.

---

## ✨ Features

- **Automatic PR analysis** — fetches diff, files, and metadata via GitHub API
- **Structured review** — categorised as Critical / Warning / Suggestion / Praise
- **Quality score** — LLM rates the PR from 1–10
- **Configurable depth** — Quick (GPT-4o-mini, fast) or Deep (GPT-4o, thorough)
- **Focus areas** — toggle security, performance, and style checks
- **GitHub integration** — optionally posts the review directly as a PR comment
- **Clean dark UI** — production-quality Streamlit frontend

---

## 🚀 Getting Started

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/ai-code-reviewer
cd ai-code-reviewer
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

### 3. Configure in the sidebar

| Field | Where to get it |
|---|---|
| OpenAI API Key | platform.openai.com → API Keys |
| GitHub Token | GitHub → Settings → Developer Settings → Personal Access Tokens |

GitHub token needs scopes: `repo` (for private repos) or just `public_repo` for public ones.

---

## 🏗️ Architecture

```
ai-code-reviewer/
├── app.py                  # Streamlit UI
├── agent/
│   └── reviewer.py         # LangChain review agent (the brain)
├── utils/
│   ├── github_client.py    # GitHub REST API client
│   └── parser.py           # PR URL parser
└── requirements.txt
```

### How it works

1. User pastes a PR URL → `parser.py` extracts owner/repo/number
2. `GitHubClient` fetches PR metadata + per-file diffs via GitHub API
3. `CodeReviewAgent` builds a structured prompt with the diff
4. LangChain + OpenAI returns a structured JSON review
5. Streamlit renders the review with severity-coded cards
6. Optionally posts the review back to GitHub as a PR comment

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-4o / GPT-4o-mini |
| LLM Framework | LangChain |
| GitHub | GitHub REST API v3 |
| Frontend | Streamlit |
| Language | Python 3.10+ |

---

## 🌐 Deploy for free

**Streamlit Cloud:**
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect your repo → Deploy
4. Add secrets in Streamlit Cloud dashboard (no hardcoded keys)

---

## 💡 Ideas to extend this

- Add line-level comments (GitHub review API) for precise annotation
- Support GitLab and Bitbucket
- Add a LangGraph multi-agent pipeline (Reviewer + Security Auditor + Style Checker)
- Store review history in SQLite
- Add webhook support so it auto-reviews every new PR

---

## 📸 Demo

Paste any PR URL like:
```
https://github.com/owner/repo/pull/42
```

The agent will:
- Fetch the PR diff
- Analyse it with LangChain + OpenAI
- Return categorised feedback with a quality score
- Optionally post the review to GitHub

---

Built as part of an AI Engineer portfolio. Stack: LangChain · OpenAI · GitHub API · Streamlit.
