import pandas as pd
import networkx as nx
from numpy import isnan
from datetime import date
from graphProject import db
from matplotlib.pyplot import figure



def addNewMember(firstName, lastName, born, died=float('NaN')):
	if firstName and lastName and born:
		db.run("CREATE (p: Person {firstName: $firstName, lastName: $lastName, born: $born, died: $died}) RETURN p",
			firstName = firstName,
			lastName = lastName,
			born = born,
			died = died
		)
	
def addRelation(firstPerson, secondPerson, reltype, attr=None):
	if firstPerson != secondPerson:
		if reltype in ["MARRIED", "HAS_SON", "HAS_DAUGHTER", "HAS_CHILD"]:
			db_query = "MATCH (n:Person {firstName: $firstName, lastName: $lastName, born: $born}) RETURN ID(n)"
			fmID = find_person(firstPerson)
			smID = find_person(secondPerson)

			if not fmID is None and not smID is None:
			
				if reltype == "MARRIED" and attr['since']:
					db_query = """ MATCH (p1:Person), (p2:Person) WHERE ID(p1) = $fmID AND ID(p2) = $smID MERGE (p1)-[r:MARRIED {since: $since}]->(p2) RETURN type(r) """
					return db.run(db_query, fmID = fmID, smID = smID, since = attr['since']).data()
				else:
					db_query = f""" MATCH (p1:Person), (p2:Person) WHERE ID(p1) = $fmID AND ID(p2) = $smID MERGE (p1)-[r:{reltype}]->(p2) RETURN type(r) """
					return db.run(db_query, fmID = fmID, smID = smID, ).data()
			else:
				return "ERROR: The same person"
		else: 
			return "No such members in database"
	else: 
		return "Relationship does not exist"
	
	
def addSampleData():
	members = [
		{"firstName": "Bob", "lastName": "Johnson", "born": 1935, "died": 2013},
		{"firstName": "Mary", "lastName": "Miller", "born": 1936},
		{"firstName": "Emily", "lastName": "Johnson", "born": 1964},
		{"firstName": "Rachel", "lastName": "Johnson", "born": 1968},
		{"firstName": "James", "lastName": "Johnson", "born": 1975},
		{"firstName": "Samantha", "lastName": "Johnson", "born": 1979},
		{"firstName": "William", "lastName": "Taylor", "born": 1953, "died": 2006},
		{"firstName": "Robert", "lastName": "Taylor", "born": 1990},
		{"firstName": "Joseph", "lastName": "Taylor", "born": 1990},
		{"firstName": "John", "lastName": "Edwards", "born": 1969},
		{"firstName": "Jennifer", "lastName": "Anderson", "born": 1990},
		{"firstName": "Amanda", "lastName": "Brown", "born": 1980, "died": 2016},
		{"firstName": "Elizabeth", "lastName": "Taylor", "born": 2007}
	]
	
	for person in members:
		addNewMember(*tuple(person.values()))
		
	addRelation(members[2], members[6], "MARRIED", {"since": 1983})
	addRelation(members[2], members[9], "MARRIED", {"since": 2009})
	addRelation(members[0], members[1], "MARRIED", {"since": 1964})
	addRelation(members[7], members[10], "MARRIED", {"since": 2011})
	addRelation(members[4], members[11], "MARRIED", {"since": 1999})

	addRelation(members[0], members[5], "HAS_DAUGHTER")
	addRelation(members[1], members[5], "HAS_DAUGHTER")
	addRelation(members[7], members[12], "HAS_DAUGHTER")
	addRelation(members[10], members[12], "HAS_DAUGHTER")
	addRelation(members[0], members[3], "HAS_DAUGHTER")
	addRelation(members[1], members[3], "HAS_DAUGHTER")
	addRelation(members[0], members[2], "HAS_DAUGHTER")
	addRelation(members[1], members[2], "HAS_DAUGHTER")
	
	addRelation(members[2], members[7], "HAS_SON")
	addRelation(members[6], members[7], "HAS_SON")
	addRelation(members[2], members[8], "HAS_SON")
	addRelation(members[6], members[8], "HAS_SON")
	addRelation(members[0], members[4], "HAS_SON")
	addRelation(members[1], members[4], "HAS_SON")


def find_person(person):
	db_query = "MATCH (n:Person {firstName: $firstName, lastName: $lastName, born: $born}) RETURN ID(n)"
	ID = db.run(db_query, 
	firstName = person["firstName"],
	lastName = person["lastName"],
	born  = person["born"] ).data()
	if len(ID) == 1:
		return ID[0]["ID(n)"]
	else:
		print("Such person does not exist.")
		return None

