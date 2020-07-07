from django.contrib.auth.hashers import make_password, check_password
from trueapp.models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import traceback
from django.db.models import Q



### function to authenticate user making requests.
def authenticateUser(phone):
    user = Users.objects.filter(contact=phone)
    if user.exists():
        return check_password(phone,user[0].password),user
    else:
        return False,None



##### register users with username,email,contact number and password
@csrf_exempt
def registerUsers(request):
    response = HttpResponse()
    try:
        print(type(request.body))
        data = json.loads(request.body)
        if data['username'] and data['contact']:    
            Users.objects.create(username=data['username'],email=data['email'], \
                contact=data['contact'],password=make_password(data['password']))
            message = "User Registered Successfully!"
            response.status_code = 200
            response.content = json.dumps({'message':message,'Ok':True})
            return response
        else:
            message = "Check user data!"
            response.content = json.dumps({'message':message,'Ok':False})
            return response
    except:
        print(traceback.format_exc())
        message = "An error Occurred!"
        response.status_code = 500
        response.content = json.dumps({'message':message,'Ok':False})


#### function to allow existing user to mark a phone number as spam
@csrf_exempt
def markSpam(request):
    try:
        response = HttpResponse()
        data = json.loads(request.body)
        phone = data['contact']
        password = data['password']
        no_to_mark_spam = data['spam']
        auth_flag,user = authenticateUser(phone)
        if auth_flag:
            contacts = Contacts.objects.filter(phone_number=no_to_mark_spam)
            if contacts:
                for item in contacts:
                    item.is_spam = 1
                    item.spam_count += 1
                    item.save()
                    Spam.objects.create(phone_number=item.phone_number,marked_spam_by_id=user[0].id)
                    response.status_code = 200
                    response.content = json.dumps({'message':'Marked '+no_to_mark_spam+' as Spam.','Ok':True})
                return response
            ## else create a new contact as spam in Contacts.
            else:
                spam_user = Contacts()
                spam_user.name = ''
                spam_user.phone_number = no_to_mark_spam
                spam_user.is_spam = 1 
                temp_user_spam = Users.objects.filter(contact=no_to_mark_spam)
                if temp_user_spam.exists():
                    spam_user.is_user = 1
                    spam_user.name = temp_user_spam[0].username
                else:
                    spam_user.is_user = 0
                    spam_user.name = 'marked by '+user[0].username
                spam_user.userid_id = user[0].id
                spam_user.spam_count = 1
                spam_user.save()
                Spam.objects.create(phone_number=no_to_mark_spam,marked_spam_by_id=user[0].id)
                response.status_code = 200
                response.content = json.dumps({'message':'Spam User Created!!','Ok':True})
                return response
        else:
            message = "You're not authorized to perform this action!"
            response.status_code = 403
            response.content = json.dumps({'message':message,'Ok':False})
            return response

    except:
        print(traceback.format_exc())
        response.status_code = 500
        message = 'Server Error.'
        response.content = json.dumps({'message':message,'Ok':False})
        return response





### consolidated function to search contacts by name or phone number
@csrf_exempt
def searchUser(request):
    response = HttpResponse()
    data = json.loads(request.body)
    phone = data['phone']
    search_name = data['search']
    search_type = data['type'] # 0 for search_by_name, 1 for search_by_number
    auth_flag,user = authenticateUser(phone)
    result = []
    try:
        if auth_flag:   # if user is valid
            if search_type: # if search_type exists

                ## search by name
                if search_type == '0':
                    start_query = Contacts.objects.filter(name__istartswith=search_name).values()
                    contains_query = Contacts.objects.filter(~Q(name__istartswith=search_name) & \
                        Q(name__contains=search_name)).values()
                    if start_query:
                        for start_item in start_query:
                            search_contact_person = Users.objects.filter(contact=start_item['phone_number'])
                            search_contact_id = search_contact_person[0].id if search_contact_person.exists() else 0
                            search_contact_list = Contacts.objects.filter(userid_id=search_contact_id).values_list('phone_number',flat=True)
                            ##if requesting user exists in contacts of searched person
                            if start_item['is_user'] == 1 and user[0].contact in search_contact_list:
                                start_item['email'] = search_contact_person[0].email
                            result.append(start_item)
                    if contains_query:
                        for contains_item in contains_query:
                            search_contact_person = Users.objects.filter(contact=start_item['phone_number'])
                            search_contact_id = search_contact_person[0].id if search_contact_person.exists() else 0
                            search_contact_list = Contacts.objects.filter(userid_id=search_contact_id).values_list('phone_number',flat=True)
                            ##if requesting user exists in contacts of searched person
                            if start_item['is_user'] == 1 and user[0].contact in search_contact_list:
                                start_item['email'] = search_contact_person[0].email
                            result.append(contains_item)

                    message = str(len(result))+' registered user records found!' if len(result) > 0 else 'No Match Found!'
                    response.status_code = 200
                    response.content = json.dumps({'message':message,'data':result,'Ok':True})
                    return response

                ## search by phone number
                elif search_type == '1':
                    number_to_search = data['searchPhone']
                    user_number = Users.objects.filter(contact=number_to_search).values('id','username','contact','email')
                    if user_number:
                        search_contact_list = Contacts.objects.filter(userid_id=user_number[0]['id']).values_list('phone_number',flat=True)
                        if user[0].contact in search_contact_list:
                            result.append(user_number[0])
                        else:
                            del user_number[0]['email']
                            result.append(user_number[0])
                    else:
                        user_contact = Contacts.objects.filter(phone_number=number_to_search).values()
                        if user_contact:
                            for item in user_contact:
                                result.append(item)
                        else:
                            message = number_to_search+' not found!'
                            response.status_code = 404
                            response.content = json.dumps({'message':message,'data':result,'Ok':True})
                            return response

                    message = str(len(result))+' records found!' if len(result) > 0 else 'No Match Found!'
                    response.status_code = 200
                    response.content = json.dumps({'message':message,'data':result,'Ok':True})
                    return response
                else:
                    message = "Wrong Search Type selected. You can select 0 (search by name) or 1 \
(search by phone number). Please try again."
                response.status_code = 422
                response.content = json.dumps({'message':message,'Ok':False})
                return response

            else:
                message = "Search Type not selected. You can select 0 (search by name) or 1 \
(search by phone number). Please try again."
                response.status_code = 422
                response.content = json.dumps({'message':message,'Ok':False})
                return response


        else:
            message = "You're not authorized to perform this action!"
            response.status_code = 403
            response.content = json.dumps({'message':message,'Ok':False})
            return response
    except:
        print(traceback.format_exc())
        response.status_code = 500
        message = 'Server Error.'
        response.content = json.dumps({'message':message,'Ok':False})
        return response
