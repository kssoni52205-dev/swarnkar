from flask import (
    Flask,
    request,
    redirect,
    render_template_string,
    flash,
    session,
    url_for,
    send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
from functools import wraps
from datetime import datetime
import sqlite3
import os
import uuid


# ============================================================
# BASIC SETTINGS
# ============================================================

APP_DIR = Path(__file__).resolve().parent
DB = APP_DIR / "swarnkar_samaj.db"

# IMPORTANT:
# static folder GitHub me manually banana hai.
# Code ise create nahi karega.
STATIC_DIR = APP_DIR / "static"

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)

app.secret_key = os.environ.get(
    "SAMAJ_SECRET_KEY",
    "swarnkar-samaj-secret-2026"
)

ADMIN_USER = os.environ.get(
    "SAMAJ_ADMIN_USER",
    "admin"
)

ADMIN_PASSWORD = os.environ.get(
    "SAMAJ_ADMIN_PASSWORD",
    "1234"
)

ADMIN_PASSWORD_HASH = generate_password_hash(
    ADMIN_PASSWORD
)


# ============================================================
# DATABASE
# ============================================================

def db():
    con = sqlite3.connect(DB, timeout=30)
    con.row_factory = sqlite3.Row
    return con


def setup():
    con = db()

    con.executescript("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY CHECK(id=1),
        samaj_name TEXT DEFAULT 'मैढ़ स्वर्णकार समाज',
        location TEXT DEFAULT 'जोधपुर, राजस्थान',
        slogan TEXT DEFAULT 'एकता • सेवा • संस्कार • विकास',
        about TEXT DEFAULT '',
        bhawan_name TEXT DEFAULT 'समाज भवन',
        bhawan_address TEXT DEFAULT '',
        bhawan_details TEXT DEFAULT '',
        bhawan_phone TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        whatsapp TEXT DEFAULT '',
        email TEXT DEFAULT '',
        map_url TEXT DEFAULT '',
        donation_info TEXT DEFAULT '',
        upi_id TEXT DEFAULT '',
        hero_photo TEXT DEFAULT 'ajmeedhji_maharaj.jpg',
        bhagwan_photo TEXT DEFAULT 'bhagwan.jpg',
        bhawan_photo TEXT DEFAULT 'samaj_bhawan.jpg'
    );

    CREATE TABLE IF NOT EXISTS members(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        mobile TEXT DEFAULT '',
        city TEXT DEFAULT '',
        village TEXT DEFAULT '',
        occupation TEXT DEFAULT '',
        family TEXT DEFAULT '',
        photo TEXT DEFAULT '',
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS committee(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        post TEXT NOT NULL,
        mobile TEXT DEFAULT '',
        photo TEXT DEFAULT '',
        sort_order INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS businesses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        owner TEXT DEFAULT '',
        category TEXT DEFAULT '',
        mobile TEXT DEFAULT '',
        address TEXT DEFAULT '',
        description TEXT DEFAULT '',
        photo TEXT DEFAULT '',
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        event_date TEXT DEFAULT '',
        event_time TEXT DEFAULT '',
        venue TEXT DEFAULT '',
        description TEXT DEFAULT '',
        photo TEXT DEFAULT '',
        registration_url TEXT DEFAULT '',
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS news(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        news_date TEXT DEFAULT '',
        body TEXT DEFAULT '',
        photo TEXT DEFAULT '',
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS notices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT DEFAULT '',
        notice_date TEXT DEFAULT '',
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS education(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT DEFAULT '',
        icon TEXT DEFAULT '🎓',
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS gallery(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT DEFAULT '',
        category TEXT DEFAULT 'General',
        photo TEXT NOT NULL,
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS donations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_name TEXT NOT NULL,
        amount REAL DEFAULT 0,
        purpose TEXT DEFAULT '',
        mode TEXT DEFAULT 'UPI',
        note TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    row = con.execute(
        "SELECT id FROM settings WHERE id=1"
    ).fetchone()

    if not row:
        con.execute(
            """
            INSERT INTO settings(
                id,
                samaj_name,
                location,
                slogan
            )
            VALUES(1,?,?,?)
            """,
            (
                "मैढ़ स्वर्णकार समाज",
                "जोधपुर, राजस्थान",
                "एकता • सेवा • संस्कार • विकास"
            )
        )

    con.commit()
    con.close()


setup()


# ============================================================
# HELPERS
# ============================================================

def get_settings():
    con = db()

    row = con.execute(
        "SELECT * FROM settings WHERE id=1"
    ).fetchone()

    con.close()

    return row


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return view(*args, **kwargs)

    return wrapped


def safe(value):
    if value is None:
        return ""

    return str(value).replace(
        "&", "&amp;"
    ).replace(
        "<", "&lt;"
    ).replace(
        ">", "&gt;"
    ).replace(
        '"', "&quot;"
    )


def money(value):
    try:
        return "₹ {:,.2f}".format(float(value or 0))
    except Exception:
        return "₹ 0.00"


def image_url(filename):
    if not filename:
        return ""

    return url_for(
        "site_image",
        filename=filename
    )


def save_upload(file):
    """
    Admin uploaded image ko directly static/ folder me save karega.
    static folder GitHub me manually hona chahiye.
    """

    if not file or not file.filename:
        return ""

    ext = Path(
        file.filename
    ).suffix.lower()

    allowed = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif"
    }

    if ext not in allowed:
        raise ValueError(
            "Sirf JPG, JPEG, PNG, WEBP aur GIF allowed hai."
        )

    # static folder missing hai to clear error
    if not STATIC_DIR.exists():
        raise RuntimeError(
            "static folder missing hai. GitHub me static naam ka folder banao."
        )

    if not STATIC_DIR.is_dir():
        raise RuntimeError(
            "static ek folder hona chahiye, file nahi."
        )

    filename = (
        "upload_"
        + uuid.uuid4().hex
        + ext
    )

    file.save(
        STATIC_DIR / filename
    )

    return filename


# ============================================================
# SITE IMAGE ROUTE
# ============================================================

@app.route("/site-image/<path:filename>")
def site_image(filename):
    return send_from_directory(
        STATIC_DIR,
        filename
    )


# ============================================================
# PUBLIC HTML
# ============================================================

PUBLIC_HTML = """
<!DOCTYPE html>

<html lang="hi">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>
{{ title }} - {{ s['samaj_name'] }}
</title>

<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    font-family:
        "Segoe UI",
        "Noto Sans Devanagari",
        Arial,
        sans-serif;

    color:#2d1909;

    background:
        radial-gradient(
            circle at top left,
            #fff0b8,
            transparent 25%
        ),
        linear-gradient(
            135deg,
            #fffdf8,
            #f4e4bb,
            #fffdf8
        );
}

header{
    position:sticky;
    top:0;
    z-index:999;

    background:
        linear-gradient(
            135deg,
            #150801,
            #5e350c,
            #a97016,
            #442105,
            #110400
        );

    border-bottom:3px solid #e1b43c;

    box-shadow:
        0 7px 28px #0004;
}

.header-inner{
    max-width:1450px;
    margin:auto;

    padding:13px 20px;

    display:flex;
    align-items:center;
    justify-content:space-between;

    gap:20px;
}

.brand{
    display:flex;
    align-items:center;
    gap:12px;
}

.logo{
    width:52px;
    height:52px;

    display:flex;
    align-items:center;
    justify-content:center;

    border-radius:50%;

    background:
        linear-gradient(
            135deg,
            #fff,
            #f3cb58
        );

    color:#885300;

    font-size:26px;

    border:2px solid #ffe394;
}

.brand h1{
    margin:0;
    color:#ffe59b;
    font-size:21px;
}

.brand p{
    margin:0;
    color:#fff1cb;
    font-size:12px;
}

nav{
    display:flex;
    flex-wrap:wrap;
    justify-content:center;
    gap:4px;
}

nav a{
    color:white;
    text-decoration:none;

    padding:8px 10px;

    border-radius:9px;

    font-size:12px;

    font-weight:800;

    transition:.25s;
}

nav a:hover{
    background:
        linear-gradient(
            135deg,
            #e9b83e,
            #fff0a5
        );

    color:#2a1604;

    transform:translateY(-2px);
}

.container{
    max-width:1250px;
    margin:auto;
    padding:45px 20px 70px;
}

.hero{
    min-height:560px;

    border-radius:28px;

    display:flex;
    align-items:center;
    justify-content:center;

    text-align:center;

    background:
        linear-gradient(
            rgba(20,8,0,.28),
            rgba(20,8,0,.72)
        ),
        url("/static/ajmeedhji_maharaj.jpg");

    background-size:cover;
    background-position:center;

    box-shadow:
        0 25px 60px #5e3c161f;
}

.hero-box{
    width:min(950px,92%);

    padding:35px;

    border-radius:28px;

    color:white;

    background:
        rgba(12,5,1,.25);

    backdrop-filter:blur(8px);

    border:
        1px solid rgba(255,255,255,.2);
}

.hero-box h2{
    margin:10px 0;

    color:#fff2ae;

    font-size:
        clamp(
            38px,
            7vw,
            76px
        );

    line-height:1.1;
}

.hero-box h3{
    font-size:28px;
    font-weight:500;
}

.hero-box p{
    font-size:18px;
    color:#fff6da;
}

.badge{
    display:inline-block;

    padding:8px 18px;

    border-radius:999px;

    background:#ffffff22;

    border:1px solid #ffffff55;

    color:#ffe28f;

    font-weight:800;
}

.buttons{
    display:flex;
    flex-wrap:wrap;
    align-items:center;
    gap:10px;
}

.center{
    justify-content:center;
}

.btn{
    display:inline-block;

    border:0;
    text-decoration:none;
    cursor:pointer;

    padding:11px 16px;

    border-radius:10px;

    font-weight:800;

    transition:.25s;
}

.btn:hover{
    transform:translateY(-3px);
    filter:brightness(1.07);
}

.gold{
    background:
        linear-gradient(
            135deg,
            #d69d1a,
            #f5d66d
        );

    color:#291605;
}

.green{
    background:
        linear-gradient(
            135deg,
            #108348,
            #2bc979
        );

    color:white;
}

.blue{
    background:
        linear-gradient(
            135deg,
            #2159c4,
            #5f94ff
        );

    color:white;
}

.red{
    background:
        linear-gradient(
            135deg,
            #a91d37,
            #df5065
        );

    color:white;
}

.purple{
    background:
        linear-gradient(
            135deg,
            #633bb5,
            #a47cf0
        );

    color:white;
}

.panel{
    background:#ffffffee;

    padding:25px;

    margin-bottom:22px;

    border-radius:22px;

    border:1px solid #ead8aa;

    box-shadow:
        0 13px 35px #754b1011;
}

.panel h2{
    margin-top:0;
    color:#6f4300;
}

.card-grid{
    display:grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                235px,
                1fr
            )
        );

    gap:18px;
}

.card{
    background:white;

    padding:20px;

    border-radius:18px;

    border:
        1px solid #ead6a7;

    border-left:
        5px solid #d5a32b;

    box-shadow:
        0 9px 25px #66400d0d;

    transition:.25s;
}

.card:hover{
    transform:translateY(-5px);

    box-shadow:
        0 15px 35px #66400d18;
}

.card h3{
    color:#714500;
}

.card p{
    color:#635b52;
}

.card img{
    width:100%;
    height:210px;

    object-fit:cover;

    border-radius:14px;

    margin-bottom:10px;
}

.large-photo{
    width:100%;
    max-height:500px;

    object-fit:cover;

    border-radius:22px;

    border:4px solid #f0dda1;
}

.two{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:20px;
}

.gallery{
    display:grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                210px,
                1fr
            )
        );

    gap:15px;
}

.gallery-item{
    background:white;

    border-radius:18px;

    overflow:hidden;

    box-shadow:
        0 10px 28px #70491012;
}

.gallery-item img{
    width:100%;
    height:220px;

    object-fit:cover;

    display:block;
}

.gallery-item div{
    padding:12px;

    color:#704500;

    font-weight:800;
}

footer{
    text-align:center;

    padding:40px 20px;

    background:
        linear-gradient(
            135deg,
            #160701,
            #492406,
            #160701
        );

    color:#ffe59a;

    border-top:3px solid #d7a932;
}

footer p{
    color:#d8cabb;
}

.form-grid{
    display:grid;

    grid-template-columns:
        repeat(
            2,
            1fr
        );

    gap:12px;
}

input,
select,
textarea{

    width:100%;

    padding:11px;

    border:
        1px solid #d5bf8d;

    border-radius:9px;

    background:#fffdf8;

    font-size:14px;
}

textarea{
    min-height:110px;
}

.full{
    grid-column:1/-1;
}

.alert{
    padding:12px;

    border-radius:9px;

    margin-bottom:15px;

    background:#dff2e5;

    color:#17633b;

    font-weight:700;
}

.alert.error{
    background:#ffe0e4;

    color:#8b2032;
}

@media(max-width:950px){

    .header-inner{
        flex-direction:column;
    }

    .two{
        grid-template-columns:1fr;
    }

}

@media(max-width:650px){

    .container{
        padding:
            22px 12px 55px;
    }

    .hero{
        min-height:500px;
        border-radius:20px;
    }

    .hero-box{
        padding:25px 15px;
        border-radius:20px;
    }

    nav a{
        font-size:10px;
        padding:7px 8px;
    }

    .form-grid{
        grid-template-columns:1fr;
    }

    .full{
        grid-column:auto;
    }

}

</style>

</head>

<body>

<header>

<div class="header-inner">

<div class="brand">

<div class="logo">
ॐ
</div>

<div>

<h1>
{{ s['samaj_name'] }}
</h1>

<p>
{{ s['location'] }}
</p>

</div>

</div>

<nav>

<a href="{{ url_for('home') }}">🏠 Home</a>

<a href="{{ url_for('about') }}">🏛️ समाज</a>

<a href="{{ url_for('bhawan') }}">🏢 भवन</a>

<a href="{{ url_for('members') }}">👥 सदस्य</a>

<a href="{{ url_for('committee') }}">👔 समिति</a>

<a href="{{ url_for('businesses') }}">🏪 व्यवसाय</a>

<a href="{{ url_for('events') }}">🎉 कार्यक्रम</a>

<a href="{{ url_for('news') }}">📰 समाचार</a>

<a href="{{ url_for('education') }}">🎓 शिक्षा</a>

<a href="{{ url_for('gallery') }}">📸 Gallery</a>

<a href="{{ url_for('donation') }}">❤️ सहयोग</a>

<a href="{{ url_for('contact') }}">📞 Contact</a>

</nav>

</div>

</header>


<div class="container">

{{ body|safe }}

</div>


<footer>

<h2>
💎 {{ s['samaj_name'] }}
</h2>

<p>
{{ s['location'] }}
</p>

<p>
{{ s['slogan'] }}
</p>

<p>
🙏 जय अजमीढ़ जी महाराज 🙏
</p>

</footer>

</body>

</html>
"""


def public_page(title, body):
    return render_template_string(
        PUBLIC_HTML,
        title=title,
        body=body,
        s=get_settings()
    )


# ============================================================
# ADMIN HTML
# ============================================================

ADMIN_HTML = """

<!DOCTYPE html>

<html lang="hi">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>
Admin - मैढ़ स्वर्णकार समाज
</title>

<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;

    font-family:
        "Segoe UI",
        Arial,
        sans-serif;

    background:
        linear-gradient(
            135deg,
            #fffaf1,
            #edd28b
        );

    color:#2e1909;
}

.top{
    background:
        linear-gradient(
            135deg,
            #170800,
            #623709,
            #170800
        );

    color:#ffe59a;

    padding:18px;

    text-align:center;

    border-bottom:
        3px solid #d8a930;
}

.layout{
    display:flex;

    min-height:
        calc(100vh - 90px);
}

.sidebar{
    width:245px;

    background:#241106;

    padding:15px;
}

.sidebar a{
    display:block;

    text-decoration:none;

    color:white;

    padding:11px;

    margin-bottom:6px;

    border-radius:9px;

    font-weight:800;
}

.sidebar a:hover{
    background:#d7a82f;
    color:#241306;
}

.main{
    flex:1;

    padding:22px;

    min-width:0;
}

.panel{
    background:white;

    padding:20px;

    margin-bottom:18px;

    border-radius:17px;

    box-shadow:
        0 9px 28px #60401014;
}

.grid{
    display:grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                220px,
                1fr
            )
        );

    gap:13px;
}

.form-grid{
    display:grid;

    grid-template-columns:
        repeat(
            2,
            1fr
        );

    gap:12px;
}

.full{
    grid-column:1/-1;
}

input,
select,
textarea{
    width:100%;

    padding:10px;

    border:
        1px solid #d6c18f;

    border-radius:8px;

    background:#fffdf8;
}

textarea{
    min-height:110px;
}

.btn{
    border:0;

    border-radius:8px;

    padding:10px 14px;

    font-weight:800;

    cursor:pointer;

    display:inline-block;

    text-decoration:none;
}

.gold{
    background:#d7a82e;
    color:#241305;
}

.green{
    background:#16864c;
    color:white;
}

.red{
    background:#b5273e;
    color:white;
}

.blue{
    background:#2c67d1;
    color:white;
}

.preview{
    width:90px;
    height:65px;

    object-fit:cover;

    border-radius:8px;
}

table{
    width:100%;
    border-collapse:collapse;
}

th{
    background:#47250f;

    color:#ffe79c;

    padding:10px;

    text-align:left;
}

td{
    padding:9px;

    border-bottom:
        1px solid #eee2c8;
}

.alert{
    padding:12px;

    background:#dff2e5;

    border-radius:9px;

    margin-bottom:12px;
}

.alert.error{
    background:#ffe0e4;
    color:#8b2132;
}

@media(max-width:800px){

    .layout{
        display:block;
    }

    .sidebar{
        width:100%;
    }

    .form-grid{
        grid-template-columns:1fr;
    }

}

</style>

</head>

<body>

<div class="top">

<h1>
💎 मैढ़ स्वर्णकार समाज
</h1>

<p>
Admin Panel
</p>

</div>

<div class="layout">

<aside class="sidebar">

<a href="{{ url_for('admin_dashboard') }}">
📊 Dashboard
</a>

<a href="{{ url_for('admin_settings') }}">
⚙️ Society Details
</a>

<a href="{{ url_for('admin_members') }}">
👥 Members
</a>

<a href="{{ url_for('admin_committee') }}">
👔 Committee
</a>

<a href="{{ url_for('admin_businesses') }}">
🏪 Businesses
</a>

<a href="{{ url_for('admin_events') }}">
🎉 Events
</a>

<a href="{{ url_for('admin_news') }}">
📰 News
</a>

<a href="{{ url_for('admin_notices') }}">
📢 Notices
</a>

<a href="{{ url_for('admin_education') }}">
🎓 Education
</a>

<a href="{{ url_for('admin_gallery') }}">
📸 Gallery
</a>

<a href="{{ url_for('admin_donations') }}">
❤️ Donations
</a>

<a
    href="{{ url_for('home') }}"
    target="_blank"
>
🌐 Website
</a>

<a href="{{ url_for('admin_logout') }}">
🚪 Logout
</a>

</aside>

<main class="main">

{% with messages=get_flashed_messages(
    with_categories=true
) %}

{% for category, message in messages %}

<div
    class="alert
    {% if category == 'error' %}
    error
    {% endif %}"
>
{{ message }}
</div>

{% endfor %}

{% endwith %}

{{ body|safe }}

</main>

</div>

</body>

</html>
"""


def admin_page(title, body):
    return render_template_string(
        ADMIN_HTML,
        title=title,
        body=body
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    con = db()

    settings = get_settings()

    notices = con.execute(
        """
        SELECT *
        FROM notices
        WHERE active=1
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    events_rows = con.execute(
        """
        SELECT *
        FROM events
        WHERE active=1
        ORDER BY id DESC
        LIMIT 3
        """
    ).fetchall()

    news_rows = con.execute(
        """
        SELECT *
        FROM news
        WHERE active=1
        ORDER BY id DESC
        LIMIT 3
        """
    ).fetchall()

    gallery_rows = con.execute(
        """
        SELECT *
        FROM gallery
        WHERE active=1
        ORDER BY id DESC
        LIMIT 6
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="hero">

            <div class="hero-box">

                <div class="badge">
                    🙏 जय अजमीढ़ जी महाराज 🙏
                </div>

                <h2>
                    {{ settings['samaj_name'] }}
                </h2>

                <h3>
                    {{ settings['location'] }}
                </h3>

                <p>
                    {{ settings['slogan'] }}
                </p>

                <br>

                <div class="buttons center">

                    <a
                        class="btn gold"
                        href="{{ url_for('about') }}"
                    >
                        🏛️ समाज के बारे में
                    </a>

                    <a
                        class="btn blue"
                        href="{{ url_for('bhawan') }}"
                    >
                        🏢 समाज भवन
                    </a>

                    <a
                        class="btn green"
                        href="{{ url_for('events') }}"
                    >
                        🎉 कार्यक्रम
                    </a>

                </div>

            </div>

        </div>


        <div class="panel">

            <h2>
                📢 महत्वपूर्ण सूचनाएँ
            </h2>

            <br>

            <div class="card-grid">

            {% for n in notices %}

                <div class="card">

                    <h3>
                        {{ n['title'] }}
                    </h3>

                    <p>
                        {{ n['body'] }}
                    </p>

                    <small>
                        {{ n['notice_date'] }}
                    </small>

                </div>

            {% else %}

                <div class="card">
                    अभी कोई सूचना नहीं है।
                </div>

            {% endfor %}

            </div>

        </div>


        <div class="panel">

            <h2>
                🎉 नवीन कार्यक्रम
            </h2>

            <br>

            <div class="card-grid">

            {% for e in events_rows %}

                <div class="card">

                    {% if e['photo'] %}

                    <img
                        src="{{ image_url(e['photo']) }}"
                        alt="{{ e['title'] }}"
                    >

                    {% endif %}

                    <h3>
                        {{ e['title'] }}
                    </h3>

                    <p>
                        📅 {{ e['event_date'] }}
                    </p>

                    <p>
                        📍 {{ e['venue'] }}
                    </p>

                </div>

            {% else %}

                <div class="card">
                    अभी कोई कार्यक्रम नहीं है।
                </div>

            {% endfor %}

            </div>

            <br>

            <a
                class="btn gold"
                href="{{ url_for('events') }}"
            >
                सभी कार्यक्रम देखें →
            </a>

        </div>


        <div class="panel">

            <h2>
                📰 नवीन समाचार
            </h2>

            <br>

            <div class="card-grid">

            {% for n in news_rows %}

                <div class="card">

                    {% if n['photo'] %}

                    <img
                        src="{{ image_url(n['photo']) }}"
                    >

                    {% endif %}

                    <h3>
                        {{ n['title'] }}
                    </h3>

                    <p>
                        {{ n['body'] }}
                    </p>

                </div>

            {% else %}

                <div class="card">
                    अभी कोई समाचार नहीं है।
                </div>

            {% endfor %}

            </div>

        </div>


        <div class="panel">

            <h2>
                📸 नवीन Gallery
            </h2>

            <br>

            <div class="gallery">

            {% for g in gallery_rows %}

                <div class="gallery-item">

                    <img
                        src="{{ image_url(g['photo']) }}"
                    >

                    <div>
                        {{ g['title'] }}
                    </div>

                </div>

            {% else %}

                <div class="card">
                    अभी Gallery खाली है।
                </div>

            {% endfor %}

            </div>

        </div>
        """,

        settings=settings,

        notices=notices,

        events_rows=events_rows,

        news_rows=news_rows,

        gallery_rows=gallery_rows,

        image_url=image_url
    )

    return public_page(
        "Home",
        body
    )


# ============================================================
# ABOUT
# ============================================================

@app.route("/about")
def about():

    s = get_settings()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                🏛️ समाज के बारे में
            </h2>

            <br>

            <p>
                {{ s['about'] or
                'समाज का परिचय Admin Panel से भरा जाएगा।' }}
            </p>

        </div>

        <div class="buttons">

            <a
                class="btn gold"
                href="{{ url_for('committee') }}"
            >
                👔 समाज समिति
            </a>

            <a
                class="btn blue"
                href="{{ url_for('members') }}"
            >
                👥 समाज सदस्य
            </a>

        </div>
        """,
        s=s
    )

    return public_page(
        "समाज के बारे में",
        body
    )


# ============================================================
# BHAWAN
# ============================================================

@app.route("/bhawan")
def bhawan():

    s = get_settings()

    photo = (
        s["bhawan_photo"]
        or "samaj_bhawan.jpg"
    )

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                🏢 {{ s['bhawan_name'] }}
            </h2>

            <br>

            <img
                class="large-photo"
                src="{{ image_url(photo) }}"
                alt="समाज भवन"
            >

            <br><br>

            <h3>
                📍 Address
            </h3>

            <p>
                {{ s['bhawan_address'] or '-' }}
            </p>

            <br>

            <h3>
                ℹ️ भवन की जानकारी
            </h3>

            <p>
                {{ s['bhawan_details'] or
                'भवन की जानकारी Admin Panel से भरी जाएगी।' }}
            </p>

            <br>

            <h3>
                📞 Contact
            </h3>

            <p>
                {{ s['bhawan_phone'] or '-' }}
            </p>

        </div>
        """,
        s=s,
        photo=photo,
        image_url=image_url
    )

    return public_page(
        "समाज भवन",
        body
    )


# ============================================================
# MEMBERS
# ============================================================

@app.route("/members")
def members():

    con = db()

    rows = con.execute(
        """
        SELECT *
        FROM members
        WHERE active=1
        ORDER BY name
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                👥 समाज सदस्य
            </h2>

        </div>

        <div class="card-grid">

        {% for m in rows %}

            <div class="card">

                {% if m['photo'] %}

                <img
                    src="{{ image_url(m['photo']) }}"
                >

                {% endif %}

                <h3>
                    {{ m['name'] }}
                </h3>

                <p>
                    <b>शहर:</b>
                    {{ m['city'] }}
                </p>

                <p>
                    <b>गांव:</b>
                    {{ m['village'] }}
                </p>

                <p>
                    <b>व्यवसाय:</b>
                    {{ m['occupation'] }}
                </p>

                {% if m['mobile'] %}

                <br>

                <a
                    class="btn green"
                    href="tel:{{ m['mobile'] }}"
                >
                    📞 Contact
                </a>

                {% endif %}

            </div>

        {% else %}

            <div class="card">
                अभी सदस्य जानकारी उपलब्ध नहीं है।
            </div>

        {% endfor %}

        </div>
        """,
        rows=rows,
        image_url=image_url
    )

    return public_page(
        "समाज सदस्य",
        body
    )


# ============================================================
# COMMITTEE
# ============================================================

@app.route("/committee")
def committee():

    con = db()

    rows = con.execute(
        """
        SELECT *
        FROM committee
        WHERE active=1
        ORDER BY sort_order,name
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                👔 समाज समिति
            </h2>

        </div>

        <div class="card-grid">

        {% for c in rows %}

            <div class="card">

                {% if c['photo'] %}

                <img
                    src="{{ image_url(c['photo']) }}"
                >

                {% endif %}

                <h3>
                    {{ c['name'] }}
                </h3>

                <p>
                    <b>पद:</b>
                    {{ c['post'] }}
                </p>

                {% if c['mobile'] %}

                <p>
                    📞 {{ c['mobile'] }}
                </p>

                {% endif %}

            </div>

        {% else %}

            <div class="card">
                अभी committee details उपलब्ध नहीं हैं।
            </div>

        {% endfor %}

        </div>
        """,
        rows=rows,
        image_url=image_url
    )

    return public_page(
        "समाज समिति",
        body
    )


# ============================================================
# BUSINESSES
# ============================================================

@app.route("/businesses")
def businesses():

    con = db()

    rows = con.execute(
        """
        SELECT *
        FROM businesses
        WHERE active=1
        ORDER BY name
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                🏪 व्यापार / व्यवसाय
            </h2>

        </div>

        <div class="card-grid">

        {% for b in rows %}

            <div class="card">

                {% if b['photo'] %}

                <img
                    src="{{ image_url(b['photo']) }}"
                >

                {% endif %}

                <h3>
                    {{ b['name'] }}
                </h3>

                <p>
                    <b>संचालक:</b>
                    {{ b['owner'] }}
                </p>

                <p>
                    <b>Category:</b>
                    {{ b['category'] }}
                </p>

                <p>
                    <b>Address:</b>
                    {{ b['address'] }}
                </p>

                <p>
                    {{ b['description'] }}
                </p>

                {% if b['mobile'] %}

                <br>

                <a
                    class="btn green"
                    href="tel:{{ b['mobile'] }}"
                >
                    📞 Contact
                </a>

                {% endif %}

            </div>

        {% else %}

            <div class="card">
                अभी business directory खाली है।
            </div>

        {% endfor %}

        </div>
        """,
        rows=rows,
        image_url=image_url
    )

    return public_page(
        "व्यवसाय",
        body
    )


# ============================================================
# EVENTS
# ============================================================

@app.route("/events")
def events():

    con = db()

    rows = con.execute(
        """
        SELECT *
        FROM events
        WHERE active=1
        ORDER BY id DESC
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                🎉 समाज के कार्यक्रम
            </h2>

        </div>

        <div class="card-grid">

        {% for e in rows %}

            <div class="card">

                {% if e['photo'] %}

                <img
                    src="{{ image_url(e['photo']) }}"
                >

                {% endif %}

                <h3>
                    {{ e['title'] }}
                </h3>

                <p>
                    📅 {{ e['event_date'] }}
                </p>

                <p>
                    ⏰ {{ e['event_time'] }}
                </p>

                <p>
                    📍 {{ e['venue'] }}
                </p>

                <p>
                    {{ e['description'] }}
                </p>

                {% if e['registration_url'] %}

                <br>

                <a
                    class="btn green"
                    target="_blank"
                    href="{{ e['registration_url'] }}"
                >
                    📝 Registration
                </a>

                {% endif %}

            </div>

        {% else %}

            <div class="card">
                अभी कोई कार्यक्रम नहीं है।
            </div>

        {% endfor %}

        </div>
        """,
        rows=rows,
        image_url=image_url
    )

    return public_page(
        "कार्यक्रम",
        body
    )


# ============================================================
# NEWS
# ============================================================

@app.route("/news")
def news():

    con = db()

    rows = con.execute(
        """
        SELECT *
        FROM news
        WHERE active=1
        ORDER BY id DESC
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                📰 समाचार एवं सूचनाएँ
            </h2>

        </div>

        <div class="card-grid">

        {% for n in rows %}

            <div class="card">

                {% if n['photo'] %}

                <img
                    src="{{ image_url(n['photo']) }}"
                >

                {% endif %}

                <h3>
                    {{ n['title'] }}
                </h3>

                <small>
                    {{ n['news_date'] }}
                </small>

                <p>
                    {{ n['body'] }}
                </p>

            </div>

        {% else %}

            <div class="card">
                अभी कोई समाचार नहीं है।
            </div>

        {% endfor %}

        </div>
        """,
        rows=rows,
        image_url=image_url
    )

    return public_page(
        "समाचार",
        body
    )


# ============================================================
# EDUCATION
# ============================================================

@app.route("/education")
def education():

    con = db()

    rows = con.execute(
        """
        SELECT *
        FROM education
        WHERE active=1
        ORDER BY id DESC
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                🎓 शिक्षा एवं सहायता
            </h2>

        </div>

        <div class="card-grid">

        {% for e in rows %}

            <div class="card">

                <div
                    style="
                        font-size:45px;
                        margin-bottom:10px;
                    "
                >
                    {{ e['icon'] }}
                </div>

                <h3>
                    {{ e['title'] }}
                </h3>

                <p>
                    {{ e['body'] }}
                </p>

            </div>

        {% else %}

            <div class="card">
                अभी education details उपलब्ध नहीं हैं।
            </div>

        {% endfor %}

        </div>
        """,
        rows=rows
    )

    return public_page(
        "शिक्षा",
        body
    )


# ============================================================
# GALLERY
# ============================================================

@app.route("/gallery")
def gallery():

    con = db()

    rows = con.execute(
        """
        SELECT *
        FROM gallery
        WHERE active=1
        ORDER BY id DESC
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                📸 समाज Gallery
            </h2>

            <p>
                समाज भवन, धार्मिक एवं कार्यक्रमों की तस्वीरें
            </p>

        </div>

        <div class="gallery">

        {% for g in rows %}

            <div class="gallery-item">

                <img
                    src="{{ image_url(g['photo']) }}"
                    alt="{{ g['title'] }}"
                >

                <div>

                    {{ g['title'] }}

                    {% if g['category'] %}

                    <br>

                    <small>
                        {{ g['category'] }}
                    </small>

                    {% endif %}

                </div>

            </div>

        {% else %}

            <div class="card">
                अभी Gallery खाली है।
            </div>

        {% endfor %}

        </div>
        """,
        rows=rows,
        image_url=image_url
    )

    return public_page(
        "Gallery",
        body
    )


# ============================================================
# DONATION
# ============================================================

@app.route(
    "/donation",
    methods=["GET", "POST"]
)
def donation():

    s = get_settings()

    if request.method == "POST":

        try:

            name = request.form.get(
                "name",
                ""
            ).strip()

            amount = float(
                request.form.get(
                    "amount",
                    "0"
                ) or 0
            )

            purpose = request.form.get(
                "purpose",
                ""
            ).strip()

            mode = request.form.get(
                "mode",
                "UPI"
            )

            note = request.form.get(
                "note",
                ""
            ).strip()

            if not name:
                raise ValueError(
                    "Donor name zaroori hai."
                )

            if amount <= 0:
                raise ValueError(
                    "Valid amount dalo."
                )

            con = db()

            con.execute(
                """
                INSERT INTO donations(
                    donor_name,
                    amount,
                    purpose,
                    mode,
                    note
                )
                VALUES(?,?,?,?,?)
                """,
                (
                    name,
                    amount,
                    purpose,
                    mode,
                    note
                )
            )

            con.commit()
            con.close()

            flash(
                "Donation information save ho gayi.",
                "success"
            )

            return redirect(
                url_for("donation")
            )

        except Exception as e:

            flash(
                str(e),
                "error"
            )

    body = render_template_string(
        """
        {% with messages=get_flashed_messages(
            with_categories=true
        ) %}

        {% for category,message in messages %}

        <div
            class="alert
            {% if category == 'error' %}
            error
            {% endif %}"
        >
            {{ message }}
        </div>

        {% endfor %}

        {% endwith %}


        <div class="panel">

            <h2>
                ❤️ समाज के लिए सहयोग
            </h2>

            <p>
                {{ s['donation_info'] or
                'समाज के विकास और सेवा कार्यों में सहयोग करें।' }}
            </p>

            <br>

            <h3>
                UPI ID
            </h3>

            <p>
                {{ s['upi_id'] or '-' }}
            </p>

        </div>


        <div class="panel">

            <h2>
                Donation Record
            </h2>

            <br>

            <form method="post">

                <div class="two">

                    <div>

                        <label>
                            Donor Name
                        </label>

                        <input
                            name="name"
                            required
                        >

                    </div>

                    <div>

                        <label>
                            Amount
                        </label>

                        <input
                            type="number"
                            step="0.01"
                            min="1"
                            name="amount"
                            required
                        >

                    </div>

                    <div>

                        <label>
                            Purpose
                        </label>

                        <input name="purpose">

                    </div>

                    <div>

                        <label>
                            Mode
                        </label>

                        <select name="mode">

                            <option>
                                UPI
                            </option>

                            <option>
                                Cash
                            </option>

                            <option>
                                Bank
                            </option>

                            <option>
                                Cheque
                            </option>

                        </select>

                    </div>

                </div>

                <br>

                <label>
                    Note
                </label>

                <textarea name="note"></textarea>

                <br><br>

                <button
                    class="btn green"
                    type="submit"
                >
                    ❤️ Submit
                </button>

            </form>

        </div>
        """,
        s=s
    )

    return public_page(
        "Donation",
        body
    )


# ============================================================
# CONTACT
# ============================================================

@app.route("/contact")
def contact():

    s = get_settings()

    body = render_template_string(
        """
        <div class="card-grid">

            <div class="card">

                <h3>
                    📍 पता
                </h3>

                <p>
                    {{ s['bhawan_address'] or
                    s['location'] }}
                </p>

            </div>


            <div class="card">

                <h3>
                    📞 Phone
                </h3>

                <p>
                    {{ s['phone'] or '-' }}
                </p>

                {% if s['phone'] %}

                <br>

                <a
                    class="btn green"
                    href="tel:{{ s['phone'] }}"
                >
                    📞 Call
                </a>

                {% endif %}

            </div>


            <div class="card">

                <h3>
                    💬 WhatsApp
                </h3>

                <p>
                    {{ s['whatsapp'] or '-' }}
                </p>

                {% if s['whatsapp'] %}

                <br>

                <a
                    class="btn green"
                    target="_blank"
                    href="https://wa.me/{{ s['whatsapp']|replace('+','')|replace(' ','')|replace('-','') }}"
                >
                    💬 WhatsApp
                </a>

                {% endif %}

            </div>


            <div class="card">

                <h3>
                    📧 Email
                </h3>

                <p>
                    {{ s['email'] or '-' }}
                </p>

            </div>

        </div>


        {% if s['map_url'] %}

        <br>

        <div class="panel">

            <a
                class="btn blue"
                target="_blank"
                href="{{ s['map_url'] }}"
            >
                📍 Open Google Maps
            </a>

        </div>

        {% endif %}
        """,
        s=s
    )

    return public_page(
        "Contact",
        body
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == ADMIN_USER
            and
            check_password_hash(
                ADMIN_PASSWORD_HASH,
                password
            )
        ):

            session.clear()

            session["admin_logged_in"] = True
            session["admin_user"] = username

            return redirect(
                url_for("admin_dashboard")
            )

        flash(
            "Wrong username ya password.",
            "error"
        )

    body = """
    <div
        style="
            max-width:430px;
            margin:60px auto;
        "
    >

        <div class="panel">

            <h2>
                🔐 Admin Login
            </h2>

            <form method="post">

                <label>
                    Username
                </label>

                <input
                    name="username"
                    required
                >

                <br><br>

                <label>
                    Password
                </label>

                <input
                    type="password"
                    name="password"
                    required
                >

                <br><br>

                <button
                    class="btn green"
                    type="submit"
                >
                    LOGIN
                </button>

            </form>

        </div>

    </div>
    """

    return public_page(
        "Admin Login",
        body
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin")
@admin_required
def admin_dashboard():

    con = db()

    members_count = con.execute(
        "SELECT COUNT(*) FROM members WHERE active=1"
    ).fetchone()[0]

    committee_count = con.execute(
        "SELECT COUNT(*) FROM committee WHERE active=1"
    ).fetchone()[0]

    business_count = con.execute(
        "SELECT COUNT(*) FROM businesses WHERE active=1"
    ).fetchone()[0]

    events_count = con.execute(
        "SELECT COUNT(*) FROM events WHERE active=1"
    ).fetchone()[0]

    news_count = con.execute(
        "SELECT COUNT(*) FROM news WHERE active=1"
    ).fetchone()[0]

    gallery_count = con.execute(
        "SELECT COUNT(*) FROM gallery WHERE active=1"
    ).fetchone()[0]

    donations = con.execute(
        """
        SELECT COALESCE(
            SUM(amount),
            0
        )
        FROM donations
        """
    ).fetchone()[0]

    con.close()

    body = f"""
    <div class="panel">

        <h2>
            📊 Admin Dashboard
        </h2>

        <p>
            Welcome,
            <b>
                {safe(
                    session.get(
                        "admin_user",
                        ""
                    )
                )}
            </b>
        </p>

    </div>

    <div class="grid">

        <div class="panel">
            <h3>👥 Members</h3>
            <h2>{members_count}</h2>
        </div>

        <div class="panel">
            <h3>👔 Committee</h3>
            <h2>{committee_count}</h2>
        </div>

        <div class="panel">
            <h3>🏪 Businesses</h3>
            <h2>{business_count}</h2>
        </div>

        <div class="panel">
            <h3>🎉 Events</h3>
            <h2>{events_count}</h2>
        </div>

        <div class="panel">
            <h3>📰 News</h3>
            <h2>{news_count}</h2>
        </div>

        <div class="panel">
            <h3>📸 Gallery</h3>
            <h2>{gallery_count}</h2>
        </div>

        <div class="panel">
            <h3>❤️ Donations</h3>
            <h2>{money(donations)}</h2>
        </div>

    </div>
    """

    return admin_page(
        "Admin Dashboard",
        body
    )


# ============================================================
# ADMIN SETTINGS
# ============================================================

@app.route(
    "/admin/settings",
    methods=["GET", "POST"]
)
@admin_required
def admin_settings():

    con = db()

    if request.method == "POST":

        try:

            current = con.execute(
                "SELECT * FROM settings WHERE id=1"
            ).fetchone()

            hero = save_upload(
                request.files.get("hero_photo")
            )

            bhagwan = save_upload(
                request.files.get("bhagwan_photo")
            )

            bhawan = save_upload(
                request.files.get("bhawan_photo")
            )

            hero = (
                hero
                or current["hero_photo"]
                or "ajmeedhji_maharaj.jpg"
            )

            bhagwan = (
                bhagwan
                or current["bhagwan_photo"]
                or "bhagwan.jpg"
            )

            bhawan = (
                bhawan
                or current["bhawan_photo"]
                or "samaj_bhawan.jpg"
            )

            con.execute(
                """
                UPDATE settings
                SET
                    samaj_name=?,
                    location=?,
                    slogan=?,
                    about=?,
                    bhawan_name=?,
                    bhawan_address=?,
                    bhawan_details=?,
                    bhawan_phone=?,
                    phone=?,
                    whatsapp=?,
                    email=?,
                    map_url=?,
                    donation_info=?,
                    upi_id=?,
                    hero_photo=?,
                    bhagwan_photo=?,
                    bhawan_photo=?
                WHERE id=1
                """,
                (
                    request.form.get(
                        "samaj_name",
                        ""
                    ).strip(),

                    request.form.get(
                        "location",
                        ""
                    ).strip(),

                    request.form.get(
                        "slogan",
                        ""
                    ).strip(),

                    request.form.get(
                        "about",
                        ""
                    ).strip(),

                    request.form.get(
                        "bhawan_name",
                        ""
                    ).strip(),

                    request.form.get(
                        "bhawan_address",
                        ""
                    ).strip(),

                    request.form.get(
                        "bhawan_details",
                        ""
                    ).strip(),

                    request.form.get(
                        "bhawan_phone",
                        ""
                    ).strip(),

                    request.form.get(
                        "phone",
                        ""
                    ).strip(),

                    request.form.get(
                        "whatsapp",
                        ""
                    ).strip(),

                    request.form.get(
                        "email",
                        ""
                    ).strip(),

                    request.form.get(
                        "map_url",
                        ""
                    ).strip(),

                    request.form.get(
                        "donation_info",
                        ""
                    ).strip(),

                    request.form.get(
                        "upi_id",
                        ""
                    ).strip(),

                    hero,
                    bhagwan,
                    bhawan
                )
            )

            con.commit()

            flash(
                "Society details update ho gayi.",
                "success"
            )

        except Exception as e:

            con.rollback()

            flash(
                str(e),
                "error"
            )

    row = con.execute(
        "SELECT * FROM settings WHERE id=1"
    ).fetchone()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                ⚙️ Society Details
            </h2>

            <form
                method="post"
                enctype="multipart/form-data"
            >

                <div class="form-grid">

                    <div>

                        <label>
                            Society Name
                        </label>

                        <input
                            name="samaj_name"
                            value="{{ r['samaj_name'] }}"
                            required
                        >

                    </div>


                    <div>

                        <label>
                            Location
                        </label>

                        <input
                            name="location"
                            value="{{ r['location'] }}"
                        >

                    </div>


                    <div class="full">

                        <label>
                            Slogan
                        </label>

                        <input
                            name="slogan"
                            value="{{ r['slogan'] }}"
                        >

                    </div>


                    <div class="full">

                        <label>
                            About Society
                        </label>

                        <textarea
                            name="about"
                        >{{ r['about'] }}</textarea>

                    </div>


                    <div>

                        <label>
                            Bhawan Name
                        </label>

                        <input
                            name="bhawan_name"
                            value="{{ r['bhawan_name'] }}"
                        >

                    </div>


                    <div>

                        <label>
                            Bhawan Phone
                        </label>

                        <input
                            name="bhawan_phone"
                            value="{{ r['bhawan_phone'] }}"
                        >

                    </div>


                    <div>

                        <label>
                            Bhawan Address
                        </label>

                        <input
                            name="bhawan_address"
                            value="{{ r['bhawan_address'] }}"
                        >

                    </div>


                    <div>

                        <label>
                            Main Phone
                        </label>

                        <input
                            name="phone"
                            value="{{ r['phone'] }}"
                        >

                    </div>


                    <div>

                        <label>
                            WhatsApp
                        </label>

                        <input
                            name="whatsapp"
                            value="{{ r['whatsapp'] }}"
                        >

                    </div>


                    <div>

                        <label>
                            Email
                        </label>

                        <input
                            name="email"
                            value="{{ r['email'] }}"
                        >

                    </div>


                    <div>

                        <label>
                            Google Maps URL
                        </label>

                        <input
                            name="map_url"
                            value="{{ r['map_url'] }}"
                        >

                    </div>


                    <div>

                        <label>
                            UPI ID
                        </label>

                        <input
                            name="upi_id"
                            value="{{ r['upi_id'] }}"
                        >

                    </div>


                    <div class="full">

                        <label>
                            Bhawan Details
                        </label>

                        <textarea
                            name="bhawan_details"
                        >{{ r['bhawan_details'] }}</textarea>

                    </div>


                    <div class="full">

                        <label>
                            Donation Information
                        </label>

                        <textarea
                            name="donation_info"
                        >{{ r['donation_info'] }}</textarea>

                    </div>


                    <div>

                        <label>
                            Ajmiढ़ Ji Maharaj Photo
                        </label>

                        <input
                            type="file"
                            name="hero_photo"
                            accept=".jpg,.jpeg,.png,.webp,.gif"
                        >

                    </div>


                    <div>

                        <label>
                            Bhagwan Photo
                        </label>

                        <input
                            type="file"
                            name="bhagwan_photo"
                            accept=".jpg,.jpeg,.png,.webp,.gif"
                        >

                    </div>


                    <div>

                        <label>
                            Samaj Bhawan Photo
                        </label>

                        <input
                            type="file"
                            name="bhawan_photo"
                            accept=".jpg,.jpeg,.png,.webp,.gif"
                        >

                    </div>

                </div>

                <br>

                <button
                    class="btn green"
                    type="submit"
                >
                    💾 SAVE DETAILS
                </button>

            </form>

        </div>
        """,
        r=row
    )

    return admin_page(
        "Society Details",
        body
    )


# ============================================================
# ADMIN MEMBERS
# ============================================================

@app.route(
    "/admin/members",
    methods=["GET", "POST"]
)
@admin_required
def admin_members():

    con = db()

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        )

        try:

            if action == "delete":

                con.execute(
                    """
                    UPDATE members
                    SET active=0
                    WHERE id=?
                    """,
                    (
                        request.form.get(
                            "id"
                        ),
                    )
                )

            else:

                photo = save_upload(
                    request.files.get(
                        "photo"
                    )
                )

                con.execute(
                    """
                    INSERT INTO members(
                        name,
                        mobile,
                        city,
                        village,
                        occupation,
                        family,
                        photo
                    )
                    VALUES(?,?,?,?,?,?,?)
                    """,
                    (
                        request.form.get(
                            "name",
                            ""
                        ).strip(),

                        request.form.get(
                            "mobile",
                            ""
                        ).strip(),

                        request.form.get(
                            "city",
                            ""
                        ).strip(),

                        request.form.get(
                            "village",
                            ""
                        ).strip(),

                        request.form.get(
                            "occupation",
                            ""
                        ).strip(),

                        request.form.get(
                            "family",
                            ""
                        ).strip(),

                        photo
                    )
                )

            con.commit()

            flash(
                "Member operation successful.",
                "success"
            )

        except Exception as e:

            con.rollback()

            flash(
                str(e),
                "error"
            )

    rows = con.execute(
        """
        SELECT *
        FROM members
        WHERE active=1
        ORDER BY name
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                👥 Members
            </h2>

            <form
                method="post"
                enctype="multipart/form-data"
            >

                <div class="form-grid">

                    <div>
                        <label>Name</label>
                        <input
                            name="name"
                            required
                        >
                    </div>

                    <div>
                        <label>Mobile</label>
                        <input name="mobile">
                    </div>

                    <div>
                        <label>City</label>
                        <input name="city">
                    </div>

                    <div>
                        <label>Village</label>
                        <input name="village">
                    </div>

                    <div>
                        <label>Occupation</label>
                        <input name="occupation">
                    </div>

                    <div>
                        <label>Photo</label>
                        <input
                            type="file"
                            name="photo"
                            accept=".jpg,.jpeg,.png,.webp,.gif"
                        >
                    </div>

                    <div class="full">
                        <label>Family</label>
                        <textarea
                            name="family"
                        ></textarea>
                    </div>

                </div>

                <br>

                <button
                    class="btn green"
                    type="submit"
                >
                    ➕ ADD MEMBER
                </button>

            </form>

        </div>


        <div class="panel">

            <div style="overflow-x:auto">

                <table>

                    <tr>

                        <th>Photo</th>
                        <th>Name</th>
                        <th>Mobile</th>
                        <th>City</th>
                        <th>Occupation</th>
                        <th>Action</th>

                    </tr>

                    {% for r in rows %}

                    <tr>

                        <td>

                            {% if r['photo'] %}

                            <img
                                class="preview"
                                src="{{ image_url(
                                    r['photo']
                                ) }}"
                            >

                            {% endif %}

                        </td>

                        <td>
                            {{ r['name'] }}
                        </td>

                        <td>
                            {{ r['mobile'] }}
                        </td>

                        <td>
                            {{ r['city'] }}
                        </td>

                        <td>
                            {{ r['occupation'] }}
                        </td>

                        <td>

                            <form method="post">

                                <input
                                    type="hidden"
                                    name="action"
                                    value="delete"
                                >

                                <input
                                    type="hidden"
                                    name="id"
                                    value="{{ r['id'] }}"
                                >

                                <button
                                    class="btn red"
                                    type="submit"
                                >
                                    DELETE
                                </button>

                            </form>

                        </td>

                    </tr>

                    {% endfor %}

                </table>

            </div>

        </div>
        """,
        rows=rows,
        image_url=image_url
    )

    return admin_page(
        "Members",
        body
    )


# ============================================================
# ADMIN COMMITTEE
# ============================================================

@app.route(
    "/admin/committee",
    methods=["GET", "POST"]
)
@admin_required
def admin_committee():

    con = db()

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        )

        try:

            if action == "delete":

                con.execute(
                    """
                    UPDATE committee
                    SET active=0
                    WHERE id=?
                    """,
                    (
                        request.form.get(
                            "id"
                        ),
                    )
                )

            else:

                photo = save_upload(
                    request.files.get(
                        "photo"
                    )
                )

                con.execute(
                    """
                    INSERT INTO committee(
                        name,
                        post,
                        mobile,
                        photo,
                        sort_order
                    )
                    VALUES(?,?,?,?,?)
                    """,
                    (
                        request.form.get(
                            "name",
                            ""
                        ).strip(),

                        request.form.get(
                            "post",
                            ""
                        ).strip(),

                        request.form.get(
                            "mobile",
                            ""
                        ).strip(),

                        photo,

                        int(
                            request.form.get(
                                "sort_order",
                                "0"
                            ) or 0
                        )
                    )
                )

            con.commit()

        except Exception as e:

            con.rollback()

            flash(
                str(e),
                "error"
            )

    rows = con.execute(
        """
        SELECT *
        FROM committee
        WHERE active=1
        ORDER BY sort_order,name
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                👔 Committee
            </h2>

            <form
                method="post"
                enctype="multipart/form-data"
            >

                <div class="form-grid">

                    <div>
                        <label>Name</label>
                        <input
                            name="name"
                            required
                        >
                    </div>

                    <div>
                        <label>Post</label>
                        <input
                            name="post"
                            placeholder="अध्यक्ष / सचिव / कोषाध्यक्ष"
                            required
                        >
                    </div>

                    <div>
                        <label>Mobile</label>
                        <input name="mobile">
                    </div>

                    <div>
                        <label>Sort Order</label>
                        <input
                            type="number"
                            name="sort_order"
                            value="0"
                        >
                    </div>

                    <div>
                        <label>Photo</label>
                        <input
                            type="file"
                            name="photo"
                            accept=".jpg,.jpeg,.png,.webp,.gif"
                        >
                    </div>

                </div>

                <br>

                <button
                    class="btn green"
                    type="submit"
                >
                    ➕ ADD COMMITTEE
                </button>

            </form>

        </div>


        <div class="panel">

            <table>

                <tr>
                    <th>Name</th>
                    <th>Post</th>
                    <th>Mobile</th>
                    <th>Action</th>
                </tr>

                {% for r in rows %}

                <tr>

                    <td>
                        {{ r['name'] }}
                    </td>

                    <td>
                        {{ r['post'] }}
                    </td>

                    <td>
                        {{ r['mobile'] }}
                    </td>

                    <td>

                        <form method="post">

                            <input
                                type="hidden"
                                name="action"
                                value="delete"
                            >

                            <input
                                type="hidden"
                                name="id"
                                value="{{ r['id'] }}"
                            >

                            <button
                                class="btn red"
                                type="submit"
                            >
                                DELETE
                            </button>

                        </form>

                    </td>

                </tr>

                {% endfor %}

            </table>

        </div>
        """,
        rows=rows
    )

    return admin_page(
        "Committee",
        body
    )


# ============================================================
# ADMIN BUSINESSES
# ============================================================

@app.route(
    "/admin/businesses",
    methods=["GET", "POST"]
)
@admin_required
def admin_businesses():

    con = db()

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        )

        try:

            if action == "delete":

                con.execute(
                    """
                    UPDATE businesses
                    SET active=0
                    WHERE id=?
                    """,
                    (
                        request.form.get(
                            "id"
                        ),
                    )
                )

            else:

                photo = save_upload(
                    request.files.get(
                        "photo"
                    )
                )

                con.execute(
                    """
                    INSERT INTO businesses(
                        name,
                        owner,
                        category,
                        mobile,
                        address,
                        description,
                        photo
                    )
                    VALUES(?,?,?,?,?,?,?)
                    """,
                    (
                        request.form.get(
                            "name",
                            ""
                        ).strip(),

                        request.form.get(
                            "owner",
                            ""
                        ).strip(),

                        request.form.get(
                            "category",
                            ""
                        ).strip(),

                        request.form.get(
                            "mobile",
                            ""
                        ).strip(),

                        request.form.get(
                            "address",
                            ""
                        ).strip(),

                        request.form.get(
                            "description",
                            ""
                        ).strip(),

                        photo
                    )
                )

            con.commit()

        except Exception as e:

            con.rollback()

            flash(
                str(e),
                "error"
            )

    rows = con.execute(
        """
        SELECT *
        FROM businesses
        WHERE active=1
        ORDER BY name
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                🏪 Businesses
            </h2>

            <form
                method="post"
                enctype="multipart/form-data"
            >

                <div class="form-grid">

                    <div>
                        <label>Business Name</label>
                        <input
                            name="name"
                            required
                        >
                    </div>

                    <div>
                        <label>Owner</label>
                        <input name="owner">
                    </div>

                    <div>
                        <label>Category</label>
                        <input name="category">
                    </div>

                    <div>
                        <label>Mobile</label>
                        <input name="mobile">
                    </div>

                    <div>
                        <label>Address</label>
                        <input name="address">
                    </div>

                    <div>
                        <label>Photo</label>
                        <input
                            type="file"
                            name="photo"
                            accept=".jpg,.jpeg,.png,.webp,.gif"
                        >
                    </div>

                    <div class="full">
                        <label>Description</label>
                        <textarea
                            name="description"
                        ></textarea>
                    </div>

                </div>

                <br>

                <button
                    class="btn green"
                    type="submit"
                >
                    ➕ ADD BUSINESS
                </button>

            </form>

        </div>


        <div class="panel">

            <table>

                <tr>
                    <th>Name</th>
                    <th>Owner</th>
                    <th>Category</th>
                    <th>Mobile</th>
                    <th>Action</th>
                </tr>

                {% for r in rows %}

                <tr>

                    <td>
                        {{ r['name'] }}
                    </td>

                    <td>
                        {{ r['owner'] }}
                    </td>

                    <td>
                        {{ r['category'] }}
                    </td>

                    <td>
                        {{ r['mobile'] }}
                    </td>

                    <td>

                        <form method="post">

                            <input
                                type="hidden"
                                name="action"
                                value="delete"
                            >

                            <input
                                type="hidden"
                                name="id"
                                value="{{ r['id'] }}"
                            >

                            <button
                                class="btn red"
                                type="submit"
                            >
                                DELETE
                            </button>

                        </form>

                    </td>

                </tr>

                {% endfor %}

            </table>

        </div>
        """,
        rows=rows
    )

    return admin_page(
        "Businesses",
        body
    )


# ============================================================
# ADMIN EVENTS
# ============================================================

@app.route(
    "/admin/events",
    methods=["GET", "POST"]
)
@admin_required
def admin_events():

    con = db()

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        )

        try:

            if action == "delete":

                con.execute(
                    """
                    UPDATE events
                    SET active=0
                    WHERE id=?
                    """,
                    (
                        request.form.get(
                            "id"
                        ),
                    )
                )

            else:

                photo = save_upload(
                    request.files.get(
                        "photo"
                    )
                )

                con.execute(
                    """
                    INSERT INTO events(
                        title,
                        event_date,
                        event_time,
                        venue,
                        description,
                        photo,
                        registration_url
                    )
                    VALUES(?,?,?,?,?,?,?)
                    """,
                    (
                        request.form.get(
                            "title",
                            ""
                        ).strip(),

                        request.form.get(
                            "event_date",
                            ""
                        ).strip(),

                        request.form.get(
                            "event_time",
                            ""
                        ).strip(),

                        request.form.get(
                            "venue",
                            ""
                        ).strip(),

                        request.form.get(
                            "description",
                            ""
                        ).strip(),

                        photo,

                        request.form.get(
                            "registration_url",
                            ""
                        ).strip()
                    )
                )

            con.commit()

        except Exception as e:

            con.rollback()

            flash(
                str(e),
                "error"
            )

    rows = con.execute(
        """
        SELECT *
        FROM events
        WHERE active=1
        ORDER BY id DESC
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                🎉 Events
            </h2>

            <form
                method="post"
                enctype="multipart/form-data"
            >

                <div class="form-grid">

                    <div>
                        <label>Title</label>
                        <input
                            name="title"
                            required
                        >
                    </div>

                    <div>
                        <label>Date</label>
                        <input
                            type="date"
                            name="event_date"
                        >
                    </div>

                    <div>
                        <label>Time</label>
                        <input
                            type="time"
                            name="event_time"
                        >
                    </div>

                    <div>
                        <label>Venue</label>
                        <input name="venue">
                    </div>

                    <div>
                        <label>Registration URL</label>
                        <input name="registration_url">
                    </div>

                    <div>
                        <label>Photo</label>
                        <input
                            type="file"
                            name="photo"
                            accept=".jpg,.jpeg,.png,.webp,.gif"
                        >
                    </div>

                    <div class="full">
                        <label>Description</label>
                        <textarea
                            name="description"
                        ></textarea>
                    </div>

                </div>

                <br>

                <button
                    class="btn green"
                    type="submit"
                >
                    ➕ ADD EVENT
                </button>

            </form>

        </div>


        <div class="panel">

            <table>

                <tr>
                    <th>Title</th>
                    <th>Date</th>
                    <th>Venue</th>
                    <th>Action</th>
                </tr>

                {% for r in rows %}

                <tr>

                    <td>
                        {{ r['title'] }}
                    </td>

                    <td>
                        {{ r['event_date'] }}
                    </td>

                    <td>
                        {{ r['venue'] }}
                    </td>

                    <td>

                        <form method="post">

                            <input
                                type="hidden"
                                name="action"
                                value="delete"
                            >

                            <input
                                type="hidden"
                                name="id"
                                value="{{ r['id'] }}"
                            >

                            <button
                                class="btn red"
                                type="submit"
                            >
                                DELETE
                            </button>

                        </form>

                    </td>

                </tr>

                {% endfor %}

            </table>

        </div>
        """,
        rows=rows
    )

    return admin_page(
        "Events",
        body
    )


