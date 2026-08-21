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
        box-sizing: border-box;
    }
    
    /* Light and Dark Mode Support */
    :root {
        color-scheme: light dark;
    }
    
    @media (prefers-color-scheme: light) {
        :root {
            --bg-primary: #fafafa;
            --bg-secondary: #ffffff;
            --text-primary: #1a1a1a;
            --text-secondary: #666;
            --text-tertiary: #999;
            --border-color: #e8e8e8;
            --border-light: #f0f0f0;
            --header-gradient: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
            --button-bg: #1a1a1a;
            --button-hover: #333333;
            --card-shadow: 0 2px 8px rgba(0,0,0,0.04);
            --card-shadow-hover: 0 4px 12px rgba(0,0,0,0.08);
            --link-color: #0066cc;
        }
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0f0f0f;
            --bg-secondary: #1a1a1a;
            --text-primary: #e8e8e8;
            --text-secondary: #b0b0b0;
            --text-tertiary: #888;
            --border-color: #333333;
            --border-light: #2a2a2a;
            --header-gradient: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%);
            --button-bg: #e8e8e8;
            --button-hover: #d0d0d0;
            --card-shadow: 0 2px 8px rgba(0,0,0,0.3);
            --card-shadow-hover: 0 4px 12px rgba(0,0,0,0.5);
            --link-color: #4da6ff;
        }
    }
    
    html, body {
        background: var(--bg-primary);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, sans-serif;
    }
    
    .main {
        background: var(--bg-primary);
        padding: 0 !important;
    }
    
    [data-testid="stAppViewContainer"] {
        padding: 0 !important;
    }
    
    [data-testid="stHeader"] {
        background: transparent;
        padding: 0 !important;
    }
    
    [data-testid="stDecoratedFunction"] {
        padding: 0 !important;
    }
    
    .header {
        background: var(--header-gradient);
        padding: 48px 24px 32px;
        border-bottom: 1px solid var(--border-color);
        text-align: center;
    }
    
    .header-title {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 12px 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 14px;
        color: var(--text-secondary);
        font-weight: 400;
        margin: 0;
    }
    
    .container {
        padding: 20px;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .stButton > button {
        width: 100% !important;
        padding: 16px 24px !important;
        background: var(--button-bg) !important;
        color: var(--bg-primary) !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        margin: 24px 0 !important;
        letter-spacing: 0.3px;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background: var(--button-hover) !important;
    }
    
    .stButton > button:active {
        transform: scale(0.98);
    }
    
    .project-card {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        border: 1px solid var(--border-color);
        box-shadow: var(--card-shadow);
        transition: all 0.2s ease;
    }
    
    .project-card:hover {
        border-color: var(--text-tertiary);
        box-shadow: var(--card-shadow-hover);
    }
    
    .project-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
        gap: 12px;
    }
    
    .project-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.3;
        flex: 1;
    }
    
    .project-score {
        font-size: 22px;
        font-weight: 700;
        color: var(--text-primary);
        flex-shrink: 0;
    }
    
    .project-category {
        display: inline-block;
        background: var(--border-light);
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .project-description {
        font-size: 14px;
        color: var(--text-secondary);
        line-height: 1.5;
        margin: 10px 0;
    }
    
    .project-link-section {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid var(--border-light);
    }
    
    .project-link {
        color: var(--link-color);
        text-decoration: none;
        font-weight: 600;
        font-size: 13px;
        word-break: break-all;
        display: inline-block;
        max-width: 100%;
    }
    
    .project-link:hover {
        text-decoration: underline;
    }
    
    .project-meta {
        font-size: 12px;
        color: var(--text-tertiary);
        margin-top: 8px;
    }
    
    .stats-box {
        background: var(--bg-secondary);
        padding: 28px 20px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        text-align: center;
        margin: 28px 0;
        box-shadow: var(--card-shadow);
    }
    
    .stats-number {
        font-size: 36px;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .stats-label {
        font-size: 13px;
        color: var(--text-secondary);
        margin-top: 8px;
        letter-spacing: 0.3px;
    }
    
    .divider {
        height: 1px;
        background: var(--border-color);
        margin: 24px 0;
    }
    
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 24px 0 16px 0;
    }
    
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
    }
    
    .stTextInput > div > div > input {
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }
    
    .stSpinner {
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1 class="header-title">Project Discovery</h1>
    <p class="header-subtitle">Fresh projects and emerging ideas</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="container">', unsafe_allow_html=True)

# API KEY INPUT
with st.sidebar:
    st.markdown("**API Key**")
    api_key = st.text_input(
        "Enter your API key",
        type="password",
        placeholder="sk-ant-...",
        label_visibility="collapsed"
    )
    st.caption("Get from console.anthropic.com")

col1, col2, col3 = st.columns([0.5, 1, 0.5])
with col2:
    if st.button("Discover Projects", use_container_width=True, key="main_button"):
        if not api_key:
            st.error("Enter your API key in the sidebar")
        else:
            st.session_state.loading = True
            st.session_state.api_key = api_key

if 'loading' in st.session_state and st.session_state.loading:
    with st.spinner("Finding fresh projects..."):
        try:
            news_sources = {
                'HackerNews': 'https://news.ycombinator.com/rss',
                'ProductHunt': 'https://www.producthunt.com/feed',
                'Lobsters': 'https://lobste.rs/rss',
            }
            
            articles = []
            
            for source_name, url in news_sources.items():
                try:
                    feed = feedparser.parse(url)
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
                except:
                    pass
            
            st.markdown(f"<p style='text-align: center; color: var(--text-tertiary); font-size: 13px;'>Analyzing {len(articles)} articles...</p>", unsafe_allow_html=True)
            
            if not articles:
                st.error("No articles found")
                st.session_state.loading = False
                st.stop()
            
            client = anthropic.Anthropic(api_key=st.session_state.api_key)
            projects = {}
            
            progress_bar = st.progress(0)
            
            for idx, article in enumerate(articles[:60]):
                try:
                    title = article['title']
                    link = article['link']
                    
                    msg = client.messages.create(
                        model="claude-opus-4-8",
                        max_tokens=300,
                        messages=[
                            {
                                "role": "user",
                                "content": f"""Analyze for FRESH, EMERGING, SMALL projects (NOT big companies).

Title: {title}

Return JSON:
{{
  "is_fresh_project": true/false,
  "project_name": "name or null",
  "description": "1-2 lines what it does",
  "category": "AI/Web/Tools/Design/Infra/etc",
  "vibe_score": 1-100
}}"""
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
                
                except:
                    pass
                
                progress_bar.progress((idx + 1) / 60)
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            if projects:
                sorted_projects = sorted(
                    projects.items(),
                    key=lambda x: x[1]['vibe_score'],
                    reverse=True
                )[:30]
                
                st.markdown(f'<h2 class="section-title">{len(sorted_projects)} Projects Found</h2>', unsafe_allow_html=True)
                
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
                        <div class="project-link-section">
                            <a href="{info['link']}" target="_blank" class="project-link">View Project</a>
                            <div class="project-meta">{date} • {info['source']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="stats-box">
                    <div class="stats-number">{len(sorted_projects)}</div>
                    <div class="stats-label">Fresh projects discovered</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("No projects found")
            
            st.session_state.loading = False
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.loading = False

st.markdown('</div>', unsafe_allow_html=True)
