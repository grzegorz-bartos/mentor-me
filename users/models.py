from urllib.parse import quote_plus

from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    class Role(models.IntegerChoices):
        STUDENT = 1, "Student"
        TUTOR = 2, "Tutor"
        FREELANCER = 3, "Freelancer"
        MENTOR = 4, "Mentor"

    role_level = models.PositiveSmallIntegerField(
        choices=Role.choices, default=Role.STUDENT
    )
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def role(self) -> str:
        return self.get_role_level_display()

    @property
    def display_name(self) -> str:
        """Return the most user-friendly name to show for the account."""

        full_name = (self.get_full_name() or "").strip()
        return full_name or self.username

    @property
    def avatar_url(self) -> str:
        """Generate a deterministic avatar URL based on the user's name."""

        name_for_avatar = quote_plus(self.display_name or self.username)
        return (
            "https://ui-avatars.com/api/?"
            f"name={name_for_avatar}&background=random&color=ffffff&size=128"
        )

    @property
    def can_browse(self) -> bool:
        return True

    @property
    def can_post_tutor(self) -> bool: # is_tutor():
        return self.role_level >= self.Role.TUTOR

    @property
    def can_take_jobs(self) -> bool:
        return self.role_level >= self.Role.FREELANCER

    @property
    def can_post_mentor(self) -> bool:
        return self.role_level >= self.Role.MENTOR
