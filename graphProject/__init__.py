from flask import Flask
from py2neo import Graph, Node, Relationship

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ce50bd8fbfbeb7391c109aca88e6ff16'
db = Graph("neo4j+s://0a3c5d1b.databases.neo4j.io",
	auth = ("neo4j", "v2UQAry6AWCQwllT9HxjfLQ4CGuRGxkX_iOeGNqbZfU"))

from graphProject import nodes