# ============================================================
# ADMIN NEWS
# ============================================================

@app.route(
    "/admin/news",
    methods=["GET", "POST"]
)
@admin_required
def admin_news():

    con = db()

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        )

        try:

            if action == "delete":

                con.execute(
                    """
                    UPDATE news
                    SET active=0
                    WHERE id=?
                    """,
                    (
                        request.form.get(
                            "id"
                        ),
                    )
                )

            else:

                photo = save_upload(
                    request.files.get(
                        "photo"
                    )
                )

                con.execute(
                    """
                    INSERT INTO news(
                        title,
                        news_date,
                        body,
                        photo
                    )
                    VALUES(?,?,?,?)
                    """,
                    (
                        request.form.get(
                            "title",
                            ""
                        ).strip(),

                        request.form.get(
                            "news_date",
                            ""
                        ).strip(),

                        request.form.get(
                            "body",
                            ""
                        ).strip(),

                        photo
                    )
                )

            con.commit()

        except Exception as e:

            con.rollback()

            flash(
                str(e),
                "error"
            )

    rows = con.execute(
        """
        SELECT *
        FROM news
        WHERE active=1
        ORDER BY id DESC
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                📰 News
            </h2>

            <form
                method="post"
                enctype="multipart/form-data"
            >

                <div class="form-grid">

                    <div>
                        <label>Title</label>
                        <input
                            name="title"
                            required
                        >
                    </div>

                    <div>
                        <label>Date</label>
                        <input
                            type="date"
                            name="news_date"
                        >
                    </div>

                    <div>
                        <label>Photo</label>
                        <input
                            type="file"
                            name="photo"
                            accept=".jpg,.jpeg,.png,.webp,.gif"
                        >
                    </div>

                    <div class="full">
                        <label>News</label>
                        <textarea
                            name="body"
                        ></textarea>
                    </div>

                </div>

                <br>

                <button
                    class="btn green"
                    type="submit"
                >
                    ➕ ADD NEWS
                </button>

            </form>

        </div>


        <div class="panel">

            <table>

                <tr>
                    <th>Title</th>
                    <th>Date</th>
                    <th>Action</th>
                </tr>

                {% for r in rows %}

                <tr>

                    <td>
                        {{ r['title'] }}
                    </td>

                    <td>
                        {{ r['news_date'] }}
                    </td>

                    <td>

                        <form method="post">

                            <input
                                type="hidden"
                                name="action"
                                value="delete"
                            >

                            <input
                                type="hidden"
                                name="id"
                                value="{{ r['id'] }}"
                            >

                            <button
                                class="btn red"
                                type="submit"
                            >
                                DELETE
                            </button>

                        </form>

                    </td>

                </tr>

                {% endfor %}

            </table>

        </div>
        """,
        rows=rows
    )

    return admin_page(
        "News",
        body
    )


