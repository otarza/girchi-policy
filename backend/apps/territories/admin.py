from django.contrib import admin

from .models import District, Precinct, Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "name_ka", "code")
    search_fields = ("name", "name_ka", "code")


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "name_ka", "cec_code", "region")
    search_fields = ("name", "name_ka", "cec_code")
    list_filter = ("region",)


@admin.register(Precinct)
class PrecinctAdmin(admin.ModelAdmin):
    list_display = ("name", "name_ka", "cec_code", "district")
    search_fields = ("name", "name_ka", "cec_code")
    list_filter = ("district__region", "district")
    raw_id_fields = ("district",)
