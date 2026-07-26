from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

from .models import Notification


@receiver(post_save, sender=Notification)
def send_email_notification(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user
    if not user.email:
        return

    context = {
        "user": user,
        "notification": instance,
        "site_url": settings.FRONTEND_URL,
        "now": timezone.now(),
    }

    html_message = render_to_string("notifications/email_notification.html", context)
    plain_message = strip_tags(html_message)

    subject = f"Новое уведомление: {instance.get_type_display()}"

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )