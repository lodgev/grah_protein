import streamlit as st
from neo4j import GraphDatabase
from collections import defaultdict

# Neo4j connection settings
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678")

driver = GraphDatabase.driver(URI, auth=AUTH)

# Query functions
def get_protein_info(tx, entry_id):
    query = """
    MATCH (p:Protein {entry: $entry})
    RETURN p.entry AS entry, p.entry_name AS name, p.protein_names AS description, p.ec_number AS ec_number,
           p.ec_predictions AS predictions
    """
    result = tx.run(query, entry=entry_id)
    return result.single()

def annotate_protein_multilabel(tx, entry_id, similarity_threshold=0.2, top_n=5, min_weight=0.0):
    query = """
    MATCH (p:Protein {entry: $entry_id})-[r:SIMILARITY]-(neighbor)
    WHERE r.weight >= $threshold AND neighbor.ec_number IS NOT NULL
    RETURN neighbor.ec_number AS ec, r.weight AS weight
    """
    result = tx.run(query, entry_id=entry_id, threshold=similarity_threshold)
    ec_weights = defaultdict(float)
    for record in result:
        ec_raw = record["ec"]
        weight = record["weight"]
        ec_list = [ec.strip() for ec in ec_raw.split(';')]
        for ec in ec_list:
            ec_weights[ec] += weight

    filtered_ecs = [(ec, weight) for ec, weight in ec_weights.items() if weight >= min_weight]
    sorted_ecs = sorted(filtered_ecs, key=lambda x: x[1], reverse=True)
    top_ecs = sorted_ecs[:top_n]
    return top_ecs

# Streamlit UI
st.title("Protein EC Annotation Tool")

entry_id = st.text_input("Enter Protein Entry ID")

if entry_id:
    with driver.session() as session:
        protein = session.execute_read(get_protein_info, entry_id)

        if protein:
            st.subheader("Protein Information")
            st.write(f"Entry: {protein['entry']}")
            st.write(f"Name: {protein['name']}")
            st.write(f"Description: {protein['description']}")
            st.write(f"EC Number: {protein['ec_number']}")

            if not protein['ec_number']:
                st.warning("No EC Number available. You can run prediction.")

                if st.button("Predict EC Numbers"):
                    top_n = st.slider("Select Top N Predictions", min_value=1, max_value=10, value=3)
                    with driver.session() as session:
                        top_ecs = session.execute_read(annotate_protein_multilabel, entry_id, 0.2, top_n, 0.1)
                        if top_ecs:
                            st.subheader("Top-N Predicted EC Numbers")
                            ec_list = [ec for ec, _ in top_ecs]
                            weight_list = [round(weight, 4) for _, weight in top_ecs]
                            st.table({"EC Number": ec_list, "Weight": weight_list})
                        else:
                            st.info("No predictions available for this protein.")
            else:
                st.success("Protein already has an EC annotation.")
                if protein['predictions']:
                    st.subheader("Existing Predictions")
                    st.write(protein['predictions'])
        else:
            st.error("Protein not found in the graph.")

driver.close()
