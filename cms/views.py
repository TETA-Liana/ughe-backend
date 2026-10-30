from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import HeroSlide, NavItem, SiteSettings, Stat, TopButton
from .serializers import (HeroSlideSerializer, NavItemSerializer, SiteSettingsSerializer,
                          StatSerializer, TopButtonSerializer)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login_view(request):
    """POST {username, password} -> {token, username}. Users are predefined (created by seed_ughe)."""
    user = authenticate(username=request.data.get("username", ""), password=request.data.get("password", ""))
    if user is None or not user.is_active:
        return Response({"detail": "Incorrect username or password."}, status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username})


@api_view(["POST"])
def logout_view(request):
    Token.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def me_view(request):
    return Response({"username": request.user.username})


@api_view(["GET"])
def homepage_view(request):
    """Everything the homepage needs, in one request. Only active items, in admin-defined order."""
    ctx = {"request": request}
    return Response({
        "settings": SiteSettingsSerializer(SiteSettings.load(), context=ctx).data,
        "top_buttons": TopButtonSerializer(TopButton.objects.filter(is_active=True), many=True).data,
        "nav_items": NavItemSerializer(NavItem.objects.filter(is_active=True, parent__isnull=True), many=True).data,
        "slides": HeroSlideSerializer(
            HeroSlide.objects.filter(is_active=True).prefetch_related("media"), many=True, context=ctx).data,
        "stats": StatSerializer(Stat.objects.filter(is_active=True), many=True).data,
    })
