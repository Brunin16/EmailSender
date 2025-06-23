from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from send_email import send_monthly_email

if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    trigger = CronTrigger(day="20", hour="9", minute="0")
    scheduler.add_job(send_monthly_email, trigger)
    print("Agendador iniciado — aguardando dia 20...")
    scheduler.start()
