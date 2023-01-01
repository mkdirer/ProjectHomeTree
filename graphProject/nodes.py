from graphProject import app
from graphProject.databaseMethods import *
from graphProject.templates import AddMemberForm, FindRelationsForm, RemoveForm, CleanDatabaseForm
from flask import render_template, url_for, flash, redirect, Response, request
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io


@app.route("/", methods=['GET', 'POST'])
@app.route("/home")
def home():
	return render_template(
		'home.html', 
		title='Genealogical Tree / Home'
	)

@app.route("/clean", methods=['GET', 'POST'])
def clean():
	form = CleanDatabaseForm()
	if request.method == "POST":
		if not 'clean_option' in request.form.keys():
			flash("You must select one of the clean options.", 'warning')
		else:
			if request.form['clean_option'] == 'delete':
				try:
					delete_all()
					flash("All data has been successfully deleted.", 'success')
				except Exception as e:
					print("Something went wrong:", e)
					flash("Operation failed. Try again.", 'warning')
			elif request.form['clean_option'] == 'reload':
				try:
					delete_all()
					addSampleData()
					flash("All data has been successfully reloaded.", 'success')
				except Exception as e:
					print("Something went wrong:", e)
					flash("Operation failed. Try again.", 'danger')
	return render_template(
		'clean.html', 
		title='Genealogical Tree / Clean',
		form=form
	)

@app.route("/familyList")
def familyList():
	df = getPeopleWithNodes()
	return render_template('familyList.html', 
		title='Genealogical Tree / Family List',
		mytable=df
	) 

@app.route("/graph.png")
def graph():
	fig = drawGraph()
	output = io.BytesIO()
	FigureCanvas(fig).print_png(output)
	
	response = Response(output.getvalue(), mimetype='image/png')
	return response

@app.route("/addMember", methods=['GET', 'POST'])
def addMember():
	df = getPeopleWithNodes()
	options = [
		(f"{df.loc[i].firstName},{df.loc[i].lastName},{df.loc[i].born}", 
		f"{df.loc[i].firstName} {df.loc[i].lastName}, born in {df.loc[i].born}") 
		for i in range(len(df))
	]
	form = AddMemberForm()
	if request.method == "POST":
		if form.validate_on_submit():
			print(request.form)
			person = f"{request.form['firstMemberName']},{request.form['LastMemberName']},{request.form['birthMemberYear']}"
			if person in [p[0] for p in options]:
				person = person.split(',')
				flash(f"{person[0]} {person[1]} born in {person[2]} is already in the databse.", 'danger')
				return render_template('addMember.html', 
					title='Genealogical Tree / Add Member', 
					form=form,
					options=options
				)
			elif request.form['memberFirstParent'] == request.form['memberSecondParent'] and \
				(request.form['memberFirstParent'] or request.form['memberSecondParent']):
				person = request.form['memberFirstParent'].split(',')
				flash(f"You cannot choose {person[0]} {person[1]} as both parents.", 'warning')
				return render_template('addMember.html', 
					title='Genealogical Tree / Add Member', 
					form=form,
					options=options
				)
			elif request.form['marriageNewMember'] and \
				(request.form['memberFirstParent'] == request.form['marriageNewMember'] or \
					request.form['memberSecondParent'] == request.form['marriageNewMember']):
					person = request.form['marriageNewMember'].split(',')
					flash(f"You cannot choose {person[0]} {person[1]} as both parent and marriageNewMember.", 'warning')
					return render_template('addMember.html', 
						title='Genealogical Tree / Add Member', 
						form=form,
						options=options
					)

			if request.form['marriageNewMember']:
				if not request.form['marriageMemberYear']:
					flash(f"You need to pass year of the marriage.", 'warning')
					return render_template('addMember.html', 
						title='Genealogical Tree / Add Member', 
						form=form,
						options=options
					)
			
			firstPerson = {
				"firstName": form.firstMemberName.data, 
				"lastName": form.LastMemberName.data, 
				"born": int(form.birthMemberYear.data)
			}

			if form.deathMemberYear.data:
				addNewMember(
					firstPerson['firstName'], 
					firstPerson['lastName'], 
					firstPerson['born'],
					form.deathMemberYear.data
				)
			else:
				addNewMember(
					firstPerson['firstName'], 
					firstPerson['lastName'], 
					firstPerson['born']
				)

			if request.form['marriageNewMember'] and request.form['marriageMemberYear']:
				marriageNewMember = request.form['marriageNewMember'].split(',')
				marriageNewMember = {"firstName": marriageNewMember[0], "lastName": marriageNewMember[1], "born": int(marriageNewMember[2])}
				addRelation(firstPerson, marriageNewMember, "MARRIED", 
					{"since": int(request.form['marriageMemberYear'])}
				)

			if request.form['memberFirstParent']:
				memberFirstParent = request.form['memberFirstParent'].split(',')
				memberFirstParent = {"firstName": memberFirstParent[0], "lastName": memberFirstParent[1], "born": int(memberFirstParent[2])}
				addRelation(memberFirstParent, firstPerson, "HAS_CHILD")
			
			if request.form['memberSecondParent']:
				memberSecondParent = request.form['memberSecondParent'].split(',')
				memberSecondParent = {"firstName": memberSecondParent[0], "lastName": memberSecondParent[1], "born": int(memberSecondParent[2])}
				addRelation(memberSecondParent, firstPerson, "HAS_CHILD")

			flash(f"Person {form.firstMemberName.data} {form.LastMemberName.data} " + \
				"has been successfully inserted to database.", 'success')
			return redirect(url_for('home'))
	return render_template('addMember.html', 
		title='Genealogical Tree / Add Member', 
		form=form,
		options=options
	)

