"""
Indian Constitution AI - Streamlit Frontend
"""
import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import time
import os
import base64
from PyPDF2 import PdfReader, PdfWriter
import io

# Fix for streamlit deployment on systems with sqlite issues
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

# Configure the page
st.set_page_config(
    page_title="Indian Constitution AI",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Updated Custom CSS for better readability
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #FF6B35;  /* Brighter orange for better contrast */
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.8rem;
        color: #004E89;  /* Darker blue for better readability */
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 600;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #E2E8F0;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .user-message {
        background-color: #EBF8FF;  /* Light blue background */
        border-left: 5px solid #004E89;
    }
    .assistant-message {
        background-color: #FFFFFF;
        border-left: 5px solid #FF6B35;
    }
    .message-content {
        display: flex;
        align-items: flex-start;
        gap: 15px;
    }
    .message-text {
        flex: 1;
        color: #2D3748;
        font-size: 16px;
        line-height: 1.6;
    }
    .message-text b {
        color: #1A365D;  /* Darker blue for usernames */
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    .avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #E2E8F0;
    }
    .timestamp {
        display: none !important;  /* Hide all timestamp elements */
    }
    .message-timestamp {
        display: none !important;  /* Hide all message timestamp elements */
    }
    .stApp {
        background-color: #FFFFFF;  /* Changed from F7FAFC to white */
    }
    .sidebar .sidebar-content {
        background-color: #FFFFFF;  /* Changed from EDF2F7 to white */
    }
    /* Style for the input box */
    .stTextInput > div > div > input {
        font-size: 16px !important;
        line-height: 1.6;
        padding: 12px 16px;
        border: 2px solid #004E89;  /* Changed border color */
        border-radius: 10px;
        background-color: #FFFFFF;  /* Explicit white background */
        color: #2D3748;  /* Dark text color for better visibility */
        width: 100%;
        margin-bottom: 0px;  /* Reduced from 10px */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);  /* Subtle shadow */
    }
    .stTextInput > div > div > input::placeholder {
        color: #718096;  /* Lighter color for placeholder text */
        opacity: 1;  /* Make sure placeholder is visible */
    }
    .stTextInput > div > div > input:focus {
        border-color: #FF6B35;  /* Orange highlight on focus */
        box-shadow: 0 0 0 2px rgba(255,107,53,0.2);  /* Subtle orange glow */
    }
    /* Style for buttons */
    .stButton > button {
        background-color: #004E89;
        color: white;
        font-weight: 600;
        padding: 12px 24px;
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        height: 100%;  /* Make button fill available height */
    }
    .stButton > button:hover {
        background-color: #003666;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* Style for the sidebar info box */
    .stAlert {
        background-color: #FFFFFF;  /* Changed from EDF2F7 to white */
        border-radius: 0.5rem;
        padding: 1rem;
    }
    /* Style for metrics */
    .stMetric {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Style for expander */
    .streamlit-expanderHeader {
        background-color: #FFFFFF;  /* Changed from F8F9FA to white */
        border-radius: 0.5rem;
        padding: 0.8rem;
        font-weight: 600;
        color: #2D3748;
        border: 1px solid #E2E8F0;  /* Added border for visibility */
    }
    /* Footer style */
    footer {
        color: #4A5568;
        font-size: 0.9rem;
        text-align: center;
        padding: 1rem;
        border-top: 1px solid #E2E8F0;
        margin-top: 2rem;
    }
    /* Sources box style */
    .sources-box {
        background-color: #EBF8FF;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 0.5rem;
        border-left: 5px solid #63B3ED;
    }
    .source-item {
        background-color: #FFFFFF;  /* Changed from F7FAFC to white */
        padding: 0.8rem;
        border-radius: 0.3rem;
        margin-bottom: 0.5rem;
        border: 1px solid #E2E8F0;
    }
    .source-title {
        font-weight: 600;
        color: #2C5282;
        margin-bottom: 0.3rem;
    }
    .source-content {
        color: #4A5568;
        font-size: 0.9rem;
        font-style: italic;
    }
    .assistant-message {
        background-color: #FFFFFF;  /* Changed from f0f0f0 to white */
        padding: 15px;
        border-radius: 15px;
        margin: 5px 0;
        border: 1px solid #E2E8F0;  /* Added border for visibility */
    }
    .message-timestamp {
        font-size: 0.8em;
        color: #666;
    }
    .debug-info {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        font-family: monospace;
    }
    /* Fix for vertical alignment in form */
    .form-container {
        display: flex;
        align-items: stretch;
    }
    .form-container > div {
        display: flex;
        align-items: center;
    }
    /* Expander content visibility improvement */
    .stExpander {
        border: 1px solid #E2E8F0;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stExpander > div {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .knowledge-graph-container {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-top: 15px;
    }
    .rag-container {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-top: 15px;
    }
    .rag-item {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-bottom: 10px;
    }
    /* PDF viewer container */
    .pdf-viewer {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 20px;
        height: 800px;
        overflow: hidden;
    }
    
    /* Source reference buttons */
    .source-reference {
        display: inline-block;
        padding: 4px 8px;
        margin: 2px;
        background-color: #EBF8FF;
        border: 1px solid #63B3ED;
        border-radius: 4px;
        color: #2C5282;
        cursor: pointer;
        font-size: 0.9em;
    }
    
    .source-reference:hover {
        background-color: #BEE3F8;
    }
    
    /* Source content container */
    .source-content-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        padding: 10px;
        margin-top: 5px;
        font-size: 0.9em;
    }
    /* PDF viewer styles */
    iframe {
        background: white;
    }
    
    /* Source button styles */
    .stButton button {
        background-color: #004E89;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .stButton button:hover {
        background-color: #003666;
    }
    
    /* Source expander styles */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar styles */
    .sidebar .sidebar-content {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'questions_asked' not in st.session_state:
    st.session_state.questions_asked = 0
if 'api_url' not in st.session_state:
    # Default to local development server with the correct endpoint path
    st.session_state.api_url = st.secrets["API_URL"]
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'debug' not in st.session_state:
    st.session_state.debug = True
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_pdf_page' not in st.session_state:
    st.session_state.current_pdf_page = 0

# Header with Indian flag colors
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown('<div class="main-header">🇮🇳 Indian Constitution AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your Expert Guide to the Constitution of India</div>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=150)
    
    # Enhanced About section
    st.markdown("""
        <div style='background: linear-gradient(135deg, #FF6B35 0%, #004E89 100%);
                    padding: 2px;
                    border-radius: 10px;'>
            <div style='background: white;
                        padding: 20px;
                        border-radius: 8px;'>
                <h2 style='color: #004E89;
                          font-size: 24px;
                          margin-bottom: 15px;
                          text-align: center;'>
                    About ConstitutionGPT
                </h2>
                <p style='color: #2D3748;
                         font-size: 16px;
                         line-height: 1.6;
                         margin-bottom: 15px;
                         text-align: justify;'>
                    Welcome to your intelligent guide to the Indian Constitution! 
                    This AI assistant uses advanced RAG (Retrieval Augmented Generation) 
                    technology to provide accurate answers directly from the 
                    constitutional text.
                </p>
                <ul style='color: #2D3748;
                          font-size: 16px;
                          line-height: 1.6;
                          margin-left: 20px;
                          margin-bottom: 15px;'>
                    <li>Constitutional Articles & Amendments</li>
                    <li>Fundamental Rights & Duties</li>
                    <li>Government Structure</li>
                    <li>Supreme Court Judgments</li>
                    <li>Current Constitutional Developments</li>
                </ul>
                <p style='color: #4A5568;
                         font-size: 14px;
                         font-style: italic;
                         text-align: center;
                         margin-top: 15px;'>
                    Ask any question about the Indian Constitution, and get accurate, detailed answers!
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.title("Settings")
    api_url = st.text_input("API URL", value=st.session_state.api_url)
    if api_url != st.session_state.api_url:
        st.session_state.api_url = api_url
    
    # Add debug mode toggle
    debug_mode = st.checkbox("Debug Mode", value=st.session_state.debug)
    if debug_mode != st.session_state.debug:
        st.session_state.debug = debug_mode
    
    # Add API status indicator
    st.subheader("API Status")
    try:
        # Get the base URL (remove everything after and including /api)
        base_url = st.session_state.api_url.split("/api")[0]
        health_url = f"{base_url}/health"
        
        if st.session_state.debug:
            st.write(f"Debug - Health check URL: {health_url}")
            
        response = requests.get(health_url, timeout=5)
        
        if st.session_state.debug:
            st.write(f"Debug - Health response status: {response.status_code}")
            
        if response.status_code == 200:
            st.success("API is online and healthy")
        else:
            st.error("API is online but reporting issues")
    except Exception as e:
        error_msg = str(e)
        st.error(f"Cannot connect to API: {error_msg}")
        
        if st.session_state.debug:
            st.write(f"Debug - Health check error: {error_msg}")
    
    # Add API test feature
    if st.session_state.debug:
        st.subheader("API Test")
        if st.button("Test API Endpoint"):
            try:
                # Get the base URL
                api_url = st.session_state.api_url
                st.write(f"Testing API endpoint: {api_url}")
                
                # Make a simple request
                response = requests.post(
                    api_url,
                    json={"question": "Hello, testing the API", "chat_history": []},
                    timeout=10
                )
                
                st.write(f"Status code: {response.status_code}")
                if response.status_code == 200:
                    st.success("API endpoint is working correctly!")
                    try:
                        st.json(response.json())
                    except:
                        st.write("Response is not JSON")
                else:
                    st.error(f"API endpoint returned status code {response.status_code}")
                    st.write(f"Response: {response.text}")
            except Exception as e:
                st.error(f"Error testing API endpoint: {str(e)}")
    
    st.title("Statistics")
    st.metric("Questions Asked", st.session_state.questions_asked)
    
    # Sample questions - Modified implementation
    st.title("Sample Questions")
    sample_questions = [
        "What are the Fundamental Rights in the Indian Constitution?",
        "Explain Article 370 and its recent developments",
        "How many amendments have been made to the Indian Constitution?",
        "What is the procedure to amend the Constitution?",
        "Explain the structure of the Indian Judiciary"
    ]
    
    # Create a unique key for each button
    for i, q in enumerate(sample_questions):
        if st.button(q, key=f"sample_q_{i}"):
            # Only process if not already processing
            if not st.session_state.processing:
                process_question(q)

# Main chat interface
st.markdown("### Chat with ConstitutionGPT")

# Display chat history with sources
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-content">
                <img src="https://www.w3schools.com/w3images/avatar2.png" class="avatar">
                <div class="message-text">
                    <b>You:</b><br>{message["content"]}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Format the bot message with sources if available
        sources_html = ""
        if message.get("sources"):
            sources_html = """
            <div class="sources-box">
                <h4>Sources from the Indian Constitution:</h4>
            """
            for source in message["sources"]:
                source_title = f"{source['type']}: {source['name']}"
                if source.get('article'):
                    source_title += f" - Article {source['article']}"
                
                sources_html += f"""
                <div class="source-item">
                    <div class="source-title">{source_title}</div>
                    <div class="source-content">{source['content']}</div>
                </div>
                """
            sources_html += "</div>"

        st.markdown(f"""
        <div class="chat-message assistant-message">
            <div class="message-content">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" class="avatar">
                <div class="message-text">
                    <b>ConstitutionGPT:</b><br>{message["content"]}
                </div>
            </div>
            {sources_html}
        </div>
        """, unsafe_allow_html=True)

# Function to handle form submission
def handle_input():
    if st.session_state.user_input and not st.session_state.processing:
        # Get the question from the input
        question = st.session_state.user_input
        
        # Process the question
        process_question(question)
        
        # Reset processing flag
        st.session_state.processing = False
        
        # Instead of directly modifying user_input, use st.rerun()
        # This will clear the input on the next run
        st.rerun()

# Function to process questions
def process_question(question):
    if not question.strip() or st.session_state.processing:
        return

    try:
        st.session_state.processing = True
        
        # Debug: Show question being processed
        if st.session_state.debug:
            with st.status("Processing your question..."):
                st.write(f"Question: {question}")
        
        # Add user message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history.append({
            "role": "user",
            "content": question,
            "timestamp": timestamp
        })
        
        # Increment questions counter
        st.session_state.questions_asked += 1
        
        # Prepare chat history for API
        api_chat_history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.chat_history[:-1]
        ]
        
        # Make API request with status indicator
        with st.status("Connecting to API...") as status:
            response = requests.post(
                st.session_state.api_url,
                json={
                    "question": question,
                    "chat_history": api_chat_history
                },
                timeout=30
            )
            
            response.raise_for_status()
            answer_data = response.json()
            
            # Add assistant response to chat history with proper formatting
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer_data.get("answer", "No answer provided"),
                "sources": answer_data.get("sources", []),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            status.update(label="Response received!", state="complete")

    except Exception as e:
        error_message = f"Error: {str(e)}"
        st.error(error_message)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    finally:
        st.session_state.processing = False
        st.rerun()  # Force a rerun to update the UI

# User input section - Using a form to control submission
st.markdown("### Ask your question")
with st.form(key='question_form', clear_on_submit=True):
    # Improved form with better alignment
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "",  # Remove label as we have the header above
            placeholder="Type your question about the Indian Constitution...",
            key="user_input"
        )
    with col2:
        # Add CSS class to container div for better alignment
        st.markdown('<div style="height: 100%; display: flex; align-items: center;">', unsafe_allow_html=True)
        submit_button = st.form_submit_button("Ask")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if submit_button and user_input:
        if not st.session_state.processing:
            process_question(user_input)

# Update the footer with better styling
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #4A5568; padding: 1rem; background-color: #FFFFFF; 
    border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 2rem;'>
        <span style='font-weight: 600; color: #2D3748;'>Powered by RAG Technology</span> | 
        <span style='color: #4A5568;'>Developed for educational purposes</span> | 
        <span style='color: #718096;'>Not legal advice</span>
    </div>
    """, 
    unsafe_allow_html=True,
    help="This tool provides information about the Indian Constitution but should not be used as a substitute for professional legal advice."
)

# Knowledge Graph section with improved visibility
with st.expander("Constitutional Knowledge Graph"):
    st.markdown("""
        <div class="knowledge-graph-container">
            <h3 style='color: #004E89; margin-bottom: 10px;'>Understanding the Knowledge Graph</h3>
            <p style='color: #2D3748; line-height: 1.6;'>
                This interactive visualization represents the complex relationships between different aspects of the Indian Constitution. 
                Here's what you're looking at:
            </p>
            <ul style='color: #2D3748; line-height: 1.6;'>
                <li><strong>Nodes (Circles):</strong> Represent major constitutional elements</li>
                <li><strong>Size:</strong> Indicates the scope and importance of each element</li>
                <li><strong>Lines:</strong> Show relationships and connections between elements</li>
                <li><strong>Colors:</strong> Group related constitutional aspects together</li>
            </ul>
            <p style='color: #2D3748; line-height: 1.6;'>
                Try hovering over the nodes to explore different aspects and their relationships!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Enhanced visualization with better colors
    nodes = pd.DataFrame({
        'id': [0, 1, 2, 3, 4, 5, 6, 7, 8],
        'name': ['Constitution', 'Fundamental Rights', 'Directive Principles', 
                'Legislature', 'Executive', 'Judiciary', 'Constitutional Bodies', 
                'Amendments', 'Emergency Provisions'],
        'group': [0, 1, 1, 2, 2, 2, 3, 4, 5]
    })
    
    edges = pd.DataFrame({
        'source': [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5],
        'target': [1, 2, 3, 4, 5, 6, 7, 8, 5, 4, 4, 5, 6],
        'value': [10, 8, 9, 9, 9, 7, 8, 6, 5, 4, 7, 8, 6]
    })
    
    # Updated color scheme with brighter colors
    color_discrete_sequence = ['#FF6B35', '#007ACC', '#05C3A7', '#9966CC', '#455A64']
    
    fig = px.scatter(nodes, 
                    x='group', 
                    y='id', 
                    size='group',
                    color='group',
                    hover_name='name',
                    title='Indian Constitution Knowledge Graph',
                    size_max=30,
                    color_discrete_sequence=color_discrete_sequence)
    
    # Enhanced edge styling
    for _, edge in edges.iterrows():
        source_node = nodes.loc[edge['source']]
        target_node = nodes.loc[edge['target']]
        fig.add_shape(
            type='line',
            x0=source_node['group'],
            y0=source_node['id'],
            x1=target_node['group'],
            y1=target_node['id'],
            line=dict(width=edge['value']/3, 
                     color='rgba(100, 100, 100, 0.5)',  # Improved visibility
                     dash='solid')  # Changed from dot to solid
        )
    
    # Improved layout
    fig.update_layout(
        showlegend=False,
        height=500,
        plot_bgcolor='rgba(255, 255, 255, 1)',  # White background
        paper_bgcolor='rgba(255, 255, 255, 1)',  # White background
        title_font_size=20,
        title_font_color='#2D3748',
        title_x=0.5,
        title_y=0.95,
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(220, 220, 220, 0.5)'  # Light grid lines
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(220, 220, 220, 0.5)'  # Light grid lines
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Add a description of RAG technology with improved visibility
with st.expander("How RAG Technology Works"):
    st.markdown("""
        <div class="rag-container">
            <h3 style='color: #004E89; margin-bottom: 15px;'>Retrieval Augmented Generation (RAG)</h3>
            
            <p style='color: #2D3748; line-height: 1.6; margin-bottom: 15px;'>
                This system uses RAG technology to provide accurate answers about the Indian Constitution. Here's how it works:
            </p>
            
            <div style='display: flex; flex-direction: column; gap: 15px;'>
                <div class="rag-item" style='border-left: 4px solid #FF6B35;'>
                    <h4 style='color: #FF6B35; margin-bottom: 10px;'>1. Knowledge Base Creation</h4>
                    <p style='color: #4A5568; line-height: 1.5;'>
                        The entire text of the Indian Constitution is processed, divided into meaningful chunks, 
                        and converted into a special format called vector embeddings that captures the meaning of the text.
                    </p>
                </div>
                
                <div class="rag-item" style='border-left: 4px solid #007ACC;'>
                    <h4 style='color: #007ACC; margin-bottom: 10px;'>2. Semantic Search</h4>
                    <p style='color: #4A5568; line-height: 1.5;'>
                        When you ask a question, the system searches for the most relevant sections of the Constitution 
                        based on meaning, not just keywords.
                    </p>
                </div>
                
                <div class="rag-item" style='border-left: 4px solid #05C3A7;'>
                    <h4 style='color: #05C3A7; margin-bottom: 10px;'>3. Contextual Response Generation</h4>
                    <p style='color: #4A5568; line-height: 1.5;'>
                        The AI uses these relevant sections as context to generate an accurate response, 
                        ensuring answers are grounded in the actual text of the Constitution.
                    </p>
                </div>
                
                <div class="rag-item" style='border-left: 4px solid #9966CC;'>
                    <h4 style='color: #9966CC; margin-bottom: 10px;'>4. Source Citation</h4>
                    <p style='color: #4A5568; line-height: 1.5;'>
                        Each answer comes with citations to the specific parts of the Constitution used, 
                        allowing you to verify the information directly.
                    </p>
                </div>
            </div>
            
            <p style='color: #2D3748; line-height: 1.6; margin-top: 20px; font-style: italic; text-align: center;'>
                This approach combines the power of AI with the accuracy of retrieving information directly from the source document.
            </p>
        </div>
    """, unsafe_allow_html=True)

# Add this function to load and display PDF
def display_pdf(pdf_path, page_number=0):
    """Display a specific page of the PDF."""
    try:
        with open(pdf_path, "rb") as f:
            pdf_reader = PdfReader(f)
            num_pages = len(pdf_reader.pages)
            
            # Ensure page number is valid
            page_number = max(0, min(page_number, num_pages - 1))
            
            # Create a new PDF with just the specified page
            writer = PdfWriter()
            writer.add_page(pdf_reader.pages[page_number])
            
            # Save to bytes
            pdf_bytes = io.BytesIO()
            writer.write(pdf_bytes)
            pdf_bytes.seek(0)
            
            # Convert to base64
            base64_pdf = base64.b64encode(pdf_bytes.read()).decode('utf-8')
            
            # Create PDF viewer
            pdf_display = f"""
                <iframe
                    src="data:application/pdf;base64,{base64_pdf}#zoom=100"
                    width="100%"
                    height="600px"
                    type="application/pdf"
                    style="border: 1px solid #ccc; border-radius: 5px;"
                >
                </iframe>
            """
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Add page navigation
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("← Previous", disabled=page_number <= 0):
                    st.session_state.current_pdf_page = page_number - 1
                    st.rerun()
            with col2:
                st.markdown(f"**Page {page_number + 1} of {num_pages}**")
            with col3:
                if st.button("Next →", disabled=page_number >= num_pages - 1):
                    st.session_state.current_pdf_page = page_number + 1
                    st.rerun()
    
    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")

# Add this function to extract page number from source
def extract_page_number(source):
    """Extract page number from source information."""
    if isinstance(source, dict):
        page_num = source.get('page_number')
        if page_num is not None:
            try:
                return int(page_num)
            except (ValueError, TypeError):
                pass
    return None

def display_chat_message(message):
    """Display a chat message with clickable sources."""
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # If this is an assistant message and has sources
        if message["role"] == "assistant" and "sources" in message:
            st.markdown("**Sources:**")
            
            # Create a container for sources
            with st.container():
                for idx, source in enumerate(message.get("sources", [])):
                    # Extract page number and article info
                    page_num = extract_page_number(source)
                    article = source.get('article', 'Unknown Article')
                    content = source.get('content', '')
                    
                    # Create an expander for each source
                    with st.expander(f"Source {idx + 1}: {article}"):
                        st.markdown(content)
                        
                        # Add a button to jump to the page in PDF
                        if page_num is not None:
                            if st.button(f"View on Page {page_num}", key=f"src_{idx}_{hash(str(source))}"):
                                st.session_state.current_pdf_page = page_num - 1
                                st.rerun()

def process_question(question):
    """Process a question and get response from the API."""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/ask",
            json={"question": question}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def main():
    """Main application function."""
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_pdf_page' not in st.session_state:
        st.session_state.current_pdf_page = 0

    # Display header
    st.markdown('<h1 class="main-header">🇮🇳 Indian Constitution AI</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Your AI Guide to the Indian Constitution</h2>', unsafe_allow_html=True)

    # Create sidebar with PDF viewer
    with st.sidebar:
        st.markdown("### Constitution Preview")
        # Adjust the path to your PDF file
        pdf_path = "20240716890312078.pdf"
        if os.path.exists(pdf_path):
            display_pdf(pdf_path, st.session_state.current_pdf_page)
        else:
            st.error(f"PDF file not found: {pdf_path}")

    # Main chat interface
    for message in st.session_state.messages:
        display_chat_message(message)

    # Chat input
    if question := st.chat_input("Ask about the Indian Constitution"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Get AI response
        response = process_question(question)
        
        if response:
            # Add assistant message with sources
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "sources": response.get("sources", [])
            })
            
            # Auto-scroll to first source page if available
            if response.get("sources"):
                first_source = response["sources"][0]
                page_num = extract_page_number(first_source)
                if page_num is not None:
                    st.session_state.current_pdf_page = page_num - 1
                    st.rerun()

if __name__ == "__main__":
    main() 