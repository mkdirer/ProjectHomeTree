# ProjectHomeTree
This project aimed to develop a web application utilizing Neo4j graph database to create a genealogy tree, which was then hosted in Render [Genealogy Tree Web Application](https://family-tree-graph-project.onrender.com/). The application allows users to add new people to the database, specify their relationships with other members, search for relations between two members, and present data in a simple visual format using a table and graph. All nodes in the database are of type "Person" and have three mandatory attributes: first name, last name, and year of birth. Optional attribute is the year of death.


Above picture shows a UML diagram of a person node and their properties and relationships.

The project is a proof of concept and is simplified and limited in scope. The assumptions include: correctness and proper format of input data, no possibility of adding people with the same name, surname, and year of birth, no consideration of gender, only one type of relationship between two nodes, limited complexity and functionality of data for demonstrating general usage of graph database, and a small number of entries in the database to maintain readability of the graph.

The application has several endpoints: home page, family list table, graph display, add member form, search relation form, remove member form, and a clean page for clearing the database.

The connection to Neo4j database was obtained using the neo4j Python library. The graph is created using the networkx module, which provides a relatively easy implementation but may not provide the most aesthetic layout.

Overall, the project is minimalist and straightforward due to its proof of concept nature.
