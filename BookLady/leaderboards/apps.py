from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler

import datetime
from datetime import timezone

from threading import Thread, Event

lbconfig_ready_executed = False
class LeaderboardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leaderboards'
    
    def ready(self):
        if globals()['lbconfig_ready_executed']:
            return
        globals()['lbconfig_ready_executed'] = True
        print("ready function called")
        from general.models import ScheduledTasks
        from leaderboards.models import Leaderboard

        sched = BackgroundScheduler()

        ###@sched.scheduled_job('cron',id='leaderboard_monthly_reset',day=1,hour=1, minute=0)
        def leaderboard_monthly_reset(on_init = False):
            run_reset = not on_init
            if on_init:
                now = datetime.datetime.now()
                last_actual_reset = ScheduledTasks.objects.get_or_create(task="leaderboard_monthly_reset")[0].last_executed
                last_intended_reset = datetime.datetime(now.year,now.month,1,1,0,tzinfo=timezone.utc)
                if last_actual_reset.astimezone(timezone.utc) < last_intended_reset.astimezone(timezone.utc):
                    run_reset = True
            if run_reset:
                _task = ScheduledTasks.objects.get(task="leaderboard_monthly_reset")
                Leaderboard.objects.all().update(monthly_score=0)
                _task.last_executed = datetime.datetime.now()
                _task.last_execution_successful = True
                _task.save()
                print(_task.task + " executed")

        class leaderboard_monthly_reset__on_ready(Thread):
            def run(self):
                print("leaderboard_monthly_reset__on_ready started")
                Event().wait(5)
                sched.add_job(leaderboard_monthly_reset,'cron',day=1,hour=1, minute=0, id='leaderboard_monthly_reset')
                leaderboard_monthly_reset(on_init = True)
                print("leaderboard_monthly_reset__on_ready finished")
        
        
        leaderboard_monthly_reset__on_ready().start()
