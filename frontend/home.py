import streamlit as st

def show():
    st.title("Protein-Protein Interaction Graph Dashboard")
    st.subheader("Realized by: Olha ALIEINIK, Doriane BEDIER, Oleksandra KUKSA")
    st.write("Date: March 2025")

    st.markdown("---")

    st.header("Project summary")
    st.write("""
    This project focuses on the construction, visualization, and analysis of a Protein-Protein Interaction (PPI) Network 
    based on domain composition similarity. Users can explore the network, search for specific proteins, 
    analyze graph statistics, and perform machine learning-based functional annotation.
    """)

    st.markdown("---")

    st.header("Implemented features")
    st.markdown("""
    - Protein graph construction
    - Search and query system 
    - Interactive graph visualization 
    - Graph statistics analysis 
    - Machine learning annotation 
    """)

    st.markdown("---")

    st.header("Technologies used")
    st.markdown("""
    - **Python** (pandas, networkx, scikit-learn, py2neo)
    - **Neo4j** Graph Database
    - **Streamlit** (Frontend dashboard)
    - **st-link-analysis** (Interactive graph component)
    - **Plotly**, **PyVis**
    - **Machine Learning Models:** XGBoost, RandomForest, Label Propagation
    """)

    st.markdown("---")

    st.info("Please ensure that the Neo4j database is running before starting the application.")
