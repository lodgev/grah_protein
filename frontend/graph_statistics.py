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
    degree_data = query.get_degree_distribution()
    query.close()

    # General Info
    st.subheader("General statistics:")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total proteins", total)
    col2.metric("Labelled proteins", labelled)
    col3.metric("Unlabelled proteins", unlabelled)

    # --- PIE CHART ---
    st.subheader("Labelled vs Unlabelled proteins:")

    color_option = st.selectbox("Choose pie Chart Color Scheme:", 
                                options=["Classic", "Dark", "Pastel"])

    colors_dict = {
        "Classic": ['#2A629A', '#FF7F3E'],
        "Dark": ['#4B0082', '#8B0000'],
        "Pastel": ['#A3C9A8', '#FFD6BA']
    }

    fig = px.pie(values=[labelled, unlabelled], 
                 names=['Labelled', 'Unlabelled'],
                 title='Labelled vs Unlabelled Proteins',
                 color_discrete_sequence=colors_dict[color_option])
    st.plotly_chart(fig)

    # --- DEGREE DISTRIBUTION ---
    st.subheader("Degree Distribution of Proteins:")

    df_degree = pd.DataFrame(degree_data)
    avg_degree = df_degree['Degree'].mean()
    max_degree = df_degree['Degree'].max()
    most_connected = df_degree.loc[df_degree['Degree'] == max_degree, 'Entry'].values[0]

    col4, col5, col6 = st.columns(3)
    col4.metric("Average Degree", f"{avg_degree:.2f}")
    col5.metric("Max Degree", max_degree)
    col6.metric("Most Connected Protein", most_connected)

    degree_count = df_degree['Degree'].value_counts().reset_index()
    degree_count.columns = ['Degree', 'Count']
    degree_count = degree_count.sort_values('Degree')

    bar_theme = st.selectbox("Bar Chart Theme:", ["Plotly", "Simple White", "Dark"])

    fig2 = px.bar(degree_count, 
                  x='Degree', y='Count', 
                  title="Protein Degree Distribution",
                  template=bar_theme.lower())
    st.plotly_chart(fig2)

    # --- ISOLATED PROTEINS ---
    st.subheader(f"Isolated Proteins: {isolated}")
    st.write("Sample of isolated proteins:")

    if isolated_list:
        df_iso = pd.DataFrame(isolated_list)
        st.dataframe(df_iso)
    else:
        st.write("No isolated proteins found.")
