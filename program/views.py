from django.shortcuts import render,redirect

from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from django.template.loader import render_to_string
from program.forms import Login,Register,coordinatorlogin
from program.models import *
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password,check_password

def home(request):
	if 'firstname' not in request.session:
		request.session['firstname'] = "Guest"

	return render(request,'home.html',{'':''})

def accessCheck(request):
	if 'id' not in request.session:
		return 0
	else:
		return 1

def login(request):
	result = accessCheck(request)
	if result==1:
 	   return HttpResponseRedirect("dashboard")

	userid = ''
	firstname = ''
	if request.method == 'GET':
		form = Login()
		return render(request,'login.html',{'form':form})
		
	elif request.method == 'POST':
		response = HttpResponse()
		form = Login(request.POST)
		if (form.is_valid()):
			emailid = form.cleaned_data['emailid']
			password = form.cleaned_data['password']
			membertype = form.cleaned_data['member']
			if membertype=='student':
				try:
			
					loggedstudent = students.objects.get(emailid = emailid)
					userid1 = loggedstudent.id
					firstname = loggedstudent.firstname
					
					if not check_password(password,loggedstudent.password):
						userid1 = None
				except students.DoesNotExist:
					userid1 = None
			elif membertype =='alumni':		
				try:
					loggedalumni = alumni.objects.get(emailid = emailid)
					userid1 = loggedalumni.id
					firstname = loggedalumni.firstname
					if not check_password(password,loggedalumni.password):
						userid1 = None
				except alumni.DoesNotExist:
					userid1 = None

			
			if userid1:
				request.session['id'] = userid1
				request.session['firstname'] = firstname or "yo"
				request.session['membertype'] = membertype
				return HttpResponseRedirect("dashboard")
				
				#return render(request,'profile.html',{'firstname':request.session['firstname'],'msg':response})
				
				#return response
			elif userid1==None:
				form = Login()
				return render(request,'login.html',{'form':form,'msg':'Username Password Combination Incorrect'})
		else:
			response.write('Error')	

		for error in form.errors:
			response.write(error)
		
		return response	



def register(request):
	sent = ''
	result = accessCheck(request)
	if result==1:
 	   return HttpResponseRedirect("dashboard")
	response = HttpResponse()
	user = ''
	if request.method == 'GET':
		form = Register()
		return render(request,'register.html',{'form':form})
	else:
		form = Register(request.POST)
		if form.is_valid():	
			password = form.cleaned_data['password']
			
			repassword = form.cleaned_data['repassword']
			if password!=repassword:
				return render(request,'register.html',{'form':form,'msg':'Passwords do not match'})

			else:	
				rawpassword = password
				password = make_password(password)
				member = form.cleaned_data['member']
				firstname = form.cleaned_data['firstname']
				lastname = form.cleaned_data['lastname']
				emailid = form.cleaned_data['emailid']
				contactnumber =form.cleaned_data['contactnumber']
				if member == 'alumni':
					try:
						user = alumni.objects.get(emailid = emailid)
					except alumni.DoesNotExist:
						user = None
					if user!=None:
						return render(request,'register.html',{'form':form,'msg':'This emailid id already exists'})
					else:
						
						#render(request,'register.html',{'form':form,'msg':'This email id already exists'})
						alumni1 = alumni(firstname = firstname,lastname = lastname,emailid = emailid,password = password,contactnumber = contactnumber)
						alumni1.save()
						alum = alumni.objects.all()
						sent = email(subject="Student Alumni Mentorship Program IIT Kharagpur",emailid=emailid,firstname=firstname,msg ="Thank you for regsitering as a mentor for the Student Alumni Mentorship Program. Your loginid is " +str(emailid)+" And your password is "+str(rawpassword))

				elif member == 'student':
					try:
						user = students.objects.get(emailid = emailid)
					except students.DoesNotExist:
						user = None
					if user!=None :
						return render(request,'register.html',{'form':form,'msg':'This email id already exists'})

					else:	
						student1 = students(firstname = firstname,lastname = lastname,emailid = emailid,password = password,contactnumber = contactnumber)
						student1.save()
						sent = email(subject="Student Alumni Mentorship Program IIT Kharagpur",emailid=emailid,firstname=firstname,msg ="You have been regsitered for the Student Alumni Mentorship Program. Your loginid is " +str(emailid)+" And your password is "+str(rawpassword))

				if sent=="sent":
					return render(request,'home.html',{'msg':'Congrats, You have successfully registered, a mail has been sent to the address you provided with the login credentials. You can login now.'})
				else:
					return render(request,'home.html',{'msg':'Your emailid appears to be incorrect. Please try registering again with a correct emailid.'})
		else:	
			errors = form.errors
			return render(request,'register.html',{'form':form,'msg':"Please see the errors: ",'errors':errors})