# ============================================================
# ADMIN NOTICES
# ============================================================

@app.route(
    "/admin/notices",
    methods=["GET", "POST"]
)
@admin_required
def admin_notices():

    con = db()

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        )

        try:

            if action == "delete":

                con.execute(
                    """
                    UPDATE notices
                    SET active=0
                    WHERE id=?
                    """,
                    (
                        request.form.get(
                            "id"
                        ),
                    )
                )

            else:

                con.execute(
                    """
                    INSERT INTO notices(
                        title,
                        body,
                        notice_date
                    )
                    VALUES(?,?,?)
                    """,
                    (
                        request.form.get(
                            "title",
                            ""
                        ).strip(),

                        request.form.get(
                            "body",
                            ""
                        ).strip(),

                        request.form.get(
                            "notice_date",
                            ""
                        ).strip()
                    )
                )

            con.commit()

        except Exception as e:

            con.rollback()

            flash(
                str(e),
                "error"
            )

    rows = con.execute(
        """
        SELECT *
        FROM notices
        WHERE active=1
        ORDER BY id DESC
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                📢 Notices
            </h2>

            <form method="post">

                <div class="form-grid">

                    <div>
                        <label>Title</label>
                        <input
                            name="title"
                            required
                        >
                    </div>

                    <div>
                        <label>Date</label>
                        <input
                            type="date"
                            name="notice_date"
                        >
                    </div>

                    <div class="full">
                        <label>Notice</label>
                        <textarea
                            name="body"
                        ></textarea>
                    </div>

                </div>

                <br>

                <button
                    class="btn green"
                    type="submit"
                >
                    ➕ ADD NOTICE
                </button>

            </form>

        </div>


        <div class="panel">

            <table>

                <tr>
                    <th>Title</th>
                    <th>Date</th>
                    <th>Action</th>
                </tr>

                {% for r in rows %}

                <tr>

                    <td>
                        {{ r['title'] }}
                    </td>

                    <td>
                        {{ r['notice_date'] }}
                    </td>

                    <td>

                        <form method="post">

                            <input
                                type="hidden"
                                name="action"
                                value="delete"
                            >

                            <input
                                type="hidden"
                                name="id"
                                value="{{ r['id'] }}"
                            >

                            <button
                                class="btn red"
                                type="submit"
                            >
                                DELETE
                            </button>

                        </form>

                    </td>

                </tr>

                {% endfor %}

            </table>

        </div>
        """,
        rows=rows
    )

    return admin_page(
        "Notices",
        body
    )


