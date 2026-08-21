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
    
    html, body {
        color: #1a1a1a;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, sans-serif;
    }
    
    .main {
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
        padding: 60px 20px 40px;
        text-align: center;
    }
    
    .header-title {
        font-size: 36px;
        font-weight: 700;
        color: #ff8800;
        margin: 0 0 16px 0;
    }
    
    .header-subtitle {
        font-size: 16px;
        color: #ff8800;
        font-weight: 400;
        margin: 0;
    }
    
    .container {
        padding: 0 20px 40px;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .stButton > button {
        width: 100% !important;
        padding: 16px 24px !important;
        background: #1a1a1a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        margin: 32px 0 !important;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        opacity: 0.9;
    }
    
    .project-item {
        padding: 24px 0;
        border-bottom: 1px solid rgba(0,0,0,0.1);
    }
    
    .project-item:last-child {
        border-bottom: none;
    }
    
    .project-number {
        font-size: 14px;
        color: #ff8800;
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .project-title {
        font-size: 18px;
        font-weight: 700;
        color: #ff8800;
        margin-bottom: 8px;
    }
    
    .project-category {
        display: inline-block;
        font-size: 11px;
        font-weight: 700;
        color: #ff8800;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    
    .project-description {
        font-size: 14px;
        color: #1a1a1a;
        line-height: 1.6;
        margin: 12px 0;
    }
    
    .project-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 12px;
        font-size: 12px;
        color: #1a1a1a;
    }
    
    .project-link {
        color: #ff8800;
        text-decoration: none;
        font-weight: 600;
    }
    
    .project-link:hover {
        text-decoration: underline;
    }
    
    .project-score {
        font-size: 16px;
        font-weight: 700;
        color: #ff8800;
    }
    
    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #ff8800;
        margin: 40px 0 24px 0;
    }
    
    .stats {
        text-align: center;
        padding: 40px 0;
    }
    
    .stats-number {
        font-size: 48px;
        font-weight: 700;
        color: #ff8800;
    }
    
    .stats-label {
        font-size: 14px;
        color: #ff8800;
        margin-top: 12px;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] {
        background: transparent;
    }
    
    .stTextInput > div > div > input {
        border: none !important;
        background: transparent !important;
        color: #ff8800 !important;
        font-size: 14px !important;
        padding: 0 !important;
        border-bottom: 2px solid #ff8800 !important;
        border-radius: 0 !important;
        font-weight: 600;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #ff8800 !important;
        opacity: 0.6 !important;
    }
    
    .stError, .stWarning {
        background: transparent !important;
        color: #1a1a1a !important;
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
                    <div class="project-item">
                        <div class="project-number">#{idx}</div>
                        <div class="project-category">{category}</div>
                        <div class="project-title">{name}</div>
                        <div class="project-description">{info['description']}</div>
                        <div class="project-meta">
                            <a href="{info['link']}" target="_blank" class="project-link">View</a>
                            <span>{date} • {info['source']} • Score: <span class="project-score">{vibe}</span></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="stats">
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
