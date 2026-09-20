from apscheduler.schedulers.background import BackgroundScheduler
from app.database import get_all_active_customers, get_todays_list
from app.whatsapp import send_text, format_veg_list
import logging

logger = logging.getLogger(__name__)


def run_morning_broadcast():
    """Sends today's vegetable list to all active customers."""
    logger.info("⏰ Running morning broadcast...")

    veg_doc  = get_todays_list()
    message  = format_veg_list(veg_doc)
    customers = get_all_active_customers()

    sent = 0
    failed = 0
    for customer in customers:
        try:
            send_text(customer["phone"], message)
            sent += 1
        except Exception as e:
            logger.error(f"Failed to send to {customer['phone']}: {e}")
            failed += 1

    logger.info(f"✅ Broadcast done. Sent: {sent}, Failed: {failed}")


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

    # Every day at 7:00 AM IST
    scheduler.add_job(
        run_morning_broadcast,
        trigger="cron",
        hour=7,
        minute=0,
        id="morning_broadcast",
    )

    scheduler.start()
    logger.info("📅 Scheduler started — broadcast at 7:00 AM IST daily")
    return scheduler