# ============================================================
# ADMIN EDUCATION
# ============================================================

@app.route(
    "/admin/education",
    methods=["GET", "POST"]
)
@admin_required
def admin_education():

    con = db()

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        )

        try:

            if action == "delete":

                con.execute(
                    """
                    UPDATE education
                    SET active=0
                    WHERE id=?
                    """,
                    (
                        request.form.get(
                            "id"
                        ),
                    )
                )

            else:

                con.execute(
                    """
                    INSERT INTO education(
                        title,
                        body,
                        icon
                    )
                    VALUES(?,?,?)
                    """,
                    (
                        request.form.get(
                            "title",
                            ""
                        ).strip(),

                        request.form.get(
                            "body",
                            ""
                        ).strip(),

                        request.form.get(
                            "icon",
                            "🎓"
                        ).strip()
                    )
                )

            con.commit()

        except Exception as e:

            con.rollback()

            flash(
                str(e),
                "error"
            )

    rows = con.execute(
        """
        SELECT *
        FROM education
        WHERE active=1
        ORDER BY id DESC
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                🎓 Education
            </h2>

            <form method="post">

                <div class="form-grid">

                    <div>
                        <label>Title</label>
                        <input
                            name="title"
                            required
                        >
                    </div>

                    <div>
                        <label>Icon</label>
                        <input
                            name="icon"
                            value="🎓"
                        >
                    </div>

                    <div class="full">
                        <label>Details</label>
                        <textarea
                            name="body"
                        ></textarea>
                    </div>

                </div>

                <br>

                <button
                    class="btn green"
                    type="submit"
                >
                    ➕ ADD
                </button>

            </form>

        </div>


        <div class="panel">

            <table>

                <tr>
                    <th>Title</th>
                    <th>Icon</th>
                    <th>Action</th>
                </tr>

                {% for r in rows %}

                <tr>

                    <td>
                        {{ r['title'] }}
                    </td>

                    <td>
                        {{ r['icon'] }}
                    </td>

                    <td>

                        <form method="post">

                            <input
                                type="hidden"
                                name="action"
                                value="delete"
                            >

                            <input
                                type="hidden"
                                name="id"
                                value="{{ r['id'] }}"
                            >

                            <button
                                class="btn red"
                                type="submit"
                            >
                                DELETE
                            </button>

                        </form>

                    </td>

                </tr>

                {% endfor %}

            </table>

        </div>
        """,
        rows=rows
    )

    return admin_page(
        "Education",
        body
    )


