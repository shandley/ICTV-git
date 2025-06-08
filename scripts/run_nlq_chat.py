"""
Natural Language Query Chat Interface

A Streamlit-based chat interface for querying viral taxonomy using plain English.
"""

import streamlit as st
import sys
import os
from datetime import datetime
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from advanced_features.nlq_interface import NaturalLanguageQuery

# Configure Streamlit page
st.set_page_config(
    page_title="ICTV-git Natural Language Query",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for chat interface
st.markdown("""
<style>
.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
}

.user-message {
    background-color: #e3f2fd;
    margin-left: 2rem;
}

.bot-message {
    background-color: #f5f5f5;
    margin-right: 2rem;
}

.message-header {
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.message-content {
    white-space: pre-wrap;
}

.example-queries {
    background-color: #fff3e0;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

.stats-container {
    background-color: #e8f5e8;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "nlq_interface" not in st.session_state:
        # Initialize the NLQ interface
        git_repo_path = "output/git_taxonomy"
        use_openai = st.sidebar.checkbox("Use OpenAI (requires API key)", value=False)
        st.session_state.nlq_interface = NaturalLanguageQuery(
            git_repo_path=git_repo_path,
            use_openai=use_openai
        )
    
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0

def display_example_queries():
    """Display example queries to help users"""
    st.markdown("""
    <div class="example-queries">
    <h4>🔍 Example Queries</h4>
    <p>Try asking questions like:</p>
    <ul>
        <li>"What happened to bacteriophage T4 after 2020?"</li>
        <li>"Show me viruses with unstable classifications"</li>
        <li>"Which coronaviruses have changed families?"</li>
        <li>"List viruses discovered in 2023"</li>
        <li>"Find viruses similar to SARS-CoV-2"</li>
        <li>"What plant viruses infect both monocots and dicots?"</li>
        <li>"Track Tobacco mosaic virus through history"</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

def display_chat_message(message_type: str, content: str, timestamp: datetime = None):
    """Display a formatted chat message"""
    if timestamp is None:
        timestamp = datetime.now()
    
    css_class = "user-message" if message_type == "user" else "bot-message"
    icon = "👤" if message_type == "user" else "🤖"
    header = "You" if message_type == "user" else "ICTV-git Assistant"
    
    st.markdown(f"""
    <div class="chat-message {css_class}">
        <div class="message-header">
            {icon} {header} <small>({timestamp.strftime('%H:%M:%S')})</small>
        </div>
        <div class="message-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)

def process_query(query: str) -> str:
    """Process user query and return response"""
    try:
        with st.spinner("🔍 Searching taxonomy data..."):
            start_time = time.time()
            response = st.session_state.nlq_interface.query(query)
            execution_time = time.time() - start_time
            
            # Add execution time to response if not already included
            if "seconds)" not in response:
                response += f"\n\n⏱️ Query executed in {execution_time:.2f} seconds"
            
            return response
    
    except Exception as e:
        return f"❌ Sorry, I encountered an error processing your query: {str(e)}"

def display_sidebar():
    """Display sidebar with controls and statistics"""
    st.sidebar.title("🧬 ICTV-git Chat")
    
    # Query statistics
    st.sidebar.markdown("### 📊 Session Stats")
    st.sidebar.metric("Queries Processed", st.session_state.query_count)
    
    # OpenAI configuration
    st.sidebar.markdown("### ⚙️ Configuration")
    
    # Repository status
    st.sidebar.markdown("### 📁 Data Status")
    repo_path = "output/git_taxonomy"
    if os.path.exists(repo_path):
        st.sidebar.success("✅ Git taxonomy repository found")
        
        # Try to get some basic stats
        try:
            import glob
            species_files = glob.glob(f"{repo_path}/**/*.yaml", recursive=True)
            st.sidebar.info(f"📄 {len(species_files)} species files available")
        except:
            st.sidebar.info("📄 Species files available")
    else:
        st.sidebar.error("❌ Git taxonomy repository not found")
        st.sidebar.info("Please run the conversion scripts first")
    
    # Tips
    st.sidebar.markdown("### 💡 Tips")
    st.sidebar.markdown("""
    - Be specific in your queries
    - Use scientific names when possible
    - Ask about specific time periods
    - Try comparative questions
    - Ask for explanations of changes
    """)
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.experimental_rerun()

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.title("🦠 ICTV-git Natural Language Query Interface")
    st.markdown("""
    Ask questions about viral taxonomy in plain English! This AI-powered interface 
    can help you explore 20 years of ICTV classification data using natural language.
    """)
    
    # Sidebar
    display_sidebar()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display example queries if no messages yet
        if not st.session_state.messages:
            display_example_queries()
        
        # Display chat history
        for message in st.session_state.messages:
            display_chat_message(
                message_type=message["type"],
                content=message["content"],
                timestamp=message["timestamp"]
            )
        
        # Query input
        st.markdown("---")
        user_input = st.text_input(
            "💬 Ask me anything about viral taxonomy:",
            placeholder="e.g., What happened to Caudovirales?",
            key="user_input"
        )
        
        # Process query when user hits enter
        if user_input:
            # Add user message to history
            timestamp = datetime.now()
            st.session_state.messages.append({
                "type": "user",
                "content": user_input,
                "timestamp": timestamp
            })
            
            # Display user message
            display_chat_message("user", user_input, timestamp)
            
            # Process and display response
            response = process_query(user_input)
            response_timestamp = datetime.now()
            
            st.session_state.messages.append({
                "type": "bot",
                "content": response,
                "timestamp": response_timestamp
            })
            
            display_chat_message("bot", response, response_timestamp)
            
            # Update statistics
            st.session_state.query_count += 1
            
            # Clear input
            st.experimental_rerun()
    
    with col2:
        # Query insights and statistics
        st.markdown("### 📈 Query Insights")
        
        if st.session_state.messages:
            user_messages = [m for m in st.session_state.messages if m["type"] == "user"]
            
            # Recent queries
            st.markdown("**Recent Queries:**")
            for msg in user_messages[-3:]:
                st.markdown(f"• {msg['content'][:50]}...")
            
            # Query types analysis (simplified)
            query_words = " ".join([m["content"].lower() for m in user_messages])
            
            insights = []
            if "history" in query_words or "happened" in query_words:
                insights.append("🕐 History tracking")
            if "unstable" in query_words or "change" in query_words:
                insights.append("📊 Stability analysis")
            if "similar" in query_words or "like" in query_words:
                insights.append("🔍 Similarity search")
            if any(year in query_words for year in ["2020", "2021", "2022", "2023", "2024"]):
                insights.append("📅 Temporal queries")
            
            if insights:
                st.markdown("**Query Types:**")
                for insight in insights:
                    st.markdown(f"• {insight}")
        
        else:
            st.info("Start asking questions to see insights!")
        
        # System status
        st.markdown("### 🔧 System Status")
        st.success("✅ NLQ Interface Active")
        
        if hasattr(st.session_state.nlq_interface, 'parser') and st.session_state.nlq_interface.parser.use_openai:
            st.success("✅ OpenAI Enhanced")
        else:
            st.info("📝 Pattern Matching Mode")

if __name__ == "__main__":
    main()