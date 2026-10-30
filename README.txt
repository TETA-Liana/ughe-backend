==========================================================================
                         UGHE TEST WEB APP
     Next.js (frontend)  +  Django REST API (backend)  +  PostgreSQL
==========================================================================

GITHUB REPOSITORIES (public)
----------------------------
Backend  (Django)  :https://github.com/TETA-Liana/ughe-backend.git
Frontend (Next.js) : https://github.com/TETA-Liana/ughe-frontend.git


1. WHAT THE APP DOES
--------------------
- Reproduces the UGHE homepage section shown in the screenshot: header (logo,
  APPLY / GET INVOLVED / MEET THE TEAM / MORE buttons, search icon), main menu
  (About Us, Academics, Research, Centres and Institutes, Admissions, News and
  Events, with dropdowns), the slideshow with caption and "Explore more" button,
  and the "Facts & Stats" boxes.
- Users must log in with predefined credentials before seeing the page.
- NOTHING on the page is hardcoded in the frontend. Every item (logo, buttons,
  menu links, slides, slide images/videos, stats, colours of stat boxes, section
  heading) is stored in PostgreSQL, managed in Django Admin, and delivered to
  Next.js through a REST API.
- The slideshow supports one or many slides; each slide can contain one image,
  one video, or several images/videos shown side by side (like the 3 photos in
  the screenshot). Videos can be uploaded files (.mp4/.webm), direct video URLs
  or YouTube links.
- Starting content (texts, links, logo, a Butaro Dialogues photo and a UGHE
  YouTube video) was taken from https://ughe.org.


2. TECHNOLOGY
-------------
Backend : Python 3.12, Django 5.2, Django REST Framework (token authentication),
          django-cors-headers, psycopg2 (PostgreSQL), Pillow
Frontend: Next.js 14 (App Router), React 18
Database: PostgreSQL 16
Tooling : Docker + Docker Compose
Font    : Roboto Slab (see section 7)


3. PROJECT STRUCTURE
--------------------
ughe-test-web-app/
  README.txt                 <- this file
  Makefile                   <- shortcuts (make up / make down / make logs)
  ughe-backend/              <- GitHub repo 1 (Django)
    docker-compose.yml       <- runs db + backend + frontend together
    Dockerfile, entrypoint.sh
    requirements.txt         <- Python libraries used
    config/                  <- Django project settings and URLs
    cms/models.py            <- content models (what you edit in admin)
    cms/admin.py             <- Django Admin configuration
    cms/serializers.py       <- JSON format of the API
    cms/views.py             <- login / logout / homepage API endpoints
    cms/management/commands/seed_ughe.py  <- creates users + starting content
  ughe-frontend/             <- GitHub repo 2 (Next.js)
    Dockerfile
    app/layout.js            <- font loading (with comments)
    app/globals.css          <- colours and layout matching the screenshot
    app/login/page.js        <- login page
    app/page.js              <- homepage (protected)
    components/Header.js, HeroSlideshow.js, FactsStats.js
    lib/api.js               <- REST API client


4. PREDEFINED CREDENTIALS
-------------------------
Web app login (http://localhost:3000):
    username: ughe
    password: UgheTest@2026

Django Admin (http://localhost:8000/admin):
    username: admin
    password: UgheAdmin@2026

Both can be changed through environment variables (see ughe-backend/.env.example).
They are created automatically when the backend container starts.


5. HOW TO RUN WITH DOCKER (recommended)
---------------------------------------
Requirements: Docker Desktop (or Docker Engine + Compose plugin) and Git.

a) Put both folders side by side (they already are in this package):
       some-folder/ughe-backend
       some-folder/ughe-frontend
   If cloning from GitHub:
       git clone https://github.com/<your-username>/ughe-backend.git
       git clone https://github.com/<your-username>/ughe-frontend.git

b) Start everything:
       cd ughe-backend
       docker compose up --build
   (or, from the parent folder: make up)

   The first build takes a few minutes. The backend waits for PostgreSQL,
   runs migrations, creates the users and loads the starting content.

c) Open:
       Web app      : http://localhost:3000   (log in with ughe / UgheTest@2026)
       Django Admin : http://localhost:8000/admin
       API          : http://localhost:8000/api/homepage/  (needs a token)

d) Stop:
       docker compose down          (keeps the database)
       docker compose down -v       (also deletes the database and uploads)

Ports used: 3000 (Next.js), 8000 (Django), 5433 (PostgreSQL on your machine).


