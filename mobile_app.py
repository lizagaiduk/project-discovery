import streamlit as st
import feedparser
from datetime import datetime
import anthropic
import json

st.set_page_config(
    page_title="Project Discovery",
    page_icon="▪️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }

    body {
        background: #f8f8f8;
        color: #1a1a1a;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main {
        background: #f8f8f8;
        padding-top: 0 !important;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .header-section {
        background: #ffffff;
        padding: 80px 40px;
        text-align: center;
        border-bottom: 1px solid #e5e5e5;
        margin: 0;
    }

    .header-title {
        font-size: 48px;
        font-weight: 300;
        color: #1a1a1a;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .header-subtitle {
        font-size: 15px;
        color: #888;
        margin-top: 16px;
        font-weight: 400;
        letter-spacing: 0.3px;
    }

    .stButton > button {
        width: 100% !important;
        padding: 14px 24px !important;
        background: #1a1a1a !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        margin: 40px 0 !important;
        letter-spacing: 0.3px;
    }

    .stButton > button:hover {
        background: #333333 !important;
    }

    .project-card {
        background: #ffffff;
        border-radius: 6px;
        padding: 28px;
        margin: 12px 0;
        border: 1px solid #e5e5e5;
        transition: all 0.2s ease;
    }

    .project-card:hover {
        border-color: #cccccc;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .project-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
    }

    .project-title {
        font-size: 18px;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0;
    }

    .project-score {
        font-size: 24px;
        font-weight: 600;
        color: #1a1a1a;
    }

    .project-category {
        display: inline-block;
        background: #f0f0f0;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        color: #666;
        margin-bottom: 12px;
    }

    .project-description {
        font-size: 14px;
        color: #555;
        margin: 12px 0;
        line-height: 1.6;
    }

    .project-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #f0f0f0;
        font-size: 12px;
        color: #999;
    }

    .project-link {
        color: #0066cc;
        text-decoration: none;
        font-weight: 500;
        cursor: pointer;
    }

    .project-link:hover {
        text-decoration: underline;
    }

    .stats-box {
        background: #ffffff;
        padding: 32px 24px;
        border-radius: 6px;
        border: 1px solid #e5e5e5;
        text-align: center;
        margin: 40px 0;
    }

    .stats-number {
        font-size: 36px;
        font-weight: 600;
        color: #1a1a1a;
    }

    .stats-label {
        font-size: 13px;
        color: #888;
        margin-top: 8px;
        letter-spacing: 0.3px;
    }

    .divider {
        height: 1px;
        background: #e5e5e5;
        margin: 40px 0;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
    }

    .sidebar-header {
        font-size: 14px;
        font-weight: 600;
        color: #1a1a1a;
        margin: 24px 16px 16px 16px;
        letter-spacing: 0.3px;
    }

    .stTextInput > div > div > input {
        border: 1px solid #e5e5e5 !important;
        border-radius: 6px !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

print("\n" + "=" * 80)
print("PROJECT DISCOVERY APP STARTED")
print("=" * 80 + "\n")

st.markdown("""
<div class="header-section">
    <h1 class="header-title">Project Discovery</h1>
    <p class="header-subtitle">Fresh projects and emerging ideas from this week</p>
</div>
""", unsafe_allow_html=True)

# API KEY INPUT
with st.sidebar:
    st.markdown('<div class="sidebar-header">Authentication</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-ant-..."
    )

col1, col2, col3 = st.columns([0.5, 1, 0.5])
with col2:
    if st.button("Discover Projects", use_container_width=True, key="main_button"):
        if not api_key:
            st.error("Please enter your API key")
            print("ERROR: No API key provided")
        else:
            st.session_state.loading = True
            st.session_state.api_key = api_key

if 'loading' in st.session_state and st.session_state.loading:
    print("\n" + "=" * 80)
    print("FETCHING PROJECT NEWS")
    print("=" * 80 + "\n")

    with st.spinner("Analyzing sources..."):
        try:
            news_sources = {
                'HackerNews': 'https://news.ycombinator.com/rss',
                'ProductHunt': 'https://www.producthunt.com/feed',
                'Lobsters': 'https://lobste.rs/rss',
            }

            articles = []

            for source_name, url in news_sources.items():
                print(f"Fetching from {source_name}...")
                try:
                    feed = feedparser.parse(url)
                    count = 0
                    for entry in feed.entries[:50]:
                        title = entry.get('title', '')
                        link = entry.get('link', '')
                        published = entry.get('published', '')
                        if title and link:
                            articles.append({
                                'title': title,
                                'link': link,
                                'source': source_name,
                                'published': published
                            })
                            count += 1
                    print(f"  Got {count} items from {source_name}")
                except Exception as e:
                    print(f"  Error: {str(e)}")

            print(f"\nTotal: {len(articles)} items collected\n")
            st.write(f"Found {len(articles)} items from {len(news_sources)} sources")

            if not articles:
                st.error("No articles found")
                st.session_state.loading = False
                st.stop()

            print("=" * 80)
            print("ANALYZING FOR FRESH PROJECTS")
            print("=" * 80 + "\n")

            client = anthropic.Anthropic(api_key=st.session_state.api_key)
            projects = {}

            progress_bar = st.progress(0)
            st.write("Analyzing emerging projects...")

            print(f"Processing up to 60 items...\n")

            for idx, article in enumerate(articles[:60]):
                try:
                    title = article['title']
                    link = article['link']
                    print(f"[{idx + 1}/60] {title[:70]}...")

                    msg = client.messages.create(
                        model="claude-opus-4-8",
                        max_tokens=300,
                        messages=[
                            {
                                "role": "user",
                                "content": f"""Analyze this for FRESH, EMERGING, SMALL projects or ideas (NOT big companies like Meta, Google, OpenAI).

Title: {title}

Return JSON:
{{
  "is_fresh_project": true/false,
  "project_name": "name or null",
  "description": "1-2 lines what it does",
  "category": "AI/Web/Tools/Infra/Design/etc or null",
  "vibe_score": 1-100
}}

Look for: New startups, indie projects, viral ideas, fresh features, emerging tools, HN launches, YC projects, cool GitHub projects.
Skip: Big tech companies, old news."""
                            }
                        ]
                    )

                    response_text = msg.content[0].text.strip()

                    if '```' in response_text:
                        response_text = response_text.split('```')[1]
                        if response_text.startswith('json'):
                            response_text = response_text[4:]

                    data = json.loads(response_text)

                    if data.get('is_fresh_project') and data.get('project_name'):
                        project_name = data['project_name']
                        if project_name not in projects:
                            projects[project_name] = {
                                'description': data.get('description', 'Fresh project'),
                                'category': data.get('category', 'Projects'),
                                'vibe_score': int(data.get('vibe_score', 50)),
                                'link': link,
                                'published': article['published'],
                                'source': article['source']
                            }
                            print(f"  FOUND: {project_name}")
                        else:
                            print(f"  DUPLICATE: {project_name}")
                    else:
                        print(f"  SKIP")

                except Exception as e:
                    print(f"  Error: {str(e)[:40]}")

                progress_bar.progress((idx + 1) / 60)

            print("\n" + "=" * 80)
            print(f"RESULTS: Found {len(projects)} fresh projects")
            print("=" * 80 + "\n")

            if projects:
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

                sorted_projects = sorted(
                    projects.items(),
                    key=lambda x: x[1]['vibe_score'],
                    reverse=True
                )[:30]

                st.markdown(
                    f"<h2 style='font-size: 24px; font-weight: 600; color: #1a1a1a; margin-bottom: 24px;'>{len(sorted_projects)} Fresh Projects</h2>",
                    unsafe_allow_html=True)

                for idx, (name, info) in enumerate(sorted_projects, 1):
                    vibe = info['vibe_score']
                    category = info.get('category', 'Projects')
                    date = info.get('published', 'Recently')[:10]

                    st.markdown(f"""
                    <div class="project-card">
                        <div class="project-header">
                            <div>
                                <span class="project-category">{category}</span>
                                <div class="project-title">{idx}. {name}</div>
                            </div>
                            <div class="project-score">{vibe}</div>
                        </div>
                        <div class="project-description">{info['description']}</div>
                        <div class="project-meta">
                            <a href="{info['link']}" target="_blank" class="project-link">View Project</a>
                            <span>{date} · {info['source']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="stats-box">
                    <div class="stats-number">{len(sorted_projects)}</div>
                    <div class="stats-label">Fresh projects discovered</div>
                </div>
                """, unsafe_allow_html=True)

                print(f"SUCCESS: Found and displayed {len(sorted_projects)} projects\n")

            else:
                st.warning("No projects found")

            st.session_state.loading = False

        except Exception as e:
            print(f"\nFATAL ERROR: {str(e)}\n")
            st.error(f"Error: {str(e)}")
            st.session_state.loading = False