from django.db import models

# registered users' model.
class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100,null=False)
    email = models.CharField(max_length=100,blank=True,null=True,default=None)
    contact = models.CharField(max_length=15,unique=True,null=False,blank=False)
    password = models.CharField(max_length=100,null=False,blank=False,default=None)

    class Meta:
        db_table = 'Users'
        unique_together = (('id','contact'))

#contact model having records of contacts of all registered users.
class Contacts(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100,null=False)
    phone_number = models.CharField(max_length=100,blank=True,null=False,default=None)
    userid = models.ForeignKey(Users,on_delete=models.PROTECT)
    is_user = models.IntegerField()   #flag to detect contact as existing user.
    is_spam = models.IntegerField()   #flag to detect contact as spam or not.
    spam_count = models.IntegerField()  #number of times  number is marked as spam.

    class Meta:
        db_table = 'Contacts'

class Spam(models.Model):
    id = models.AutoField(primary_key=True)
    phone_number = models.CharField(max_length=100,blank=True,null=True,default=None)
    marked_spam_by = models.ForeignKey(Users,on_delete=models.PROTECT)

    class Meta:
        db_table = 'Spam'


