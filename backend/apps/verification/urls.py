from django.urls import path

from . import views

app_name = "verification"

urlpatterns = [
    path("sms/send-otp/", views.SendOTPView.as_view(), name="send-otp"),
    path("sms/verify-otp/", views.VerifyOTPView.as_view(), name="verify-otp"),
    path("ged/verify/", views.GeDVerifyView.as_view(), name="ged-verify"),
    path("ged/status/", views.GeDStatusView.as_view(), name="ged-status"),
    path("device/fingerprint/", views.DeviceFingerprintView.as_view(), name="device-fingerprint"),
]
