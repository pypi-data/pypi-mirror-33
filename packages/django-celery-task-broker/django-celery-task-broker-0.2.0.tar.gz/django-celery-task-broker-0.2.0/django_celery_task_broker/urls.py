from django.conf.urls import url

from tasks.views.trigger_task_view import TriggerTaskView
from tasks.views.periodic_task_view import PeriodicTaskView
from tasks.views.crontab_schedule_view import CrontabScheduleView


urlpatterns = [
    url(r'^trigger-task/$', TriggerTaskView.as_view(), name='trigger_task'),
    url(r'^periodic-task/$', PeriodicTaskView.as_view(), name='periodic_task'),
    url(r'^crontab-schedule/$', CrontabScheduleView.as_view(), name='crontab_schedule')
]
