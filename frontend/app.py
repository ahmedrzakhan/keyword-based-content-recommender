import streamlit as st
import requests
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Content Recommender",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def call_api(endpoint, method="GET", data=None):
    """Make API calls to the backend."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("🚫 Cannot connect to API. Please ensure the FastAPI server is running on localhost:8000")
        return None
    except Exception as e:
        st.error(f"Error calling API: {e}")
        return None

def display_content_card(content, show_similarity=True):
    """Display a content item as a card."""
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader(content['title'])
            st.write(f"**Author:** {content['author']}")
            st.write(f"**Category:** {content['category']} | **Difficulty:** {content['difficulty']} | **Read Time:** {content['read_time']} min")

            if show_similarity and 'similarity_score' in content:
                st.write(f"**Similarity Score:** {content['similarity_score']:.3f}")

            with st.expander("View Content"):
                st.write(content['content'])

            st.write(f"**Tags:** {', '.join(content['tags'])}")

        with col2:
            if st.button(f"Find Similar", key=f"similar_{content['id']}"):
                st.session_state.similar_content_id = content['id']
                st.rerun()

        st.divider()

def search_page():
    """Main search interface."""
    st.title("🔍 Content Recommender")
    st.write("Find relevant content using AI-powered semantic search")

    # Search input
    col1, col2 = st.columns([3, 1])

    with col1:
        query = st.text_input(
            "Search for content:",
            placeholder="e.g., machine learning algorithms, climate change, digital marketing...",
            key="search_query"
        )

    with col2:
        search_button = st.button("🔍 Search", type="primary")

    # Advanced filters
    with st.expander("🎛️ Advanced Filters"):
        col1, col2, col3 = st.columns(3)

        with col1:
            category_filter = st.selectbox(
                "Category:",
                ["All", "Technology", "Science", "Business", "Health", "Education"],
                key="category_filter"
            )

        with col2:
            difficulty_filter = st.selectbox(
                "Difficulty:",
                ["All", "Beginner", "Intermediate", "Advanced"],
                key="difficulty_filter"
            )

        with col3:
            max_results = st.slider("Max Results:", 1, 20, 10, key="max_results")
            min_similarity = st.slider("Min Similarity:", 0.0, 1.0, 0.0, 0.1, key="min_similarity")

    # Perform search
    if search_button and query:
        with st.spinner("Searching for relevant content..."):
            search_data = {
                "query": query,
                "max_results": max_results,
                "category_filter": None if category_filter == "All" else category_filter,
                "difficulty_filter": None if difficulty_filter == "All" else difficulty_filter,
                "min_similarity": min_similarity
            }

            results = call_api("/search", "POST", search_data)

            if results:
                st.success(f"Found {results['total_results']} results in {results['search_time']:.3f} seconds")

                if results['results']:
                    st.subheader("📄 Search Results")
                    for content in results['results']:
                        display_content_card(content)
                else:
                    st.info("No results found. Try adjusting your search terms or filters.")

    # Handle similar content requests
    if 'similar_content_id' in st.session_state:
        with st.spinner("Finding similar content..."):
            similar_results = call_api(f"/similar/{st.session_state.similar_content_id}")

            if similar_results and similar_results['similar_content']:
                st.subheader("🔗 Similar Content")
                for content in similar_results['similar_content']:
                    display_content_card(content)
            else:
                st.info("No similar content found.")

        # Clear the session state
        del st.session_state.similar_content_id

def analytics_page():
    """Analytics dashboard."""
    st.title("📊 Analytics Dashboard")

    # Get stats from API
    stats = call_api("/stats")

    if not stats:
        st.error("Failed to load analytics data")
        return

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Content", stats['total_content'])

    with col2:
        st.metric("Total Searches", stats['total_searches'])

    with col3:
        st.metric("Avg Search Time", f"{stats['average_search_time']:.3f}s")

    with col4:
        st.metric("Categories", len(stats['categories']))

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Category distribution
        if stats['categories']:
            fig_categories = px.pie(
                values=list(stats['categories'].values()),
                names=list(stats['categories'].keys()),
                title="Content Distribution by Category"
            )
            st.plotly_chart(fig_categories, use_container_width=True)

    with col2:
        # Popular queries
        if stats['popular_queries']:
            queries_df = pd.DataFrame(stats['popular_queries'])
            fig_queries = px.bar(
                queries_df,
                x='count',
                y='query',
                orientation='h',
                title="Popular Search Queries"
            )
            fig_queries.update_layout(height=400)
            st.plotly_chart(fig_queries, use_container_width=True)
        else:
            st.info("No search queries yet")

def admin_page():
    """Admin panel for content management."""
    st.title("⚙️ Admin Panel")

    # Add new content
    st.subheader("➕ Add New Content")

    with st.form("add_content_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Title *")
            author = st.text_input("Author *")
            category = st.selectbox("Category *", ["Technology", "Science", "Business", "Health", "Education"])
            difficulty = st.selectbox("Difficulty *", ["Beginner", "Intermediate", "Advanced"])

        with col2:
            read_time = st.number_input("Read Time (minutes) *", min_value=1, max_value=60, value=5)
            tags_input = st.text_input("Tags (comma-separated) *", placeholder="tag1, tag2, tag3")

        content = st.text_area("Content *", height=200, placeholder="Enter the main content here...")

        submitted = st.form_submit_button("Add Content", type="primary")

        if submitted:
            if title and author and content and tags_input:
                tags = [tag.strip() for tag in tags_input.split(",")]

                content_data = {
                    "title": title,
                    "content": content,
                    "category": category,
                    "tags": tags,
                    "difficulty": difficulty,
                    "read_time": read_time,
                    "author": author
                }

                with st.spinner("Adding content..."):
                    result = call_api("/add-content", "POST", content_data)

                if result:
                    st.success(f"✅ Content added successfully! ID: {result['content_id']}")
                    st.rerun()
            else:
                st.error("Please fill in all required fields")

    st.divider()

    # Database status
    st.subheader("🗄️ Database Status")

    health = call_api("/health")

    if health:
        col1, col2 = st.columns(2)

        with col1:
            st.write("**API Status:**", "🟢 Healthy" if health['status'] == 'healthy' else "🔴 Unhealthy")
            st.write("**Database Connected:**", "✅ Yes" if health['database']['connected'] else "❌ No")

        with col2:
            st.write("**Total Content:**", health['database']['total_content'])
            st.write("**Last Updated:**", health['timestamp'])

def main():
    """Main application."""
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🔍 Search", "📊 Analytics", "⚙️ Admin Panel"]
    )

    # API status check
    health = call_api("/health")
    if health and health['status'] == 'healthy':
        st.sidebar.success("🟢 API Connected")
    else:
        st.sidebar.error("🔴 API Disconnected")
        st.sidebar.write("Make sure the FastAPI server is running on localhost:8000")

    # Page routing
    if page == "🔍 Search":
        search_page()
    elif page == "📊 Analytics":
        analytics_page()
    elif page == "⚙️ Admin Panel":
        admin_page()

    # Footer
    st.sidebar.divider()
    st.sidebar.write("**Content Recommender System**")
    st.sidebar.write("AI-powered semantic search")
    st.sidebar.write("Built with FastAPI, ChromaDB & Streamlit")

if __name__ == "__main__":
    main()