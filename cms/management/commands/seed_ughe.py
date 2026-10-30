"""
python manage.py seed_ughe

1. Creates the predefined accounts (from environment variables):
   - APP_USERNAME / APP_PASSWORD           -> user who logs in on the Next.js site
   - DJANGO_SUPERUSER_USERNAME / _PASSWORD -> Django Admin account
2. Loads starting content taken from https://ughe.org ONLY if the tables are empty,
   so anything you change in Django Admin is never overwritten on restart.
   Use --reset to wipe and reload the starting content.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from cms.models import HeroSlide, NavItem, SiteSettings, SlideMedia, Stat, TopButton

LOGO = "https://ughe.org/wp-content/uploads/2026/04/UGHE-H.png"
BUTARO_PHOTO = "https://ughe.org/wp-content/uploads/2026/07/IMG_2169-scaled-770x400.jpg"
UGHE_VIDEO = "https://www.youtube.com/watch?v=M2l7sCuOnHo"

NAV = [
    ("About Us", "https://ughe.org/about", [
        ("Our Story", "https://ughe.org/about"),
        ("Leadership", "https://ughe.org/leadership/"),
        ("University Medalists", "https://ughe.org/university-medalists/"),
    ]),
    ("Academics", "https://ughe.org/academics/", [
        ("School of Medicine", "https://ughe.org/school-of-medicine/"),
        ("Graduate Programs", "https://ughe.org/academics/"),
        ("Professional and Executive Programs", "https://ughe.org/professional-and-executive-education-programs/"),
    ]),
    ("Research", "https://ughe.org/research/", []),
    ("Centres and Institutes", "", [
        ("Institute of Global Health Equity Research", "https://ughe.org/institute-of-global-health-equity-research/"),
        ("Centre for Gender Equity", "https://ughe.org/centre-for-gender-equity/"),
        ("Centre for One Health", "https://ughe.org/centre-for-one-health/"),
        ("Centre for Nursing and Midwifery", "https://ughe.org/centre-for-nursing-and-midwifery/"),
    ]),
    ("Admissions", "https://ughe.org/admission/", [
        ("Apply to UGHE", "https://ughe.org/admission/"),
        ("Tuition, Fees & Financial Aid", "https://ughe.org/tuition-fees-financial-aid/"),
        ("I've Been Admitted", "https://ughe.org/ive-been-admitted/"),
    ]),
    ("News and Events", "https://ughe.org/news/", [
        ("UGHE Stories", "https://ughe.org/news/"),
        ("Press releases", "https://ughe.org/press-releases/"),
        ("Newsletters", "https://ughe.org/newsletters/"),
    ]),
]

STATS = [
    ("128", "Trained community members through UGHE entrepreneurship initiatives", "#B3352F"),
    ("1,260", "Community members employed for Campus projects", "#8C2B25"),
    ("677", "Leaders across 61 countries trained in our Executive Education since 2016", "#B3352F"),
    ("4TH", "Among 129 Universities in Sub-Saharan Africa (Times Higher Education Rankings 2024)", "#8C2B25"),
]


class Command(BaseCommand):
    help = "Create predefined users and load starting homepage content from ughe.org"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing content and reload it.")

    def handle(self, *args, **options):
        self.create_users()
        if options["reset"]:
            for model in (SlideMedia, HeroSlide, NavItem, TopButton, Stat, SiteSettings):
                model.objects.all().delete()
        self.seed_content()

    def create_users(self):
        User = get_user_model()
        accounts = [
            (os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin"),
             os.environ.get("DJANGO_SUPERUSER_PASSWORD", "UgheAdmin@2026"), True),
            (os.environ.get("APP_USERNAME", "ughe"),
             os.environ.get("APP_PASSWORD", "UgheTest@2026"), False),
        ]
        for username, password, is_admin in accounts:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.is_staff = user.is_superuser = is_admin
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created {'admin' if is_admin else 'app'} user '{username}'"))

    def seed_content(self):
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(logo_url=LOGO)

        if not TopButton.objects.exists():
            for i, (label, url) in enumerate([
                ("Apply", "https://ughe.org/admission/"),
                ("Get Involved", "https://ughe.org/get-involved/"),
                ("Meet the Team", "https://ughe.org/leadership/"),
                ("More", "https://ughe.org/more/"),
            ]):
                TopButton.objects.create(label=label, url=url, order=i)

        if not NavItem.objects.exists():
            for i, (label, url, children) in enumerate(NAV):
                parent = NavItem.objects.create(label=label, url=url, order=i)
                for j, (c_label, c_url) in enumerate(children):
                    NavItem.objects.create(label=c_label, url=c_url, parent=parent, order=j)

        if not HeroSlide.objects.exists():
            # Slide 1: three images side by side (like the screenshot)
            s1 = HeroSlide.objects.create(
                heading=("The Inaugural Paul E. Farmer Butaro Dialogues: Leaders, partners, students, and "
                         "health practitioners gathered at UGHE's Butaro Campus to advance innovation for "
                         "maternal and newborn health"),
                button_text="Explore more",
                button_url="https://ughe.org/butaro-dialogues-ughe-and-partners-call-for-innovation-that-reaches-those-who-need-it-most/",
                order=0,
            )
            for i in range(3):
                SlideMedia.objects.create(slide=s1, media_type="image", external_url=BUTARO_PHOTO,
                                          alt_text="Participants at the Butaro Dialogues", order=i)
            # Slide 2: a single UGHE video
            s2 = HeroSlide.objects.create(
                heading=("Experience our impact: from classrooms to communities, UGHE is transforming "
                         "healthcare across Africa and beyond"),
                button_text="Explore more",
                button_url="https://ughe.org/ughe-turns-10/",
                order=1, duration_seconds=15,
            )
            SlideMedia.objects.create(slide=s2, media_type="video", external_url=UGHE_VIDEO,
                                      alt_text="UGHE impact video")

        if not Stat.objects.exists():
            for i, (value, text, color) in enumerate(STATS):
                Stat.objects.create(value=value, description=text, background_color=color, order=i)

        self.stdout.write(self.style.SUCCESS("Homepage content ready."))