def delete_all():
    db.run("MATCH (n) DETACH DELETE n")
	

def delete(person):
	mID = find_person(person)
	if not mID is None:
		db.run("MATCH (n) WHERE ID(n) = $mID DETACH DELETE n", mID=mID)
		
def getPeopleWithNodes():
	result = db.run("MATCH (n) RETURN n").data()
	df = pd.DataFrame([ t['n'] for t in result])
	df = df.reindex(columns=['firstName', 'lastName', 'born', 'died'])
	df.died = df.died.astype('Int64')
	df.fillna(-1, inplace=True)
	df = df.sort_values(by=['born'])
	df = df.reset_index(drop=True)
	return df
	
def getPeopleWithRelations():
	db_query = """
	MATCH (a:Person)-[r]->(b) RETURN a, type(r) as type, properties(r) as properties, b
	"""
	result = db.run(db_query).data()
	df = pd.DataFrame([ t for t in result ])
	return df
	
def drawGraph():
	df = getPeopleWithNodes()
	G = nx.DiGraph()
	now = date.today().year
	for i in range(len(df)):
		if df.loc[i].died != -1:
			label = df.loc[i].firstName + '\n' + df.loc[i].lastName + '\ndied in: ' + str(df.loc[i].died) + ', aged: ' + str(df.loc[i].died - df.loc[i].born)
		else:
			label = df.loc[i].firstName + '\n' + df.loc[i].lastName + '\nage: ' + str(now - df.loc[i].born)
		G.add_node(label)
		
	df = getPeopleWithRelations()
	for i in range(len(df)):
		labels = []
		for person in ['a', 'b']:
			if not isnan(df[person][i]['died']):
				labels.append(
					df[person][i]['firstName'] + '\n' + df[person][i]['lastName'] + '\ndied in: ' + str(df[person][i]['died']) + ', aged: ' + str(df[person][i]['died'] - df[person][i]['born']))
			else:
				labels.append(
					df[person][i]['firstName'] + '\n' + df[person][i]['lastName'] + '\nage: ' + str(now - df[person][i]['born']))

		if df['properties'][i]:
			G.add_edge(labels[0], labels[1], reltype = df['type'][i] + '\n' + str(df['properties'][i]).replace('{', '').replace('}', '').replace('\'', ''),)
		else:
			G.add_edge(labels[0],
			labels[1],
			reltype = df['type'][i],)
	
	fig = figure(figsize=(14, 12))
	pos = nx.shell_layout(G, scale = 2)
	nx.draw(G, pos, node_color='#e5e619', node_shape = 'o', with_labels=True, node_size = 4500)
	labels = nx.get_edge_attributes(G, 'reltype')
	nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, label_pos=0.4, font_size = 13)
	return fig

def searchConnections(firstPerson, secondPerson):
	fmID = find_person(firstPerson)
	smID = find_person(secondPerson)

	if not fmID is None and not smID is None:
		db_query = """ MATCH path = shortestPath( (p1:Person)-[r*]-(p2:Person) ) WHERE ID(p1) = $fmID AND ID(p2) = $smID RETURN path """
		result = db.run(db_query, fmID=fmID, smID=smID).data()
		result_list = []
		if not result:
			return None
		for r in result[0]['path'].relationships:
			result_list.append(
				(f"{r.nodes[0]['firstName']} {r.nodes[0]['lastName']}", 
				type(r).__name__, 
				f"{r.nodes[1]['firstName']} {r.nodes[1]['lastName']}")
			)
		return result_list

def getGrandparents(person):
	mID = find_person(person)
	result = []
	if not mID is None:
		parents = getParents(person)
		for parent in parents:
			grandparents = getParents(parent['person'])
			for g in grandparents:
				result.append( g )
	return result


def getSiblings(person):
	mID = find_person(person)
	if not mID is None:
		db_query = """ MATCH (p1:Person)<-[:HAS_SON | :HAS_DAUGHTER]-(:Person)-[:HAS_SON | :HAS_DAUGHTER]->(p2:Person) WHERE ID(p1) = $mID RETURN DISTINCT p2 as person """
		result = db.run(db_query, mID=mID).data()
		return result

def getParents(person):
	mID = find_person(person)
	if not mID is None:
		db_query = """ MATCH (p1:Person)<-[:HAS_SON | :HAS_DAUGHTER]-(p2:Person) WHERE ID(p1) = $mID RETURN p2 as person """
		result = db.run(db_query, mID=mID).data()
		return result
