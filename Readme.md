# 🧬 Protein-Protein Interaction Graph Dashboard

A **Streamlit-based web application** to visualize, explore, and analyze protein-protein interaction networks stored in **Neo4j** graph database.

---

## 🚀 Features:

- 🔍 **Protein search** by Entry ID or Protein Name.
- 🌐 **Interactive graph visualization** (powered by Cytoscape & st-link-analysis).
- 🖱 **Double-click** any protein node to expand its neighborhood.
- ⬅️ **Back button** to return to the previous graph state.
- 📊 **Graph statistics**: total proteins, labelled/unlabelled counts, isolated nodes, degree distribution.
- 🎨 **Customizable graph styles & charts.**

---

## 🧩 Technologies Used:

- **Python**, **Streamlit**
- **Neo4j** graph database
- **NetworkX**, **Pandas**
- **Py2Neo**
- **Plotly**
- **st-link-analysis** component

---

## ⚙️ Installation Instructions:

### 1️⃣ Clone Repository:

```bash
git clone https://github.com/your-repo/protein-graph-dashboard.git
cd protein-graph-dashboard
```

2️⃣ Install Dependencies:

```bash
pip install -r requirements.txt
```

3️⃣ Neo4j Database Setup:

Download & Install Neo4j Desktop

Open Neo4j Desktop and:

Create a New Project.
Inside it, create a New Local Database.
Set password to `12345678`
Start the Database!

4️⃣ Run the App:
Once Neo4j database is running:

```bash
streamlit run main.py
```

App opens in browser at `http://localhost:8501`
📊 Graph Statistics:
Total number of proteins.
Labelled Proteins (EC Number assigned).
Unlabelled Proteins.
Isolated Proteins (proteins with no connections).
Degree Distribution (number of connections per protein).
Interactive Pie & Bar Charts.
🛠 Configuration:
Neo4j Credentials:

Username: neo4j
Password: 12345678 (default)
If you need to change, modify in:

python
Копіювати
Редагувати
backend/graph_query.py:
GraphDatabase.driver(uri, auth=(user, password))
📝 Notes:
Always start Neo4j Database before running the app!
Neo4j and Streamlit communicate locally.
📂 Project Structure:
bash
Копіювати
Редагувати
/backend                 # Handles Neo4j queries and graph logic
/frontend/pages          # Streamlit pages (search, statistics, upload)
main.py                  # Streamlit entry point
requirements.txt         # Python dependencies
README.md