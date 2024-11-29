# HILDEGARD
_Human In the Loop Data Extraction &amp; Graphically Augmented Relation Discovery_

If you use or reference this application, please cite the following article:

Palma, C. (2024). HILDEGARD: Human-in-the-Loop Data Extraction and Graphically Augmented Relation Discovery. Journal of Computational and Cognitive Engineering, Bon View Press. https://doi.org/10.47852/bonviewJCCE42022924

A colab file presenting a light-weight version of this project can be found [here](https://github.com/Glottocrisio/HILDEGARD/blob/main/hildegard_lightweight.ipynb).

<p align="center">
  <img src="Data/hildergardlogo.png" alt="Hildegard" width="50%" />
</p>

### Requirements

- Neo4j installed locally
- Python 3.7 or higher
- Selenium web-driver installed locally

HILDEGARD is an application conceived to guide a semi-expert user in the domain of cultural heritage data management toward the creation of a lightweight knowledge graph tailored for supporting Automatic Story Generation (ASG).
For this purpose, a subset of CIDOC-CRM classes and properties is preliminarily selected to fit the domain of interest. The input is constituted
by one or more seed-heritage objects selected from a knowledge base. In our case study, they are SPARQL-queried from a Linked
Open Database for Italian Cultural Heritage. The shortest path algorithm is then run online on all couplets obtained by a combination of
the Wikipedia entities from the selected entry-seeds descriptions. The retrieved entities are subsequently linked to their related DBpediaor
YAGO-entry in the chosen language, and the relationships among them are automatically retrieved. The proposed tool addresses different
knowledge gaps and societal needs simultaneously, such as the lack of solutions tailored for narrative purposes in the cultural heritage
domain, that is, to be used in a scenario where objects belonging to the same room must be linked through a narrative, which shall not only
be coherent and informative but also engaging and interesting. The prototype, already able to generate the triples required for the following
step of the proposed general ASG pipeline, is intended to be graphically enhanced so that the end user may guide the graph expansion
interactively.

<p align="center">
  <img src="pics/hildegard6.png" alt="hildegard6"/>
</p>

After downloading the project, open the Hildegard project file.

Replace the Neo4J authentication credential with the ones of your initialized graph:

driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j","***"))


Then, run the project. You will be guided to building the graph via a simple UI as in the following.

<p align="center">
  <img src="pics/ui.png" alt="ui"/>
</p>

<p align="center">
  <img src="Data/hildergardlogo.png" alt="Hildegard" />
</p>

<p align="center">
  <img src="Data/hildergardlogo.png" alt="Hildegard" />
</p>

<p align="center">
  <img src="Data/hildergardlogo.png" alt="Hildegard" />
</p>

<p align="center">
  <img src="Data/hildergardlogo.png" alt="Hildegard" />
</p>