6. HOW TO RUN WITHOUT DOCKER (optional)
---------------------------------------
Backend (needs Python 3.10+ and a running PostgreSQL):
    createdb ughe_db        (or create it in pgAdmin; user/password below)
    cd ughe-backend
    python -m venv venv
    venv\Scripts\activate            (Windows)  |  source venv/bin/activate (Mac/Linux)
    pip install -r requirements.txt
    set environment variables if yours differ from the defaults:
        POSTGRES_DB=ughe_db POSTGRES_USER=ughe_user POSTGRES_PASSWORD=ughe_password
        POSTGRES_HOST=localhost POSTGRES_PORT=5432
    python manage.py migrate
    python manage.py seed_ughe
    python manage.py runserver 8000

Frontend (needs Node.js 18.17+):
    cd ughe-frontend
    copy .env.example to .env.local  (NEXT_PUBLIC_API_URL=http://localhost:8000)
    npm install
    npm run dev                       -> http://localhost:3000


7. FONT
-------
The preferred font, Museo Slab, is a commercial font (exljbris / Adobe Fonts) and
cannot be bundled freely, so the allowed alternative Roboto Slab is used.
- Found on Google Fonts: https://fonts.google.com/specimen/Roboto+Slab
- Included with Next.js' built-in "next/font/google" in ughe-frontend/app/layout.js;
  Next.js downloads it at build time and self-hosts it.
- Applied through the CSS variable --font-slab in app/globals.css, with
  Rockwell and Courier as fallbacks.
Comments in both files explain this.


8. MANAGING CONTENT (Django Admin)
----------------------------------
Log in at http://localhost:8000/admin, then:
- Site settings      : logo (upload or URL), logo link, show/hide search,
                       "Facts & Stats" heading.
- Top buttons        : APPLY, GET INVOLVED, ... (label, link, order, active).
- Navigation items   : main menu; open an item to add its dropdown links.
- Slideshow slides   : caption, button text/link, duration, overlay darkness.
                       In "Slide images / videos" add one or more items:
                       choose Image or Video, then upload a file OR paste a URL
                       (image URL, .mp4 URL or YouTube link).
- Facts / stats      : value (e.g. 128, 1,260, 4TH), text, box colour.
Use "order" to change positions and untick "is active" to hide an item.
Refresh http://localhost:3000 to see changes.

To reset to the starting content:
    docker compose exec backend python manage.py seed_ughe --reset


9. REST API
-----------
POST /api/auth/login/    body {"username","password"} -> {"token","username"}
POST /api/auth/logout/   header Authorization: Token <token>
GET  /api/auth/me/       header Authorization: Token <token>
GET  /api/homepage/      header Authorization: Token <token>
                         -> settings, top_buttons, nav_items, slides, stats
Requests without a valid token get 401.


11. DEPLOYMENT NOTES
--------------------
For a real server: set DJANGO_DEBUG=0, a strong DJANGO_SECRET_KEY, real
DJANGO_ALLOWED_HOSTS and CORS_ALLOWED_ORIGINS, serve Django with gunicorn behind
nginx (nginx also serving /media and /static), and build the frontend with
NEXT_PUBLIC_API_URL set to the public API address.


12. APPROACH
------------
1. Studied the screenshot and https://ughe.org to list every visible element
   and the real texts, links, logo, photo and video.
2. Designed Django models so each element is an editable record (singleton
   settings, ordered/activatable buttons, nested menu, slides with many media,
   stats with colours), configured Django Admin with inlines for easy editing.
3. Built one REST endpoint returning all homepage data, protected by DRF token
   authentication, plus login/logout endpoints. Predefined users and starting
   content are created by a management command that never overwrites admin
   edits.
4. Built the Next.js pages (login + protected homepage) and components that
   only render what the API returns, with CSS colours and positions matched to
   the screenshot and Roboto Slab as the font.
5. Containerised PostgreSQL, Django and Next.js with Docker Compose and tested
   login, token protection, the API and the rendered page.
Resources used: Django, DRF, Next.js and Docker documentation, Google Fonts,
ughe.org, and an AI coding assistant (Claude) to help generate and review code.


13. TROUBLESHOOTING
-------------------
- "Cannot reach the server" on login: the backend is not up yet; check
  "docker compose logs backend".
- Port already in use: stop the program using 3000/8000/5433 or change the
  left-hand port numbers in docker-compose.yml.
- Windows "entrypoint.sh not found": the Dockerfile already converts line
  endings; rebuild with "docker compose build --no-cache backend".
- Images not showing: the starting images/video load from ughe.org and
  YouTube, so an internet connection is needed (or upload files in admin).
