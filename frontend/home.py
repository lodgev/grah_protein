import streamlit as st

def show():
    st.title("Protein-Protein Interaction Graph Analysis")
    st.subheader("Realised by: Olha ALIEINIK, Doriane BEDIER, Oleksandra KUKSA")
    st.write("Date: March 2025")

    st.markdown("---")

    st.header("Project Summary")
    st.write("""
    The goal of this project is to analyze a protein-protein interaction network 
    based on shared protein domains.
    """)

    st.markdown("---")

    st.header("Implemented Features")
    st.markdown("""
    - Protein Graph Construction
    - Search and Query System
    - Graph Visualization
    - Graph Statistics Analysis
    - Machine Learning Annotation
    - Custom Graph Upload
    """)

    st.markdown("---")

    st.header("Technologies Used")
    st.markdown("""
    - Python (pandas, networkx, scikit-learn, py2neo)
    - Neo4j
    - Streamlit
    - PyVis
    - XGBoost / RandomForest / Label Propagation
    """)
