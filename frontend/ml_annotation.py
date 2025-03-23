import streamlit as st
from backend.graph_query import ProteinGraphQuery  # твій клас з усіма запитами

def show():
    st.title("Protein EC annotation tool")

    entry_id = st.text_input("Enter protein entry ID")
    
    if "predict_clicked" not in st.session_state:
        st.session_state.predict_clicked = False
    if "top_n_value" not in st.session_state:
        st.session_state.top_n_value = 3

    if entry_id:
        query = ProteinGraphQuery() 

        # --- GET PROTEIN INFO ---
        with query.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Protein {entry: $entry})
                RETURN p.entry AS entry, p.entry_name AS name, p.protein_names AS description, 
                    p.ec_number AS ec_number, p.ec_predictions AS predictions
                """,
                entry=entry_id
            )
            protein = result.single()

        if protein:
            st.subheader("Protein information")
            st.write(f"**Entry:** {protein['entry']}")
            st.write(f"**Name:** {protein['name']}")
            st.write(f"**Description:** {protein['description']}")
            st.write(f"**EC Number:** {protein['ec_number']}")

            # --- IF NO EC NUMBER ---
            if not protein['ec_number']:
                st.warning("No EC Number available. You can run prediction.")

                top_n = st.slider("Select top N predictions", min_value=1, max_value=10, value=st.session_state.top_n_value)
                st.session_state.top_n_value = top_n

                if st.button("Predict EC Numbers"):
                    st.session_state.predict_clicked = True

                # --- PERFORM PREDICTION ---
                if st.session_state.predict_clicked:
                    with query.driver.session() as session:
                        result = session.run(
                            """
                            MATCH (p:Protein {entry: $entry_id})-[r:SIMILARITY]-(neighbor)
                            WHERE r.weight >= $threshold AND neighbor.ec_number IS NOT NULL
                            RETURN neighbor.ec_number AS ec, r.weight AS weight
                            """,
                            entry_id=entry_id, threshold=0.2
                        )
                        from collections import defaultdict
                        ec_weights = defaultdict(float)
                        for record in result:
                            ec_raw = record["ec"]
                            weight = record["weight"]
                            ec_list = [ec.strip() for ec in ec_raw.split(';')]
                            for ec in ec_list:
                                ec_weights[ec] += weight
                        filtered_ecs = [(ec, weight) for ec, weight in ec_weights.items() if weight >= 0.1]
                        sorted_ecs = sorted(filtered_ecs, key=lambda x: x[1], reverse=True)
                        top_ecs = sorted_ecs[:st.session_state.top_n_value]

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
                    st.subheader("Existing predictions")
                    st.write(protein['predictions'])

        else:
            st.error("Protein not found in the graph.")

        query.close()  
