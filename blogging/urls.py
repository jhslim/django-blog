from django.urls import include, path
from rest_framework import routers
from blogging.views import (
    BlogListView,
    BlogDetailView,
    UserViewSet,
    PostViewSet,
    CategoryViewSet,
)
from django.contrib.auth.views import LoginView, LogoutView


router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"posts", PostViewSet)
router.register(r"categories", CategoryViewSet)

urlpatterns = [
    path("", BlogListView.as_view(), name="blog_index"),
    path("api/", include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("posts/<int:pk>/", BlogDetailView.as_view(), name="blog_detail"),
    path("login", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout", LogoutView.as_view(template_name="logout.html"), name="logout"),
]

urlpatterns += router.urls
