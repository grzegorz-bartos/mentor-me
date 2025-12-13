from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import Account


class Review(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=5
    )
    text = models.TextField()
    role_at_time = models.IntegerField(
        choices=Account.Role.choices, default=Account.Role.STUDENT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.rating} stars"

    def get_role_display(self):
        return dict(Account.Role.choices).get(self.role_at_time, "")
