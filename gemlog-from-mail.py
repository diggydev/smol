from datetime import datetime
from mailbox import mbox
import re 

TIME_TZ_OFFSET = '%a, %d %b %Y %H:%M:%S %z'
TIME_TZ_NAME = '%a, %d %b %Y %H:%M:%S %Z'

mail_source = mbox('mail')
author_email = 'abc@example.com'

def is_from_author(from_field):
  address = from_field[from_field.find('<')+1:-1].strip()
  return author_email==address

def parse_date(date_str):
  return datetime.strptime(date_str, TIME_TZ_OFFSET)

def generate_filename(mail_date, subject):
  return datetime.strftime(mail_date, '%Y-%m-%d') + '-' + re.sub('\W+','-',subject.lower()) + '.gmi'

for mail in mail_source:
  if is_from_author(mail['From']):
    mail_date = parse_date(mail['Date'])
    print(mail_date)
    print(mail['Subject'])
    print(generate_filename(mail_date, mail['Subject']))
  # print(mail.get_payload())
