from django.db import models


class Section(models.Model):
    location = models.ForeignKey("locations.Location", on_delete=models.PROTECT, related_name="sections")
    name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["location", "name"], name="uq_section_location_name"),
        ]

    def __str__(self):
        return f"{self.location} - {self.name}"
