from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("applications.offer.urls"), name="offer"),
    path("api/profile/", include("applications.user_profile.urls"), name="profile"),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),

    path("chat/", include("applications.chat.urls"), name="chat")
    # path("auth/", include("djoser.urls.jwt")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
