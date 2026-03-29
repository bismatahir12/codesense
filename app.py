import streamlit as st
import time
from agent.reviewer import CodeReviewAgent
from utils.github_client import GitHubClient
from utils.parser import parse_pr_url

st.set_page_config(
    page_title="CodeSense — AI Code Reviewer",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: 'Geist', sans-serif;
    background: #080810 !important;
    color: #e2e0f0;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2a3e; border-radius: 2px; }

div[data-testid="stSidebar"] {
    background: #0c0c18 !important;
    border-right: 1px solid #16162a !important;
}
.sidebar-brand {
    padding: 2rem 1.5rem 1.5rem;
    border-bottom: 1px solid #16162a;
    margin-bottom: 1.5rem;
}
.sidebar-logo {
    font-family: 'Instrument Serif', serif;
    font-size: 1.5rem;
    color: #e2e0f0;
    letter-spacing: -0.02em;
}
.sidebar-logo .hex { color: #7c6af7; }
.sidebar-tagline {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #2a2a4a;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 0.3rem;
}
.sidebar-section-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #3a3a5c;
    margin-bottom: 0.8rem;
    padding: 0 1.5rem;
}
.stTextInput input {
    background: #0f0f1e !important;
    border: 1px solid #1e1e32 !important;
    border-radius: 8px !important;
    color: #e2e0f0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}
.stTextInput input:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 3px #7c6af715 !important;
}
.stTextInput label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: #4a4a6a !important;
}
[data-testid="stWidgetLabel"] p {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: #4a4a6a !important;
}
.stToggle label p {
    font-family: 'Geist', sans-serif !important;
    font-size: 0.82rem !important;
    color: #6666888 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #7c6af7 0%, #5b4fcf 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    box-shadow: 0 4px 20px #7c6af730 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 30px #7c6af750 !important;
}
.page-header {
    padding: 3rem 0 2.5rem;
    border-bottom: 1px solid #12122a;
    margin-bottom: 2.5rem;
}
.page-title {
    font-family: 'Instrument Serif', serif;
    font-size: 3.4rem;
    font-weight: 400;
    color: #e2e0f0;
    letter-spacing: -0.03em;
    line-height: 1.05;
    margin-bottom: 0.6rem;
}
.page-title em { font-style: italic; color: #7c6af7; }
.page-subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #3a3a5c;
    text-transform: uppercase;
    letter-spacing: 0.15em;
}
.url-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #3a3a5c;
    margin-bottom: 0.5rem;
}
.pr-meta-card {
    background: #0c0c1a;
    border: 1px solid #16162e;
    border-radius: 14px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: flex-start;
    gap: 1.2rem;
    animation: fadeUp 0.4s ease;
}
.pr-meta-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #22c55e;
    margin-top: 0.35rem;
    flex-shrink: 0;
    box-shadow: 0 0 10px #22c55e80;
}
.pr-meta-title {
    font-family: 'Geist', sans-serif;
    font-size: 1rem;
    font-weight: 500;
    color: #e2e0f0;
    margin-bottom: 0.4rem;
}
.pr-meta-details {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #4a4a6a;
    display: flex;
    gap: 1.4rem;
    flex-wrap: wrap;
}
.pr-meta-details .add { color: #22c55e; }
.pr-meta-details .del { color: #ef4444; }
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
    animation: fadeUp 0.5s ease;
}
.stat-tile {
    background: #0c0c1a;
    border: 1px solid #16162e;
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.stat-tile::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.stat-tile.critical::after   { background: #ef4444; }
.stat-tile.warning::after    { background: #f59e0b; }
.stat-tile.suggestion::after { background: #7c6af7; }
.stat-tile.score::after      { background: #22c55e; }
.stat-number {
    font-family: 'Instrument Serif', serif;
    font-size: 2.8rem;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.stat-tile.critical .stat-number   { color: #ef4444; }
.stat-tile.warning .stat-number    { color: #f59e0b; }
.stat-tile.suggestion .stat-number { color: #7c6af7; }
.stat-tile.score .stat-number      { color: #22c55e; }
.stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #3a3a5c;
}
.summary-section {
    background: #0c0c1a;
    border: 1px solid #16162e;
    border-radius: 14px;
    padding: 1.8rem;
    margin-bottom: 2rem;
    animation: fadeUp 0.6s ease;
}
.section-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #3a3a5c;
    margin-bottom: 0.8rem;
}
.summary-text {
    font-family: 'Geist', sans-serif;
    font-size: 0.95rem;
    color: #9090b0;
    line-height: 1.8;
}
.comment-card {
    background: #0c0c1a;
    border: 1px solid #16162e;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.75rem;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    transition: border-color 0.2s, transform 0.15s;
    animation: fadeUp 0.4s ease;
}
.comment-card:hover { border-color: #2a2a4a; transform: translateX(4px); }
.comment-card.critical   { border-left: 2px solid #ef4444; }
.comment-card.warning    { border-left: 2px solid #f59e0b; }
.comment-card.suggestion { border-left: 2px solid #7c6af7; }
.comment-card.praise     { border-left: 2px solid #22c55e; }
.comment-icon { font-size: 0.9rem; flex-shrink: 0; margin-top: 0.1rem; }
.comment-body { flex: 1; }
.comment-meta { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem; flex-wrap: wrap; }
.comment-badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 500;
}
.badge-critical   { background: #ef444415; color: #ef4444; border: 1px solid #ef444430; }
.badge-warning    { background: #f59e0b15; color: #f59e0b; border: 1px solid #f59e0b30; }
.badge-suggestion { background: #7c6af715; color: #7c6af7; border: 1px solid #7c6af730; }
.badge-praise     { background: #22c55e15; color: #22c55e; border: 1px solid #22c55e30; }
.comment-file {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #4a4a6a;
    background: #12122a;
    padding: 1px 7px;
    border-radius: 4px;
}
.comment-text {
    font-family: 'Geist', sans-serif;
    font-size: 0.87rem;
    color: #8080a8;
    line-height: 1.7;
}
.divider {
    display: flex; align-items: center; gap: 1rem; margin: 2.5rem 0;
}
.divider-line { flex: 1; height: 1px; background: #12122a; }
.divider-dot  { width: 4px; height: 4px; border-radius: 50%; background: #2a2a4a; }
.stProgress > div > div {
    background: linear-gradient(90deg, #7c6af7, #5b4fcf) !important;
    border-radius: 4px !important;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 880px; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-logo"><span class="hex">⬡</span> CodeSense</div>
        <div class="sidebar-tagline">AI-powered code review</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">Credentials</div>', unsafe_allow_html=True)
    openai_key   = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    github_token = st.text_input("GitHub Token", type="password", placeholder="ghp_...")

    st.markdown('<br><div class="sidebar-section-title">Review settings</div>', unsafe_allow_html=True)
    review_depth      = st.select_slider("Depth", options=["Quick", "Standard", "Deep"], value="Standard")
    post_comments     = st.toggle("Post to GitHub PR",    value=False)
    check_security    = st.toggle("Security analysis",    value=True)
    check_performance = st.toggle("Performance analysis", value=True)
    check_style       = st.toggle("Style & readability",  value=True)

    st.markdown("""
    <br>
    <div style="font-family: DM Mono, monospace; font-size: 0.62rem; color: #2a2a4a; line-height: 2; padding: 0 0.2rem;">
        MODEL &nbsp;· llama-3.3-70b-versatile<br>
        INFRA &nbsp;·· Groq<br>
        STACK &nbsp;·· LangChain + GitHub API
    </div>
    """, unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-title">Code Review,<br><em>Reimagined.</em></div>
    <div class="page-subtitle">Paste a GitHub PR — get instant AI-powered feedback</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="url-label">Pull Request URL</div>', unsafe_allow_html=True)
pr_url = st.text_input("pr", placeholder="https://github.com/owner/repo/pull/42", label_visibility="collapsed")
run_review = st.button("⬡  Analyse Pull Request")

st.markdown('<div class="divider"><div class="divider-line"></div><div class="divider-dot"></div><div class="divider-line"></div></div>', unsafe_allow_html=True)

if run_review:
    if not pr_url:
        st.error("Enter a PR URL above.")
        st.stop()
    if not openai_key:
        st.error("Add your Groq API key in the sidebar.")
        st.stop()
    if not github_token:
        st.error("Add your GitHub token in the sidebar.")
        st.stop()

    parsed = parse_pr_url(pr_url)
    if not parsed:
        st.error("Invalid URL — use: https://github.com/owner/repo/pull/42")
        st.stop()

    owner, repo, pr_number = parsed

    with st.spinner("Connecting to GitHub..."):
        try:
            gh = GitHubClient(github_token)
            pr_data = gh.get_pr_data(owner, repo, pr_number)
        except Exception as e:
            st.error(f"GitHub error: {e}")
            st.stop()

    st.markdown(f"""
    <div class="pr-meta-card">
        <div class="pr-meta-dot"></div>
        <div>
            <div class="pr-meta-title">#{pr_number} — {pr_data['title']}</div>
            <div class="pr-meta-details">
                <span>👤 {pr_data['author']}</span>
                <span>📁 {pr_data['changed_files']} files</span>
                <span class="add">+{pr_data['additions']}</span>
                <span class="del">-{pr_data['deletions']}</span>
                <span>🌿 {pr_data['head_branch']} → {pr_data['base_branch']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    focus_areas = []
    if check_security:     focus_areas.append("security")
    if check_performance:  focus_areas.append("performance")
    if check_style:        focus_areas.append("code style")

    pb   = st.progress(0)
    stat = st.empty()

    for pct, msg in [(15, "Initialising agent..."), (40, "Parsing diff..."), (62, "Llama 3.3 analysing code...")]:
        stat.markdown(f'<div style="font-family:DM Mono,monospace;font-size:0.72rem;color:#4a4a6a;">{msg}</div>', unsafe_allow_html=True)
        pb.progress(pct)
        time.sleep(0.25)

    try:
        agent  = CodeReviewAgent(openai_api_key=openai_key, depth=review_depth, focus_areas=focus_areas)
        result = agent.review(pr_data)
    except Exception as e:
        st.error(f"Agent error: {e}")
        st.stop()

    pb.progress(100)
    pb.empty()
    stat.empty()

    comments = result.get("comments", [])
    summary  = result.get("summary",  "")
    score    = result.get("score",    "—")

    nc = len([c for c in comments if c["severity"] == "critical"])
    nw = len([c for c in comments if c["severity"] == "warning"])
    ns = len([c for c in comments if c["severity"] == "suggestion"])

    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-tile critical">
            <div class="stat-number">{nc}</div>
            <div class="stat-label">Critical</div>
        </div>
        <div class="stat-tile warning">
            <div class="stat-number">{nw}</div>
            <div class="stat-label">Warnings</div>
        </div>
        <div class="stat-tile suggestion">
            <div class="stat-number">{ns}</div>
            <div class="stat-label">Suggestions</div>
        </div>
        <div class="stat-tile score">
            <div class="stat-number">{score}</div>
            <div class="stat-label">Quality score</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-section">
        <div class="section-eyebrow">Summary</div>
        <div class="summary-text">{summary}</div>
    </div>
    """, unsafe_allow_html=True)

    if comments:
        icons = {
            "critical":   ("🔴", "badge-critical",   "critical"),
            "warning":    ("🟡", "badge-warning",    "warning"),
            "suggestion": ("🔵", "badge-suggestion", "suggestion"),
            "praise":     ("🟢", "badge-praise",     "praise"),
        }
        st.markdown('<div class="section-eyebrow" style="margin-bottom:1rem">Review Comments</div>', unsafe_allow_html=True)
        for sev in ["critical", "warning", "suggestion", "praise"]:
            for c in [x for x in comments if x["severity"] == sev]:
                icon, badge_cls, card_cls = icons[sev]
                file_chip = f'<span class="comment-file">📄 {c["file"]}</span>' if c.get("file") else ""
                st.markdown(f"""
                <div class="comment-card {card_cls}">
                    <div class="comment-icon">{icon}</div>
                    <div class="comment-body">
                        <div class="comment-meta">
                            <span class="comment-badge {badge_cls}">{sev}</span>
                            {file_chip}
                        </div>
                        <div class="comment-text">{c['comment']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    if post_comments and comments:
        st.markdown('<div class="divider"><div class="divider-line"></div><div class="divider-dot"></div><div class="divider-line"></div></div>', unsafe_allow_html=True)
        if st.button("📬  Post Review to GitHub"):
            with st.spinner("Posting..."):
                try:
                    sev_emoji = {"critical":"🔴","warning":"🟡","suggestion":"🔵","praise":"🟢"}
                    body = f"## ⬡ CodeSense Review\n\n**Quality Score: {score}/10**\n\n> {summary}\n\n---\n\n"
                    for sev in ["critical","warning","suggestion","praise"]:
                        group = [c for c in comments if c["severity"]==sev]
                        if group:
                            body += f"### {sev_emoji[sev]} {sev.title()}s\n"
                            for c in group:
                                ref = f" `{c['file']}`" if c.get("file") else ""
                                body += f"-{ref} {c['comment']}\n"
                            body += "\n"
                    gh.post_pr_comment(owner, repo, pr_number, body)
                    st.success("✅ Review posted to GitHub!")
                except Exception as e:
                    st.error(f"Failed: {e}")