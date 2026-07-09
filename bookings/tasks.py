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


@shared_task(
    name="bookings.tasks.sweep_stale_holds",
    queue="celery",
    rate_limit="30/m",
    ignore_result=True,
)
def sweep_stale_holds(limit=500, correlation_id=None):
    from bookings.services.hold_expiry import BookingHoldExpiryService

    return BookingHoldExpiryService.expire_stale_holds(limit=limit)


@shared_task(
    name="bookings.tasks.sweep_expired_checkouts",
    queue="celery",
    rate_limit="30/m",
    ignore_result=True,
)
def sweep_expired_checkouts(correlation_id=None):
    from checkout.services import expire_due_checkout_sessions

    return expire_due_checkout_sessions()


@shared_task(
    name="bookings.tasks.process_gallery_image",
    queue="gallery",
    rate_limit="60/m",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
    ignore_result=True,
)
def process_gallery_image(image_public_id, correlation_id=None):
    from bookings.services.gallery_images import process_gallery_image_now

    process_gallery_image_now(image_public_id)
