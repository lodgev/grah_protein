import streamlit as st
from backend.graph_query import ProteinGraphQuery
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import pandas as pd


COMPONENT_KEY = "PROTEIN_GRAPH"

def show():
    st.title("Search protein")

    st.write("You can search by **Entry ID**, **Protein Name**, or both.")

    # --- INPUT ---
    entry_id = st.text_input("Search by entry ID:")
    protein_name = st.text_input("Search by protein name (Full):")
    protein_key = st.text_input("Search by keywords:")

    # --- Search BUTTON ---
    if st.button("Search"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()


    if 'current_nodes' in st.session_state:
        # --- BACK BUTTON ---
        if 'graph_history' not in st.session_state:
            st.session_state.graph_history = []

        if st.session_state.graph_history:
            if st.button("Go back"):
                last_graph = st.session_state.graph_history.pop()
                st.session_state.current_nodes = last_graph["nodes"]
                st.session_state.current_edges = last_graph["edges"]
                st.session_state.back_pressed = True 
                st.experimental_rerun()


        # --- GRAPH VISUALIZATION ---
        node_styles = [NodeStyle("Protein", "#2A629A", "name", "science")]
        edge_styles = [EdgeStyle("Direct Neighbor", caption='label', directed=False),
                    EdgeStyle("Similarity", caption='label', directed=False)]

        elements = {
            "nodes": st.session_state.current_nodes,
            "edges": st.session_state.current_edges
        }

        st.subheader("Graph Visualization:")
        event = st_link_analysis(
            elements,
            layout="cose",
            node_styles=node_styles,
            edge_styles=edge_styles,
            node_actions=['expand'],
            key=COMPONENT_KEY,
            height=700
        )

        # --- DOUBLE CLICK EVENT ---
        if event and event.get("action") == "expand":
            selected_node = event["data"]["node_ids"][0]
            st.info(f"Double Clicked Node: {selected_node}")
            

            st.session_state.graph_history.append({
                "nodes": st.session_state.current_nodes.copy(),
                "edges": st.session_state.current_edges.copy()
            })
            
            st.session_state.current_nodes = []
            st.session_state.current_edges = []


            query = ProteinGraphQuery()
            sub_data = query.get_neighbors_by_id(selected_node)
            query.close()

            # + nodes
            st.session_state.current_nodes.append({
                "data": {"id": sub_data['protein']['entry'], "label": "Protein", "name": sub_data['protein']['name']}
            })

            # + neighbors
            for neighbor in sub_data['neighbors']:
                st.session_state.current_nodes.append({
                    "data": {"id": neighbor['entry'], "label": "Protein", "name": neighbor['name']}
                })

            # + edges
            for rel in sub_data['edges']:
                st.session_state.current_edges.append({
                    "data": {"id": f"{rel['source']}-{rel['target']}",
                            "label": f"Similarity {rel['weight']:.2f}",
                            "source": rel['source'],
                            "target": rel['target']}}
                )

            st.experimental_rerun()

    # --- INITIAL LOAD ---
    elif (entry_id or protein_name or protein_key) and not st.session_state.get('back_pressed'):
        query = ProteinGraphQuery()
        data = query.search_protein(entry_id=entry_id if entry_id else None,
                                    protein_name=protein_name if protein_name else None,
                                    protein_key=protein_key if protein_key else None)
        query.close()

        if data:
            nodes = []
            edges = []

            nodes.append({
                "data": {"id": data['protein']['entry'], "label": "Protein", "name": data['protein']['name']}
            })

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

            for neighbor in data['second_neighbors']:
                nodes.append({
                    "data": {"id": neighbor['entry'], "label": "Protein", "name": neighbor['name']}
                })

            for rel in data['second_edges']:
                edges.append({
                    "data": {"id": f"{rel['source']}-{rel['target']}",
                                "label": f"Similarity {rel['weight']:.2f}",
                                "source": rel['source'],
                                "target": rel['target']}
                })


            st.session_state.current_nodes = nodes.copy()
            st.session_state.current_edges = edges.copy()
            st.experimental_rerun()
        else:
            st.warning("No matching protein found.")