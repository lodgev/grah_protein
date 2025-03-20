import streamlit as st
from neo4j import GraphDatabase

# Neo4j connection settings
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678")

driver = GraphDatabase.driver(URI, auth=AUTH)

# Query functions
def search_protein(tx, search_term):
    query = """
    MATCH (p:Protein)
    WHERE toLower(p.entry) CONTAINS toLower($term)
       OR toLower(p.entry_name) CONTAINS toLower($term)
       OR toLower(p.protein_names) CONTAINS toLower($term)
    RETURN p.entry, p.entry_name, p.protein_names LIMIT 10
    """
    return [record.data() for record in tx.run(query, term=search_term)]

def get_protein_neighborhood(tx, entry_id):
    query = """
    MATCH (p:Protein {entry: $entry_id})-[r*1..2]-(n)
    RETURN DISTINCT n.entry AS neighbor_entry
    LIMIT 50
    """
    return [record['neighbor_entry'] for record in tx.run(query, entry_id=entry_id)]

def get_label_stats(tx):
    query = """
    MATCH (p:Protein)
    RETURN COUNT(p) AS total,
           SUM(CASE WHEN p.ec_number IS NOT NULL THEN 1 ELSE 0 END) AS labeled,
           SUM(CASE WHEN p.ec_number IS NULL THEN 1 ELSE 0 END) AS unlabeled
    """
    return tx.run(query).single()

def get_isolated_nodes(tx):
    query = """
    MATCH (p:Protein)
    WHERE NOT (p)--()
    RETURN COUNT(p) AS isolated_proteins
    """
    return tx.run(query).single()

def get_predicted_ecs(tx):
    query = """
    MATCH (p:Protein)
    WHERE p.ec_predictions IS NOT NULL
    RETURN p.entry, p.ec_predictions LIMIT 20
    """
    return [record.data() for record in tx.run(query)]

def filter_ec_predictions_by_prefix(tx, prefix):
    query = """
    MATCH (p:Protein)
    WHERE ANY(ec IN p.ec_predictions WHERE ec STARTS WITH $prefix)
    RETURN p.entry, p.ec_predictions LIMIT 20
    """
    return [record.data() for record in tx.run(query, prefix=prefix)]

# Streamlit UI
st.title("Protein Graph Dashboard")

menu = st.sidebar.selectbox("Select Action", [
    "Search Protein", "Protein Neighborhood", "Label Statistics",
    "Isolated Proteins", "Predicted EC Numbers", "Filter EC by Level"
])

with driver.session() as session:
    if menu == "Search Protein":
        term = st.text_input("Search by ID, Name or Description")
        if term:
            results = session.execute_read(search_protein, term)
            st.write(results)

    elif menu == "Protein Neighborhood":
        entry = st.text_input("Enter Protein Entry ID")
        if entry:
            neighbors = session.execute_read(get_protein_neighborhood, entry)
            st.write(neighbors)

    elif menu == "Label Statistics":
        stats = session.execute_read(get_label_stats)
        st.write({"Total": stats['total'], "Labeled": stats['labeled'], "Unlabeled": stats['unlabeled']})

    elif menu == "Isolated Proteins":
        iso = session.execute_read(get_isolated_nodes)
        st.write({"Isolated Proteins": iso['isolated_proteins']})

    elif menu == "Predicted EC Numbers":
        predictions = session.execute_read(get_predicted_ecs)
        st.write(predictions)

    elif menu == "Filter EC by Level":
        level_prefix = st.text_input("Enter EC prefix (e.g. 2.7)")
        if level_prefix:
            filtered = session.execute_read(filter_ec_predictions_by_prefix, level_prefix)
            st.write(filtered)

driver.close()
