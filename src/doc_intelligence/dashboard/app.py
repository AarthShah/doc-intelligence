import streamlit as st
import requests
import pandas as pd

st.title("Document Intelligence Dashboard")

st.header("Retrieval Search")
api_base_url = st.text_input("FastAPI Backend URL", value="http://localhost:8000")
query = st.text_input("Query")
top_k = st.number_input("Top K", min_value=1, max_value=50, value=5)

st.header("Evaluation Metrics")

def display_evaluation_metrics(api_url: str):
    """Fetches and displays evaluation metrics from the backend."""
    if st.button("Fetch Evaluation Results"):
        with st.spinner("Fetching evaluation results..."):
            try:
                response = requests.post(
                    f"{api_url}/evaluate"
                )
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if not results:
                        st.info("No evaluation results found.")
                    else:
                        st.success(f"Found {len(results)} evaluation sets.")
                        # Placeholder for displaying charts/tables
                        st.write("Evaluation metrics will be displayed here.")
                        st.json(results) # Display raw data for now
                else:
                    st.error(f"Error from API: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to backend: {e}")

display_evaluation_metrics(api_base_url)

if st.button("Search"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Fetching retrieval results..."):
            try:
                response = requests.post(
                    f"{api_base_url}/retrieve",
                    json={"query": query, "top_k": top_k}
                )
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if not results:
                        st.info("No documents found for this query.")
                    else:
                        st.success(f"Found {len(results)} results.")
                        table_data = []
                        for idx, item in enumerate(results, start=1):
                            table_data.append({
                                "Rank": idx,
                                "Score": item.get("score"),
                                "Content": item.get("content"),
                                "Source": item.get("source", item.get("metadata", {}).get("source", ""))
                            })
                        df = pd.DataFrame(table_data)
                        st.dataframe(df, use_container_width=True)
                else:
                    st.error(f"Error from API: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to backend: {e}")
