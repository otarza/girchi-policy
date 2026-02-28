from django.contrib import admin

from .models import Initiative, InitiativeSignature


class InitiativeSignatureInline(admin.TabularInline):
    model = InitiativeSignature
    extra = 0
    readonly_fields = ["signer", "signed_at"]
    can_delete = False


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "author",
        "status",
        "signature_count_display",
        "signature_threshold",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = [
        "title",
        "author__phone_number",
        "author__first_name",
        "author__last_name",
    ]
    readonly_fields = ["created_at", "updated_at", "responded_at", "signature_count_display"]
    raw_id_fields = ["author", "precinct", "district", "responded_by"]
    inlines = [InitiativeSignatureInline]
    fieldsets = (
        ("Initiative Info", {"fields": ("title", "description", "status")}),
        ("Territory", {"fields": ("precinct", "district")}),
        ("Signatures", {"fields": ("signature_threshold", "signature_count_display")}),
        ("Response", {"fields": ("response_text", "responded_by", "responded_at")}),
        ("Author & Timestamps", {"fields": ("author", "created_at", "updated_at")}),
    )

    @admin.display(description="Signatures")
    def signature_count_display(self, obj):
        return obj.signatures.count()


@admin.register(InitiativeSignature)
class InitiativeSignatureAdmin(admin.ModelAdmin):
    list_display = ["id", "initiative", "signer", "signed_at"]
    list_filter = ["signed_at"]
    search_fields = [
        "initiative__title",
        "signer__phone_number",
        "signer__first_name",
    ]
    readonly_fields = ["signed_at"]
    raw_id_fields = ["initiative", "signer"]