def editProfile(request):
	result = accessCheck(request)
	if result==0:
 	   return HttpResponseRedirect("home")
	from program.forms import EditStudentProfile, EditAlumniProfile
	from program.models import interest
	form = ''
	if request.method=='GET' and request.session['membertype']=="student":
		try:
			filledpreference = studentpreferences.objects.get(id = students.objects.get(id = request.session['id']))
			profiledata = students.objects.get(id = request.session['id'])
			form = EditStudentProfile({'department':profiledata.department.id,'rollnumber':profiledata.rollnumber,'cgpa':profiledata.cgpa,'interest1':filledpreference.interest1.id,'interest2':filledpreference.interest2.id,'interest3':filledpreference.interest3.id,'interest4':filledpreference.interest4.id})
		except studentpreferences.DoesNotExist:
			form = EditStudentProfile()
		return render(request,'editProfile.html',{'firstname':request.session['firstname'],'form':form,'msg':''})
	if request.method=='GET' and request.session['membertype']=="alumni":
		try:
			filleddata = alumnipreferences.objects.get(id = alumni.objects.get(id = request.session['id']))
			profiledata = alumni.objects.get(id=request.session['id'])
			form = EditAlumniProfile({'department':profiledata.department.id,'batch':profiledata.batch,'interest':filleddata.interest.id,'noofmentees':filleddata.noofmentees,'organization':profiledata.organization,'designation':profiledata.designation})
		except alumnipreferences.DoesNotExist:
			form = EditAlumniProfile()
		return render(request,'editProfile.html',{'form':form,'msg':''})

	else:
		if request.session['membertype']=='student':
			form = EditStudentProfile(request.POST)
			if form.is_valid():	
				interest1 = interest.objects.get(id = form.cleaned_data['interest1'])
				interest2 = interest.objects.get(id = form.cleaned_data['interest2'])
				interest3 = interest.objects.get(id = form.cleaned_data['interest3'])
				interest4 = interest.objects.get(id = form.cleaned_data['interest4'])
				rollnumber = form.cleaned_data['rollnumber']
				# interestlist = [interest1,interest2,interest3,interest4]
				# if len(interestlist)!=len(set(interestlist)):#check if distinct interests are given
				# 	try:	
				# 		filleddata = studentpreferences.objects.get(id = students.objects.get(id = request.session['id']))
				# 		form = EditStudentProfile({'department':filleddata.department.id,'cgpa':filleddata.cgpa,'interest1':filleddata.interest1.id,'interest2':filleddata.interest2.id,'interest3':filleddata.interest3.id,'interest4':filleddata.interest4.id})
				# 	except studentpreferences.DoesNotExist:
				# 		form = EditStudentProfile()
				# 	return render(request,'editProfile.html',{'form':form,'msg':'You have to specify different interest or leave it blank'})

				department = departments.objects.get(id =form.cleaned_data['department'])
				cgpa = form.cleaned_data['cgpa']
				obj = students.objects.get(id = request.session['id'])
				batch = form.cleaned_data['batch']
				try:
					preference = studentpreferences.objects.get(id = obj)
					obj.rollnumber = rollnumber
					obj.department = department
					preference.interest1 = interest1
					preference.interest2 = interest2
					preference.interest3 = interest3
					preference.interest4 = interest4
					obj.cgpa = cgpa
					preference.save()
					students.objects.filter(id = request.session['id']).update(cgpa = cgpa,department = department,batch = batch)

					obj.save()
				except studentpreferences.DoesNotExist:
					preference = studentpreferences(id =obj,interest1=interest1,interest2=interest2,interest3=interest3,interest4=interest4) 
					students.objects.filter(id = request.session['id']).update(cgpa = cgpa,department = department,batch = batch)
					preference.save()
				return render(request,'home.html',{'msg':'Your preferences have been updated.'})
			else:
				errors = form.errors
				return render(request,'editProfile.html',{'form':form,'msg':'Please see the errors','errors':errors })
		else:
			form = EditAlumniProfile(request.POST)
			if form.is_valid():	
				department = departments.objects.get(id = form.cleaned_data['department'])
				interest = interest.objects.get(id = form.cleaned_data['interest'])	
				noofmentees = form.cleaned_data['noofmentees']	
				organization = form.cleaned_data['organization']
				designation = form.cleaned_data['designation']	
				batch = form.cleaned_data['batch']
				obj = alumni.objects.get(id = request.session['id'])
				try:
					preference = alumnipreferences.objects.get(id=obj)
					preference.interest = interest
					preference.noofmentees = noofmentees
					alumni.objects.filter(id = request.session['id']).update(designation = designation,organization=organization,batch = batch,department = department)
					preference.save()
				except alumnipreferences.DoesNotExist:
					preference = alumnipreferences(id =obj,interest=interest,noofmentees = noofmentees) 
					preference.save()
					
					alumni.objects.filter(id = request.session['id']).update(designation = designation,organization=organization,batch = batch,department = department)

				return render(request,'home.html',{'msg':'Your preferences have been updated.'})
			else:
				errors = form.errors
				return render(request,'editProfile.html',{'form':form,'msg':'Please see the errors','errors':errors })

