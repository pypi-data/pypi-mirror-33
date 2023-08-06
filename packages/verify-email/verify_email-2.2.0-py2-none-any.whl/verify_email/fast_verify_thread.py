from datetime import datetime
from verify_email import validate_email
from verify_email import get_mx_ip

import threading


def validate(email, mass):
    a = datetime.now()
    value = validate_email(email, mass)
    delta = datetime.now() - a
    print(value, email, (delta.microseconds + delta.microseconds/1E6))


def lookup(email):
    hostname = email[email.find('@') + 1:]
    max_hosts = get_mx_ip(hostname)
    return max_hosts


emails = ["k.akshay9721@gmail.com", "xyz231312dasdaf@gmail.com", "foo@bar.com", "ex@example.com"]  # add emails
b = datetime.now()

# creating threads
t2 = threading.Thread(target=validate, name='t2', args=(emails, True))
# starting threads
t2.start()
# wait until all threads finish
t2.join()

delta = datetime.now() - b
print(delta.seconds + delta.microseconds/1E6)
