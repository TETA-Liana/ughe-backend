"""
Content models for the UGHE Test Web App homepage.
Every section visible in the screenshot is stored here and edited in Django Admin:
  - SiteSettings  -> logo, search icon, "Facts & Stats" heading
  - TopButton     -> APPLY / GET INVOLVED / MEET THE TEAM / MORE
  - NavItem       -> About Us, Academics, Research ... (with optional dropdown children)
  - HeroSlide     -> slideshow slides (caption + button)
  - SlideMedia    -> one or many images / videos per slide
  - Stat          -> the coloured Facts & Stats boxes
"""
from django.core.exceptions import ValidationError
from django.db import models


class OrderedModel(models.Model):
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers are shown first.")
    is_active = models.BooleanField(default=True, help_text="Untick to hide without deleting.")

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class SiteSettings(models.Model):
    """Single row holding global header / section settings."""
    site_name = models.CharField(max_length=200, default="University of Global Health Equity")
    logo = models.ImageField(upload_to="branding/", blank=True, help_text="Upload a logo (takes priority over Logo URL).")
    logo_url = models.URLField(blank=True, help_text="Or use a logo hosted online.")
    logo_link = models.URLField(default="https://ughe.org", blank=True)
    show_search = models.BooleanField(default=True)
    search_url = models.URLField(default="https://ughe.org/?s=", blank=True,
                                 help_text="The search text is appended to this URL.")
    stats_heading = models.CharField(max_length=120, default="Facts & Stats")

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Site settings"


class TopButton(OrderedModel):
    label = models.CharField(max_length=60)
    url = models.URLField(blank=True)

    class Meta(OrderedModel.Meta):
        verbose_name = "Top button"

    def __str__(self):
        return self.label


class NavItem(OrderedModel):
    label = models.CharField(max_length=80)
    url = models.URLField(blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, related_name="children",
                               on_delete=models.CASCADE,
                               help_text="Leave empty for a main menu item; choose a parent to make it a dropdown link.")

    class Meta(OrderedModel.Meta):
        verbose_name = "Navigation item"

    def __str__(self):
        return f"{self.parent.label} > {self.label}" if self.parent else self.label


class HeroSlide(OrderedModel):
    heading = models.TextField(help_text="Caption text displayed over the slide.")
    button_text = models.CharField(max_length=60, blank=True, default="Explore more")
    button_url = models.URLField(blank=True)
    duration_seconds = models.PositiveIntegerField(default=7, help_text="How long the slide stays before the next one.")
    overlay_opacity = models.FloatField(default=0.45, help_text="Dark overlay strength, 0 (none) to 1 (black).")

    class Meta(OrderedModel.Meta):
        verbose_name = "Slideshow slide"

    def __str__(self):
        return self.heading[:70]


class SlideMedia(models.Model):
    IMAGE, VIDEO = "image", "video"
    TYPES = [(IMAGE, "Image"), (VIDEO, "Video")]

    slide = models.ForeignKey(HeroSlide, related_name="media", on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=TYPES, default=IMAGE)
    file = models.FileField(upload_to="slides/", blank=True, help_text="Upload an image or an .mp4/.webm video.")
    external_url = models.URLField(blank=True, max_length=500,
                                   help_text="Or paste a link: image URL, .mp4 URL or a YouTube link.")
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Slide image / video"
        verbose_name_plural = "Slide images / videos (several are shown side by side)"

    def clean(self):
        if not self.file and not self.external_url:
            raise ValidationError("Upload a file or provide an external URL.")

    def __str__(self):
        return f"{self.get_media_type_display()} #{self.pk}"


class Stat(OrderedModel):
    value = models.CharField(max_length=30, help_text='e.g. "128", "1,260" or "4TH"')
    description = models.CharField(max_length=255)
    background_color = models.CharField(max_length=7, default="#B3352F", help_text="Hex colour, e.g. #B3352F")
    text_color = models.CharField(max_length=7, default="#FFFFFF")

    class Meta(OrderedModel.Meta):
        verbose_name = "Fact / stat"

    def __str__(self):
        return f"{self.value} - {self.description[:50]}"
