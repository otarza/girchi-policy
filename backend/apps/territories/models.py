from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=100)
    name_ka = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class District(models.Model):
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="districts"
    )
    name = models.CharField(max_length=100)
    name_ka = models.CharField(max_length=100)
    cec_code = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["cec_code"]),
        ]

    def __str__(self):
        return self.name


class Precinct(models.Model):
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="precincts"
    )
    name = models.CharField(max_length=100)
    name_ka = models.CharField(max_length=100)
    cec_code = models.CharField(max_length=20, unique=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["cec_code"]),
        ]

    def __str__(self):
        return self.name
