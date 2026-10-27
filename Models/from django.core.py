from django.core.exceptions import ValidationError

class BloodRequest(models.Model):
    class Urgency(models.TextChoices):
        ROUTINE = "ROUTINE", "Routine"
        URGENT = "URGENT", "Urgent"
        EMERGENCY = "EMERGENCY", "Emergency"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_REVIEW = "IN_REVIEW", "In Review"
        ACCEPTED = "ACCEPTED", "Accepted"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    hospital = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blood_requests",
        limit_choices_to={"role": User.Role.HOSPITAL},
    )
    blood_type = models.CharField(max_length=3, choices=User.BloodType.choices)
    units_needed = models.PositiveIntegerField(default=1)
    urgency = models.CharField(max_length=20, choices=Urgency.choices, default=Urgency.ROUTINE)
    notes = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    def can_transition_to(self, new_status):
        allowed = {
            self.Status.OPEN: {self.Status.IN_REVIEW, self.Status.CANCELLED},
            self.Status.IN_REVIEW: {self.Status.ACCEPTED, self.Status.CANCELLED},
            self.Status.ACCEPTED: {self.Status.COMPLETED},
            self.Status.COMPLETED: set(),
            self.Status.CANCELLED: set(),
        }
        return new_status in allowed.get(self.status, set())

    def update_status(self, new_status):
        if not self.can_transition_to(new_status):
            raise ValidationError("This status change is not allowed.")
        self.status = new_status
        self.save(update_fields=["status"])