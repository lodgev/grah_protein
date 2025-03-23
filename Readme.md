# Protein-Protein Interaction Graph Dashboard

A **Streamlit-based web application** to visualize, explore, and analyze protein-protein interaction networks stored in **Neo4j** graph database.

---

## Features:

- **Protein search** by Entry ID or Protein Name.
- **Interactive graph visualization.**
- **Double-click** any protein node to expand its neighborhood.
- **Back button** to return to the previous graph state.
- **Graph statistics**: total proteins, labelled/unlabelled counts, isolated nodes.
- **Customizable graph styles & charts.**

---

## Technologies Used:

- **Python**, **Streamlit**
- **Neo4j** graph database
- **NetworkX**, **Pandas**
- **Py2Neo**
- **Plotly**
- **st-link-analysis** component

---

## Installation Instructions:

### 1. Clone Repository:

```bash
git clone https://github.com/lodgev/grah_protein.git 
cd grah_protein
```

### 2. Install Dependencies:

```bash
pip install -r requirements.txt
```

### 3. Neo4j Database Setup:

Download & Install Neo4j Desktop

Open Neo4j Desktop and:

Create a New Project.
Inside it, create a New Local Database.
Set password to `12345678`
Start the Database!

### 4. Run the App:
Once Neo4j database is running:

```bash
streamlit run main.py
```

App opens in browser at `http://localhost:8501`
