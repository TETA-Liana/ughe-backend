import re

from rest_framework import serializers

from .models import HeroSlide, NavItem, SiteSettings, SlideMedia, Stat, TopButton

YOUTUBE_RE = re.compile(r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})")


def absolute(request, file_field):
    if not file_field:
        return ""
    return request.build_absolute_uri(file_field.url) if request else file_field.url


class SiteSettingsSerializer(serializers.ModelSerializer):
    logo_src = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = ["site_name", "logo_src", "logo_link", "show_search", "search_url", "stats_heading"]

    def get_logo_src(self, obj):
        return absolute(self.context.get("request"), obj.logo) or obj.logo_url


class TopButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopButton
        fields = ["id", "label", "url"]


class NavChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavItem
        fields = ["id", "label", "url"]


class NavItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = NavItem
        fields = ["id", "label", "url", "children"]

    def get_children(self, obj):
        return NavChildSerializer(obj.children.filter(is_active=True), many=True).data


class SlideMediaSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()
    youtube_id = serializers.SerializerMethodField()

    class Meta:
        model = SlideMedia
        fields = ["id", "media_type", "src", "youtube_id", "alt_text"]

    def get_src(self, obj):
        return absolute(self.context.get("request"), obj.file) or obj.external_url

    def get_youtube_id(self, obj):
        match = YOUTUBE_RE.search(obj.external_url or "")
        return match.group(1) if (match and not obj.file) else None


class HeroSlideSerializer(serializers.ModelSerializer):
    media = SlideMediaSerializer(many=True, read_only=True)

    class Meta:
        model = HeroSlide
        fields = ["id", "heading", "button_text", "button_url", "duration_seconds", "overlay_opacity", "media"]


class StatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stat
        fields = ["id", "value", "description", "background_color", "text_color"]
