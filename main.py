import streamlit as st
from frontend import home, search_protein, graph_statistics, ml_annotation, visualize_graph
from backend.data_loader import ProteinGraph

# ---------------- Load Graph On Startup -----------------
@st.cache_resource
def load_graph_once():
    pg = ProteinGraph()
    pg.load_data('backend/data/uniprotkb_AND_model_organism_9606_2025_02_07.tsv', sample_size=1000)
    pg.build_graph()
    pg.connect_neo4j()
    pg.upload_to_neo4j()
    return "Graph loaded!"

load_graph_once()

st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select Page:",
    ("Home", "Visualize graph", "Search protein", "Graph statistics", "ML annotation")
)


# Routing
if page == "Home":
    home.show()
elif page == "Visualize graph":
    visualize_graph.show()
elif page == "Search protein":
    search_protein.show()
elif page == "Graph statistics":
    graph_statistics.show()
elif page == "ML annotation":
    ml_annotation.show()