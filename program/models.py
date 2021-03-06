from django.db import models

class departments(models.Model):
	department = models.CharField(max_length=100) 

class alumni(models.Model):
	firstname = models.CharField(max_length =100)
	lastname = models.CharField(max_length =100)
	password = models.CharField(max_length = 100)
	emailid = models.EmailField()
	password = models.CharField(max_length =128)
	contactnumber = models.CharField(max_length =15)
	organization = models.CharField(max_length=100,null = True)
	department = models.ForeignKey(departments,related_name='alumnipreferences_department',null = True)
	batch = models.CharField(max_length=10,null = True)	
	designation = models.CharField(max_length=100,null = True)

class students(models.Model):
	firstname = models.CharField(max_length =100)
	lastname = models.CharField(max_length =100)
	password = models.CharField(max_length = 100)
	emailid = models.EmailField()
	password = models.CharField(max_length =128)
	contactnumber = models.CharField(max_length =15)
	rollnumber = models.CharField(max_length=20)
	department = models.ForeignKey(departments,null = True)
	cgpa = models.DecimalField(max_digits = 3,decimal_places=2,null = True)


class interest(models.Model):
	interest = models.CharField(max_length = 100)	

class studentpreferences(models.Model):
	id = models.ForeignKey(students,primary_key = True)
	interest1 = models.ForeignKey(interest,related_name = 'studentpreferences_interest1',null = True)
	interest2 = models.ForeignKey(interest,related_name = 'studentpreferences_interest2',null = True)
	interest3 = models.ForeignKey(interest,related_name = 'studentpreferences_interest3',null = True)
	interest4 = models.ForeignKey(interest,related_name = 'studentpreferences_interest4',null = True)
	mentorid1 = models.ForeignKey(alumni,related_name = 'studentpreferences_mentorid1',null=True,default = None)
	mentorid2 = models.ForeignKey(alumni,related_name = 'studentpreferences_mentorid2',null=True,default = None)
	mentorid3 = models.ForeignKey(alumni,related_name = 'studentpreferences_mentorid3',null=True,default = None)
	mentorid4 = models.ForeignKey(alumni,related_name = 'studentpreferences_mentorid4',null=True,default = None)
	mentorid5 = models.ForeignKey(alumni,related_name = 'studentpreferences_mentorid5',null=True,default = None)


class alumnipreferences(models.Model):
	id = models.ForeignKey(alumni,primary_key = True)
	interest = models.ForeignKey(interest,related_name='alumnipreferences_interest')
	noofmentees = models.IntegerField()
	
class coordinators(models.Model):
	emailid = models.EmailField()
	password = models.CharField(max_length = 128)