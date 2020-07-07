from django.core.management.base import BaseCommand
from trueapp.models import *
from trueapp.listdata import userList,contactList
from django.contrib.auth.hashers import make_password

### custom command to fill data in Users and Contacts table
class Command(BaseCommand):
    def handle(self, *args, **options):
        for i in range(len(userList)):
            user = Users.objects.create(username=userList[i]['username'],email='',contact=userList[i]['contact'],password=make_password(userList[i]['password']))
            fillActivity(user,i)



def fillActivity(user,i):
    for item in contactList[i]:
        Contacts.objects.create(name=item['name'],phone_number=item['phone_number'],userid_id=user.id,is_spam=0,is_user=0,spam_count=0)
