#celery = Celery('Task', broker='amqp://guest:guest@localhost:5672//')
from celery import shared_task
#for revoking a task from terminal
'''
from amass import celery
celery.control.revoke('task_id', terminate = True, signal = 'SIGKILL')
'''
import subprocess

######################################################################################
from core.models import scan
from django.conf import settings
import datetime


@shared_task
def amass(y,user):
    
    print(y)
    print('Please wait while your query is being processed. This may take some time.')
    #print(current_task.request.id)
    print(f"Execution of {y} has STARTED")
    # process = subprocess.Popen(['./amass.exe', 'enum', '-active', '-d', domain],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    # stdout, stderr = process.communicate()
    subprocess.call(['bash',f'{settings.SITE_ROOT}/attack_eye/apps/amass/scripts/search.sh',y])
    print(f"Execution of {y} has COMPLETED")
    scan.objects.filter(UserId=user,domain=y).update(pending=1, timeDateEnd=datetime.datetime.now())