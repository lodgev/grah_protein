import streamlit as st
from backend.graph_query import ProteinGraphQuery
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle

def show():
    st.title("Visualize full graph")

    st.write("Displaying a sample of the full protein-protein interaction graph.")

    limit = st.slider("Number of proteins to visualize:", 50, 500, 100, step=50)

    query = ProteinGraphQuery()
    proteins, edges = query.get_full_graph(limit=limit)
    query.close()

    # Preparing data
    nodes = [{"data": {"id": data["entry"], "label": "Protein", "name": data["name"]}} for data in proteins.values()]
    edge_list = [{"data": {"id": f"{edge['source']}-{edge['target']}", 
                        "label": f"Similarity {edge['weight']:.2f}" if edge['weight'] else "", 
                        "source": edge['source'], 
                        "target": edge['target']}} for edge in edges]

    node_styles = [NodeStyle("Protein", "#FF7F3E", "name", "science")]
    edge_styles = [EdgeStyle("Similarity", caption='label', directed=False)]
    elements = {"nodes": nodes, "edges": edge_list}

    st.subheader(f"Full graph visualization ({limit} proteins)")
    st_link_analysis(elements, layout="cose", node_styles=node_styles, edge_styles=edge_styles)
