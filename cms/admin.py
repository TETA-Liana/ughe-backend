from django.contrib import admin

from .models import HeroSlide, NavItem, SiteSettings, SlideMedia, Stat, TopButton


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "show_search", "stats_heading")

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()  # only one settings row


@admin.register(TopButton)
class TopButtonAdmin(admin.ModelAdmin):
    list_display = ("label", "url", "order", "is_active")
    list_editable = ("order", "is_active")


class ChildNavInline(admin.TabularInline):
    model = NavItem
    fk_name = "parent"
    extra = 0
    fields = ("label", "url", "order", "is_active")
    verbose_name = "Dropdown link"
    verbose_name_plural = "Dropdown links"


@admin.register(NavItem)
class NavItemAdmin(admin.ModelAdmin):
    list_display = ("label", "parent", "url", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("parent",)
    inlines = [ChildNavInline]


class SlideMediaInline(admin.StackedInline):
    model = SlideMedia
    extra = 1


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("__str__", "media_count", "order", "is_active")
    list_editable = ("order", "is_active")
    inlines = [SlideMediaInline]

    @admin.display(description="Images / videos")
    def media_count(self, obj):
        return obj.media.count()


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ("value", "description", "background_color", "order", "is_active")
    list_editable = ("order", "is_active")
