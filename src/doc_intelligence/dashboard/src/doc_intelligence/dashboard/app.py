import streamlit as st

def main():
    """Main function for the Streamlit dashboard."""
    st.set_page_config(page_title="Document Intelligence Dashboard", layout="wide")
    st.title("Document Intelligence Dashboard")

    st.sidebar.header("Navigation")
    selected_section = st.sidebar.radio("Go to", ["Retrieval Results", "Evaluation Metrics"])

    if selected_section == "Retrieval Results":
        st.header("Retrieval Results")
        st.write("This section will display the retrieval results.")
        # Placeholder for retrieval results visualization
    elif selected_section == "Evaluation Metrics":
        st.header("Evaluation Metrics")
        st.write("This section will display the evaluation metrics.")
        # Placeholder for evaluation metrics visualization

if __name__ == "__main__":
    main()
