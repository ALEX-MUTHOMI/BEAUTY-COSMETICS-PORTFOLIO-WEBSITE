from celery import shared_task


@shared_task(
    name="bookings.tasks.process_booking_notification",
    queue="receipts",
    rate_limit="120/m",
    ignore_result=True,
)
def process_booking_notification(notification_id, correlation_id=None):
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    BookingNotificationDeliveryService.send_one(notification_id)


@shared_task(
    name="bookings.tasks.sweep_booking_notifications",
    queue="receipts",
    rate_limit="30/m",
    ignore_result=True,
)
def sweep_booking_notifications(limit=100, correlation_id=None):
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    BookingNotificationDeliveryService.send_pending(limit=limit)


@shared_task(
    name="bookings.tasks.sweep_booking_reminders",
    queue="receipts",
    rate_limit="60/m",
    ignore_result=True,
)
def sweep_booking_reminders(limit=100, correlation_id=None):
    from bookings.services.reminders import BookingReminderDeliveryService

    BookingReminderDeliveryService.send_due(limit=limit)
