import streamlit as st
from backend.graph_query import ProteinGraphQuery
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import pandas as pd

def show():
    st.title("Search protein")

    st.write("You can search by **Entry ID**, **Protein Name**, or both.")

    entry_id = st.text_input("Search by Entry ID:")
    protein_name = st.text_input("Search by Protein Name (Full):")

    if st.button("Search"):
        query = ProteinGraphQuery()
        data = query.search_protein(entry_id=entry_id if entry_id else None,
                                    protein_name=protein_name if protein_name else None)
        query.close()

        if data:
            st.subheader("Protein Info:")
            st.write(f"**ID:** {data['protein']['entry']}")
            st.write(f"**Name:** {data['protein']['name']}")
            st.write(f"**Gene Names:** {data['protein']['gene_names']}")
            st.write(f"**Function (EC):** {data['protein']['function']}")

            # Neighbors Tables
            st.subheader("Direct Neighbors:")
            df_neighbors = pd.DataFrame(data['direct_neighbors'])
            if not df_neighbors.empty:
                st.dataframe(df_neighbors)
            else:
                st.write("No direct neighbors found.")

            st.subheader("Second-Level Neighbors:")
            df_second = pd.DataFrame(data['second_neighbors'])
            if not df_second.empty:
                st.dataframe(df_second)
            else:
                st.write("No second-level neighbors found.")

            # --- GRAPH VISUALIZATION ---

            st.subheader("Graph Visualization:")

            nodes = []
            edges = []

            # Add main protein node
            nodes.append({
                "data": {"id": data['protein']['entry'], "label": "Protein", "name": data['protein']['name']}
            })

            # Add direct neighbors nodes and edges
            for neighbor in data['direct_neighbors']:
                nodes.append({
                    "data": {"id": neighbor['entry'], "label": "Protein", "name": neighbor['name']}
                })
                edges.append({
                    "data": {"id": f"{data['protein']['entry']}-{neighbor['entry']}",
                             "label": "Direct Neighbor",
                             "source": data['protein']['entry'],
                             "target": neighbor['entry']}
                })

            # Add second neighbors nodes
            for neighbor in data['second_neighbors']:
                nodes.append({
                    "data": {"id": neighbor['entry'], "label": "Protein", "name": neighbor['name']}
                })

            # Add edges between neighbors and second neighbors
            for rel in data['second_edges']:
                edges.append({
                    "data": {"id": f"{rel['source']}-{rel['target']}",
                            "label": f"Similarity {rel['weight']:.2f}",
                            "source": rel['source'],
                            "target": rel['target']}
                })

            # Set styles
            node_styles = [NodeStyle("Protein", "#2A629A", "name", "science")]
            edge_styles = [EdgeStyle("Direct Neighbor", caption='label', directed=False),
                        EdgeStyle("Similarity", caption='label', directed=False)]

            elements = {"nodes": nodes, "edges": edges}

            # Visualize
            st_link_analysis(elements, layout="cose", node_styles=node_styles, edge_styles=edge_styles)

        else:
            st.warning("No matching protein found.")
            
        

