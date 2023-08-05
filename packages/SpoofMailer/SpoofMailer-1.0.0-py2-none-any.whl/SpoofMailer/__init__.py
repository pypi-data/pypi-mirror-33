import requests

sender_email=""
sender_name=""
receiver_email=""
body=""
subject=str()

def set_sender_name(s):
    global sender_name
    sender_name=s

def set_sender_email(s):
    global sender_email
    sender_email=s


def set_receiver_email(s):
    global receiver_email
    receiver_email=s

def set_subject(s):
    global subject
    subject=s

def set_body(s):
    global body
    body=s

def send():
    if (sender_email!="" and sender_name!="" and receiver_email!="" and subject!="" and body!=""):
        r = requests.post("http://gourl.gq/email.php", data={'fake_email': sender_email, 'subject': subject, 'txt': body,'sender_email':receiver_email,'name':sender_name})
        print "Mail sent!"
        return r.status_code
    else:
        print "Please set all arguments"
        return "Insufficient arguments set"