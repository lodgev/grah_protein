import streamlit as st
from backend.graph_query import ProteinGraphQuery
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show():
    st.title("Graph statistics")

    query = ProteinGraphQuery()

    # General Stats
    total = query.get_total_proteins()
    labelled, unlabelled = query.get_labelled_unlabelled()
    isolated = query.get_isolated_proteins_count()
    isolated_list = query.get_isolated_proteins_list()
    query.close()

    # General Info
    st.subheader("General statistics:")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total proteins", total)
    col2.metric("Labelled proteins", labelled)
    col3.metric("Unlabelled proteins", unlabelled)

    # --- PIE CHART ---
    st.subheader("Labelled vs Unlabelled proteins:")

    fig = px.pie(values=[labelled, unlabelled], 
                names=['Labelled', 'Unlabelled'],
                title='Labelled vs Unlabelled Proteins',
                color_discrete_sequence=['#2A629A', '#FF7F3E'])
    st.plotly_chart(fig)


    # --- ISOLATED PROTEINS ---
    st.subheader(f"Isolated proteins: {isolated}")
    st.write("Sample of isolated proteins:")

    if isolated_list:
        df_iso = pd.DataFrame(isolated_list)
        st.dataframe(df_iso)
    else:
        st.write("No isolated proteins found.")