@app.route("/removeMember", methods=['GET', 'POST'])
def removeMember():
	form = RemoveForm()
	df = getPeopleWithNodes()
	options = [
		(f"{df.loc[i].firstName},{df.loc[i].lastName},{df.loc[i].born}", 
		f"{df.loc[i].firstName} {df.loc[i].lastName}, born in {df.loc[i].born}") 
		for i in range(len(df))
	]
	if request.method == "POST":
		if not request.form['firstPerson']:
			flash(f"You have to choose someone.", 'warning')
			return render_template('removeMember.html', 
				title='Genealogical Tree / Remove Member',
				form=form,
				options=options
			)
		else:
			try:
				firstPerson = request.form['firstPerson'].split(',')
				firstPerson = {"firstName": firstPerson[0], "lastName": firstPerson[1], "born": int(firstPerson[2])}
				delete(firstPerson)
				flash("Person has been succcessfully removed.", 'success')
			except Exception as e:
				print("Something went wrong:", e)
				flash("Operation failed. Try again.", 'danger')
	return render_template('removeMember.html', 
		title='Genealogical Tree / Remove Member',
		form=form,
		options=options
	)

@app.route("/searchRelation", methods=['GET', 'POST'])
def searchRelation():
	form = FindRelationsForm()
	df = getPeopleWithNodes()
	options = [
		(f"{df.loc[i].firstName},{df.loc[i].lastName},{df.loc[i].born}", 
		f"{df.loc[i].firstName} {df.loc[i].lastName}, born in {df.loc[i].born}") 
		for i in range(len(df))
	]
	if request.method == "POST":
		if request.form['firstPerson'] == request.form['secondPerson'] and \
			(request.form['firstPerson'] or request.form['secondPerson']):
			flash(f"You cannot choose the same person.", 'warning')
			return render_template('searchRelation.html', 
				title='Genealogical Tree / Search Relations',
				form=form,
				options=options,
				results=None
			)
		elif not request.form['firstPerson'] or not request.form['secondPerson']:
			flash(f"You have to choose two different members.", 'warning')
			return render_template('searchRelation.html', 
				title='Genealogical Tree / Search Relations',
				form=form,
				options=options,
				results=None
			)

		try:
			firstPerson = request.form['firstPerson'].split(',')
			firstPerson = {"firstName": firstPerson[0], "lastName": firstPerson[1], "born": int(firstPerson[2])}
			secondPerson = request.form['secondPerson'].split(',')
			secondPerson = {"firstName": secondPerson[0], "lastName": secondPerson[1], "born": int(secondPerson[2])}
			results = searchConnections(firstPerson, secondPerson)
			if not results:
				flash("There are no relations between those members.", 'info')
			return render_template('searchRelation.html', 
				title='Genealogical Tree / Search Relations',
				form=form,
				options=options,
				results=results
			)
		except Exception as e:
			print("Something went wrong:", e)
	return render_template('searchRelation.html', 
		title='Genealogical Tree / Search Relations',
		form=form,
		options=options,
		results=None
	)