# ============================================================
# ADMIN GALLERY
# ============================================================

@app.route(
    "/admin/gallery",
    methods=["GET", "POST"]
)
@admin_required
def admin_gallery():

    con = db()

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        )

        try:

            if action == "delete":

                con.execute(
                    """
                    UPDATE gallery
                    SET active=0
                    WHERE id=?
                    """,
                    (
                        request.form.get(
                            "id"
                        ),
                    )
                )

            else:

                photo = save_upload(
                    request.files.get(
                        "photo"
                    )
                )

                if not photo:

                    raise ValueError(
                        "Photo select karo."
                    )

                con.execute(
                    """
                    INSERT INTO gallery(
                        title,
                        category,
                        photo
                    )
                    VALUES(?,?,?)
                    """,
                    (
                        request.form.get(
                            "title",
                            ""
                        ).strip(),

                        request.form.get(
                            "category",
                            "General"
                        ).strip(),

                        photo
                    )
                )

            con.commit()

        except Exception as e:

            con.rollback()

            flash(
                str(e),
                "error"
            )

    rows = con.execute(
        """
        SELECT *
        FROM gallery
        WHERE active=1
        ORDER BY id DESC
        """
    ).fetchall()

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                📸 Gallery
            </h2>

            <form
                method="post"
                enctype="multipart/form-data"
            >

                <div class="form-grid">

                    <div>
                        <label>Title</label>
                        <input name="title">
                    </div>

                    <div>
                        <label>Category</label>
                        <input
                            name="category"
                            value="General"
                        >
                    </div>

                    <div class="full">
                        <label>Photo</label>
                        <input
                            type="file"
                            name="photo"
                            accept=".jpg,.jpeg,.png,.webp,.gif"
                            required
                        >
                    </div>

                </div>

                <br>

                <button
                    class="btn green"
                    type="submit"
                >
                    📸 UPLOAD
                </button>

            </form>

        </div>


        <div class="card-grid">

        {% for r in rows %}

            <div class="card">

                <img
                    src="{{ image_url(r['photo']) }}"
                    alt="{{ r['title'] }}"
                >

                <h3>
                    {{ r['title'] }}
                </h3>

                <p>
                    {{ r['category'] }}
                </p>

                <form method="post">

                    <input
                        type="hidden"
                        name="action"
                        value="delete"
                    >

                    <input
                        type="hidden"
                        name="id"
                        value="{{ r['id'] }}"
                    >

                    <button
                        class="btn red"
                        type="submit"
                    >
                        DELETE
                    </button>

                </form>

            </div>

        {% endfor %}

        </div>
        """,
        rows=rows,
        image_url=image_url
    )

    return admin_page(
        "Gallery",
        body
    )


# ============================================================
# ADMIN DONATIONS
# ============================================================

@app.route("/admin/donations")
@admin_required
def admin_donations():

    con = db()

    rows = con.execute(
        """
        SELECT *
        FROM donations
        ORDER BY id DESC
        """
    ).fetchall()

    total = con.execute(
        """
        SELECT COALESCE(
            SUM(amount),
            0
        )
        FROM donations
        """
    ).fetchone()[0]

    con.close()

    body = render_template_string(
        """
        <div class="panel">

            <h2>
                ❤️ Donations
            </h2>

            <h3>
                Total:
                ₹ {{ "%.2f"|format(total or 0) }}
            </h3>

        </div>


        <div class="panel">

            <table>

                <tr>

                    <th>
                        Donor
                    </th>

                    <th>
                        Amount
                    </th>

                    <th>
                        Purpose
                    </th>

                    <th>
                        Mode
                    </th>

                    <th>
                        Note
                    </th>

                </tr>

                {% for r in rows %}

                <tr>

                    <td>
                        {{ r['donor_name'] }}
                    </td>

                    <td>
                        ₹ {{ "%.2f"|format(
                            r['amount'] or 0
                        ) }}
                    </td>

                    <td>
                        {{ r['purpose'] }}
                    </td>

                    <td>
                        {{ r['mode'] }}
                    </td>

                    <td>
                        {{ r['note'] }}
                    </td>

                </tr>

                {% endfor %}

            </table>

        </div>
        """,
        rows=rows,
        total=total
    )

    return admin_page(
        "Donations",
        body
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    setup()

    print()
    print("=" * 60)
    print("       मैढ़ स्वर्णकार समाज - WEBSITE")
    print("       Jodhpur, Rajasthan")
    print("=" * 60)
    print()
    print("Website:")
    print("http://127.0.0.1:5000")
    print()
    print("Admin:")
    print("http://127.0.0.1:5000/admin/login")
    print()
    print("Username : admin")
    print("Password : 1234")
    print()
    print("Developer : KRISHNA")
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )
