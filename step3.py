from neo4j import GraphDatabase
import random
from collections import defaultdict

# Neo4j connection settings
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678")

# Connect to Neo4j
driver = GraphDatabase.driver(URI, auth=AUTH)


# Select test proteins: labeled proteins to hide their labels for validation
def select_test_proteins(tx, sample_size=100):
    query = """
    MATCH (p:Protein)
    WHERE p.ec_number IS NOT NULL
    RETURN p.entry AS entry, p.ec_number AS ec
    LIMIT $limit
    """
    result = tx.run(query, limit=sample_size)
    return [(record["entry"], record["ec"]) for record in result]


# Temporarily remove EC numbers from test proteins
def remove_labels(tx, test_entries):
    for entry in test_entries:
        tx.run("MATCH (p:Protein {entry: $entry}) SET p.true_ec = p.ec_number, p.ec_number = NULL", entry=entry)


# Restore original EC numbers after testing
def restore_labels(tx):
    tx.run("MATCH (p:Protein) WHERE p.true_ec IS NOT NULL SET p.ec_number = p.true_ec REMOVE p.true_ec")


# Perform label propagation and collect predicted labels
def annotate_protein(tx, entry_id, similarity_threshold=0.2):
    query = """
    MATCH (p:Protein {entry: $entry_id})-[r:SIMILARITY]-(neighbor)
    WHERE r.weight >= $threshold AND neighbor.ec_number IS NOT NULL
    RETURN neighbor.ec_number AS ec, r.weight AS weight
    """
    result = tx.run(query, entry_id=entry_id, threshold=similarity_threshold)
    ec_weights = defaultdict(float)
    for record in result:
        ec_weights[record["ec"]] += record["weight"]
    if ec_weights:
        return max(ec_weights, key=ec_weights.get)
    return None


# Run validation test
with driver.session() as session:
    test_proteins = session.execute_read(select_test_proteins, sample_size=100)
    session.execute_write(remove_labels, [entry for entry, _ in test_proteins])

    TP = 0
    P = 0
    T = 0

    for entry, true_ec in test_proteins:
        predicted_ec = session.execute_read(annotate_protein, entry)
        if predicted_ec:
            P += 1
            if predicted_ec == true_ec:
                TP += 1
        if true_ec:
            T += 1

    precision = TP / P if P else 0
    recall = TP / T if T else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    coverage = P / len(test_proteins)

    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1:.2f}")
    print(f"Coverage: {coverage:.2f}")

    session.execute_write(restore_labels)

driver.close()
