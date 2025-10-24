from django.conf import settings
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    level = models.PositiveSmallIntegerField(
        help_text="1=Student, 2=Tutor, 3=Freelancer, 4=Mentor"
    )
    price_month = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_free = models.BooleanField(default=False)
    max_listings = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ["level"]

    def __str__(self) -> str:
        return self.name


class Subscription(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.user} -> {self.plan}"