def showProfile(request):
	result = accessCheck(request)
	if result==0:
 	   return HttpResponseRedirect("home")
	userid1 = request.session['id']
	membertype = request.session['membertype']
	preferences = {}
	profiledata = {}
	if membertype=='student':
		try:
			preferences = studentpreferences.objects.get(id = userid1)
		except studentpreferences.DoesNotExist:
			from program.forms import EditStudentProfile
			form = EditStudentProfile()
			return render(request,'editProfile.html',{'form':form})
		profiledata = students.objects.get(id = request.session['id'])
		return render(request,'profile.html',{'profiledata':profiledata,'preferences':preferences,'msg':'','membertype':membertype})

	elif membertype=='alumni':
		try:
			preferences = alumnipreferences.objects.get(id = userid1)
		except alumnipreferences.DoesNotExist:
			from program.forms import EditAlumniProfile
			form = EditAlumniProfile()
			return render(request,'editProfile.html',{'form':form})
		profiledata = alumni.objects.get(id = request.session['id'])
		return render(request,'profile.html',{'profiledata':profiledata,'preferences':preferences,'msg':'','membertype':membertype})

def mentorlist(request,suggest="off"):
	result = accessCheck(request)
	if result==0:
 	   return HttpResponseRedirect("home")
	response = HttpResponse()
	al1=[]
	al2=[]
	al3=[]
	al4=[]
	match = ''
	userid = request.session['id']
	user = students.objects.get(id=userid)
	preference=''
	if suggest=="off":
		try:
			preference = studentpreferences.objects.get(id =user )

		except studentpreferences.DoesNotExist:
			preference = None

	
		if preference:
		#response.write("We have your preference stored")
			interest1 = preference.interest1
			interest2 = preference.interest2
			interest3 = preference.interest3
			interest4 = preference.interest4
		
			match1 = alumnipreferences.objects.filter(interest = interest1)
			match2 = alumnipreferences.objects.filter(interest = interest2)
			match3 = alumnipreferences.objects.filter(interest = interest3)
			match4 = alumnipreferences.objects.filter(interest = interest4)

			if match1:
				for match in match1:
					alum = match.id
					al1.append([alum.id,alum.department.department,match.interest.interest,alum.organization,alum.designation])
			if match2:
				for match in match2:
					alum = match.id
					al2.append([alum.id,alum.department.department,match.interest.interest,alum.organization,alum.designation])

			if match3:
				for match in match3:
					alum = match.id
					al3.append([alum.id,alum.department.department,match.interest.interest,alum.organization,alum.designation])

			if match4:
				for match in match4:
					alum = match.id
					al4.append([alum.id,alum.department.department,match.interest.interest,alum.organization,alum.designation])
			return render(request,'mentorlist.html',{'match1':al1,'match2':al2,'match3':al3,'match4':al4})
		else:
			
			return render(request,'mentorlist.html',{'msg':'Sorry, we have no mentors with matching preferences'})

	else:
		pass

def dashboard(request):
	#response.write('this is dashboard where you will see notifications regarding the program')
	if request.session['membertype']=="student":
		return render(request,'mentee.html',{'':''}) 
	if request.session['membertype']=="alumni":
		return render(request,'mentor.html',{'':''})

def logout(request):
	result = accessCheck(request)
	if result==0:
 	   return HttpResponseRedirect("home")
	request.session.flush()
	return HttpResponseRedirect("home")

def email(subject,emailid,firstname,msg):
	sent = send_mail(subject,msg,'mentorship@adm.iitkgp.ernet.in',[emailid])
	if sent == 1:
		return "sent"
	else:
		return "not sent"

def selectmentor(request):
	response = HttpResponse()
	result = accessCheck(request)
	if result==0:
 		return HttpResponseRedirect("home")
 	if request.method=='GET':
 		return HttpResponseRedirect("showProfile")
 	elif request.method=='POST':
 		mentoridlist = request.POST.getlist('mentorid')
 		preference = studentpreferences.objects.get(id = students.objects.get(id=request.session['id']))
 
 		
 		if len(mentoridlist)>0:
 			preference.mentorid1 = alumni.objects.get(id =mentoridlist[0])
 		if len(mentoridlist)>1:
 			preference.mentorid2 = alumni.objects.get(id =mentoridlist[1])
 		if len(mentoridlist)>2:
 			preference.mentorid3 = alumni.objects.get(id =mentoridlist[2])
 		if len(mentoridlist)>3:
 			preference.mentorid4 = alumni.objects.get(id =mentoridlist[3])
 		if len(mentoridlist)>4:
 			preference.mentorid5 = alumni.objects.get(id =mentoridlist[4])		
 		preference.save()
 		
 	return HttpResponseRedirect("showProfile")

def coordinator(request):
	if request.method=="GET":
		form = coordinatorlogin()
		return render(request,'coordinatorlogin.html',{'form':form})
	elif request.method =="POST":
		response = HttpResponse()
		form = coordinatorlogin(request.POST)
		if (form.is_valid()):

			username = form.cleaned_data['emailid']
			password = form.cleaned_data['password']
			coordinator = coordinators.objects.get(emailid=username)
			if check_password(password,coordinator.password):
				request.session['firstname'] = "coordinator"
				request.session['membertype']="admin"
				request.session['id']=0
				return HttpResponseRedirect('coordinatordashboard')
				
			else:
				return render(request,'coordinatorlogin.html',{'form':form,'msg':"Incorrect username password combination"})	


def allot(request):
	if not request.session['membertype']=="admin":
		return HttpResponseRedirect('login')
	else:
		pass
		# the algo for allotment will be here .. no more use of excel file
		#count number of records in students model

def showlist(request,member):

	if member=='mentee':
		menteelist = students.objects.all().values() 
		return render(request,'list.html',{'member':'mentee','list':menteelist})
	elif member=='mentor':
		mentorlist = alumni.objects.all().values()
		return render(request,'list.html',{'member':'mentor','list':mentorlist})
	else:
		pass

def coordinatordashboard(request):
	if not request.session['membertype']=="admin":
		return HttpResponseRedirect('login')
	else:
	
		studentregistrations = students.objects.count()
		alumniregistrations = alumni.objects.count()
		return render(request,'coordinator.html',{'msg':'','studentregistrations':studentregistrations,'alumniregistrations':alumniregistrations})

def showprofilecoordinator(request,member,id):
	if not request.session['membertype']=="admin":
		return HttpResponseRedirect('login')
	else:
		if member=="mentee":
			mentee = students.objects.get(id = id)
			menteepref = studentpreferences.objects.get(id = mentee)
			return render(request,'showprofile.html',{'mentee':mentee,'menteepref':menteepref})
		elif member =="mentor":
			mentor = alumni.objects.get(id = id)
			mentorpref = alumnipreferences.objects.get(id = mentor)
			return render(request,'showprofile.html',{'mentor':mentor,'mentorpref':mentorpref})
		response = HttpResponse()
		response.write("Yay")
		return response