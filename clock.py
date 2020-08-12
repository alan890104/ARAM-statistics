""" import os
from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()

@sched.scheduled_job('interval',days=1) #定期執行，每三分鐘執行一次
def cr():
    print('do crawler') #運行時打印出此行訊息
    os.system("python hero_kda_winrate.py")
    os.system("python bp.py") """