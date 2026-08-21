from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for
)

app = Flask(__name__)

# ============================================================
# BASIC SETTINGS
# ============================================================

SAMAJ_NAME = "मैढ़ स्वर्णकार समाज"
LOCATION = "Jodhpur, Rajasthan"

# ============================================================
# SAMPLE DATA
# ============================================================

NEWS = [
    {
        "title": "मैढ़ स्वर्णकार समाज",
        "text": "समाज के सभी सदस्यों का हार्दिक स्वागत है।"
    },
    {
        "title": "समाज भवन",
        "text": "समाज भवन से संबंधित महत्वपूर्ण जानकारी यहाँ उपलब्ध होगी।"
    },
    {
        "title": "समाज सूचना",
        "text": "समाज के आगामी कार्यक्रमों एवं महत्वपूर्ण सूचनाओं की जानकारी यहाँ मिलेगी।"
    }
]

EVENTS = [
    {
        "title": "समाज कार्यक्रम",
        "date": "जल्द घोषित किया जाएगा",
        "place": "Jodhpur",
        "photo": "function1.jpg"
    },
    {
        "title": "समाज बैठक",
        "date": "जल्द घोषित किया जाएगा",
        "place": "समाज भवन",
        "photo": "function2.jpg"
    },
    {
        "title": "समाज समारोह",
        "date": "जल्द घोषित किया जाएगा",
        "place": "Jodhpur",
        "photo": "function3.jpg"
    }
]

MEMBERS = [
    {
        "name": "सदस्य का नाम",
        "business": "व्यवसाय",
        "area": "Jodhpur"
    }
]

BUSINESSES = [
    {
        "name": "व्यवसाय / दुकान का नाम",
        "owner": "संचालक का नाम",
        "area": "Jodhpur"
    }
]


# ============================================================
# MAIN HTML
# ============================================================

BASE_HTML = """
<!DOCTYPE html>

<html lang="hi">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
    {{ title }} | मैढ़ स्वर्णकार समाज
</title>

<style>

:root{
    --gold:#d7a72f;
    --gold-light:#ffe08a;
    --gold-dark:#8b5a05;
    --brown:#3a1d08;
    --brown-light:#70420d;
    --cream:#fff9eb;
    --white:#ffffff;
    --text:#2a190b;
    --muted:#70695f;
    --green:#159447;
    --blue:#2866d4;
    --red:#c32943;
    --purple:#7247c9;
}

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

html{
    scroll-behavior:smooth;
}

body{
    font-family:
        "Segoe UI",
        "Noto Sans Devanagari",
        Arial,
        sans-serif;

    color:var(--text);

    line-height:1.6;

    background:
        radial-gradient(
            circle at 5% 5%,
            rgba(255,228,135,.65),
            transparent 25%
        ),
        radial-gradient(
            circle at 95% 20%,
            rgba(221,176,75,.25),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            #fffdf8,
            #f7ecd0 45%,
            #fffdf8
        );

    min-height:100vh;
}

::-webkit-scrollbar{
    width:9px;
}

::-webkit-scrollbar-track{
    background:#f4ead1;
}

::-webkit-scrollbar-thumb{
    background:
        linear-gradient(
            #d3a336,
            #80520a
        );

    border-radius:20px;
}

header{
    position:sticky;
    top:0;
    z-index:999;

    background:
        linear-gradient(
            135deg,
            #1c0c03,
            #5a310a,
            #a46b13,
            #4b2707,
            #170902
        );

    color:white;

    border-bottom:
        3px solid var(--gold);

    box-shadow:
        0 8px 35px rgba(0,0,0,.25);

    backdrop-filter:
        blur(12px);
}

.topbar{
    max-width:1400px;
    margin:auto;

    padding:
        12px 22px;

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:25px;
}

.brand{
    display:flex;

    align-items:center;

    gap:13px;

    min-width:max-content;
}

.brand-icon{
    width:52px;
    height:52px;

    border-radius:50%;

    display:flex;

    align-items:center;

    justify-content:center;

    background:
        linear-gradient(
            135deg,
            #fff9dc,
            #f8d35b
        );

    color:#8a5800;

    font-size:27px;

    border:
        2px solid #ffe58f;

    box-shadow:
        0 0 18px rgba(244,200,79,.55);
}

.brand-text h1{
    font-size:21px;
    line-height:1.2;
    color:#ffe38a;
    letter-spacing:.4px;
}

.brand-text p{
    margin-top:2px;
    color:#fff2cf;
    font-size:12px;
}

nav{
    display:flex;
    flex-wrap:wrap;
    justify-content:center;
    gap:5px;
}

nav a{
    color:white;
    text-decoration:none;

    padding:
        9px 11px;

    border-radius:10px;

    font-size:13px;

    font-weight:700;

    transition:
        all .25s ease;

    position:relative;

    overflow:hidden;
}

nav a::before{
    content:"";

    position:absolute;

    left:-120%;
    top:0;

    width:100%;
    height:100%;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,.2),
            transparent
        );

    transition:.4s;
}

nav a:hover::before{
    left:120%;
}

nav a:hover{
    background:
        linear-gradient(
            135deg,
            #f2c64d,
            #fff0a6
        );

    color:#2c1605;

    transform:
        translateY(-2px);
}

.hero{
    min-height:700px;

    position:relative;

    background:
        linear-gradient(
            rgba(20,8,0,.25),
            rgba(20,8,0,.70)
        ),
        url("/static/ajmerji_maharaj.jpg");

    background-size:cover;
    background-position:center;

    display:flex;
    align-items:center;
    justify-content:center;

    text-align:center;

    overflow:hidden;
}

.hero::before{
    content:"";

    position:absolute;
    inset:0;

    background:
        radial-gradient(
            circle,
            rgba(255,215,99,.18),
            transparent 35%
        );

    animation:
        pulseGlow 5s infinite alternate;
}

@keyframes pulseGlow{

    from{
        opacity:.4;
    }

    to{
        opacity:1;
    }
}

.hero-content{
    position:relative;
    z-index:2;

    width:min(
        1000px,
        92%
    );

    padding:
        40px 25px;

    color:white;

    background:
        rgba(15,7,2,.20);

    border:
        1px solid rgba(255,255,255,.18);

    border-radius:30px;

    backdrop-filter:
        blur(8px);

    box-shadow:
        0 25px 80px rgba(0,0,0,.35);
}

.hero-badge{
    display:inline-block;

    padding:
        9px 20px;

    border-radius:999px;

    background:
        rgba(255,255,255,.15);

    border:
        1px solid rgba(255,255,255,.3);

    backdrop-filter:
        blur(10px);

    color:#ffe28c;

    font-weight:700;

    margin-bottom:20px;
}

.hero h2{
    font-size:
        clamp(
            40px,
            7vw,
            78px
        );

    line-height:1.1;

    color:#fff2ae;

    text-shadow:
        0 5px 25px rgba(0,0,0,.8);
}

.hero h3{
    margin-top:10px;

    font-size:
        clamp(
            21px,
            3vw,
            31px
        );

    font-weight:500;
}

.hero p{
    margin-top:15px;
    font-size:18px;
    color:#fff7de;
}

.hero-buttons{
    margin-top:30px;

    display:flex;

    justify-content:center;

    flex-wrap:wrap;

    gap:13px;
}

.btn{
    display:inline-block;

    border:0;

    cursor:pointer;

    text-decoration:none;

    padding:
        12px 21px;

    border-radius:13px;

    font-weight:800;

    position:relative;

    overflow:hidden;

    transition:
        all .25s ease;

    box-shadow:
        0 8px 20px rgba(0,0,0,.15);
}

.btn::after{
    content:"";

    position:absolute;

    width:0;
    height:0;

    top:50%;
    left:50%;

    background:
        rgba(255,255,255,.25);

    transform:
        translate(-50%,-50%);

    border-radius:50%;

    transition:.4s;
}

.btn:hover::after{
    width:240px;
    height:240px;
}

.btn:hover{
    transform:
        translateY(-3px);

    box-shadow:
        0 13px 28px rgba(0,0,0,.2);
}

.btn-gold{
    background:
        linear-gradient(
            135deg,
            #d69715,
            #f7d76f
        );

    color:#2c1605;
}

.btn-light{
    background:
        linear-gradient(
            135deg,
            #ffffff,
            #fff5ce
        );

    color:#704500;
}

.btn-green{
    background:
        linear-gradient(
            135deg,
            #0c8748,
            #2aca79
        );

    color:white;
}

.btn-blue{
    background:
        linear-gradient(
            135deg,
            #2255bb,
            #5791ff
        );

    color:white;
}

.btn-red{
    background:
        linear-gradient(
            135deg,
            #ab1d34,
            #df4e64
        );

    color:white;
}

.btn-purple{
    background:
        linear-gradient(
            135deg,
            #633bb2,
            #a178f2
        );

    color:white;
}

section{
    max-width:
        1250px;

    margin:auto;

    padding:
        85px 22px;
}

.section-title{
    text-align:center;
    margin-bottom:45px;
}

.section-title span{
    display:inline-block;

    color:
        var(--gold-dark);

    font-size:13px;

    font-weight:900;

    letter-spacing:
        1.8px;

    margin-bottom:5px;
}

.section-title h2{
    font-size:
        clamp(
            28px,
            4vw,
            42px
        );

    color:
        #553006;
}

.section-title p{
    color:
        var(--muted);

    margin-top:7px;
}

.ornament{
    width:150px;
    height:3px;

    margin:
        14px auto 0;

    background:
        linear-gradient(
            90deg,
            transparent,
            var(--gold),
            transparent
        );
}

.ornament::after{
    content:"✦";

    position:relative;

    display:block;

    top:-15px;

    width:
        max-content;

    margin:auto;

    color:
        var(--gold-dark);

    background:
        #f8efd9;

    padding:0 10px;
}

.cards{
    display:grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                235px,
                1fr
            )
        );

    gap:22px;
}

.card{
    background:
        rgba(
            255,
            255,
            255,
            .88
        );

    backdrop-filter:
        blur(10px);

    border:
        1px solid
        rgba(
            218,
            174,
            72,
            .28
        );

    border-left:
        5px solid
        var(--gold);

    border-radius:22px;

    padding:27px;

    box-shadow:
        0 15px 40px
        rgba(
            85,
            51,
            10,
            .09
        );

    transition:
        .3s ease;

    position:relative;

    overflow:hidden;
}

.card::before{
    content:"";

    position:absolute;

    width:100px;
    height:100px;

    background:
        radial-gradient(
            circle,
            rgba(243,200,76,.28),
            transparent 70%
        );

    top:-30px;
    right:-20px;
}

.card:hover{
    transform:
        translateY(-8px);

    box-shadow:
        0 20px 45px
        rgba(
            85,
            51,
            10,
            .17
        );
}

.card h3{
    color:
        #744700;

    margin-bottom:9px;

    font-size:20px;
}

.card p{
    color:
        #635b51;

    font-size:14px;
}

.card-icon{
    width:62px;
    height:62px;

    border-radius:18px;

    display:flex;

    align-items:center;

    justify-content:center;

    background:
        linear-gradient(
            135deg,
            #fff2bf,
            #fffdf2
        );

    border:
        1px solid #ecd17e;

    font-size:30px;

    margin-bottom:17px;

    box-shadow:
        0 8px 20px #a3752130;
}

.about{
    display:grid;

    grid-template-columns:
        minmax(
            300px,
            1.1fr
        )
        minmax(
            300px,
            .9fr
        );

    gap:28px;

    align-items:
        stretch;
}

.about-box{
    background:
        linear-gradient(
            135deg,
            #fffef9,
            #fff5d5
        );

    border-radius:25px;

    padding:35px;

    border:
        1px solid #ecd699;

    box-shadow:
        0 15px 38px #80500f17;
}

.about-box h2{
    color:
        #724300;

    font-size:30px;
}

.about-box p{
    color:#5f574e;

    margin:
        14px 0;
}

.gold-line{
    width:90px;
    height:4px;

    border-radius:10px;

    background:
        linear-gradient(
            90deg,
            #b57909,
            #f0cb54
        );

    margin:
        14px 0 20px;
}

.feature-grid{
    display:grid;

    grid-template-columns:
        repeat(
            2,
            1fr
        );

    gap:15px;
}

.feature{
    background:white;

    border-radius:20px;

    padding:23px;

    text-align:center;

    border:
        1px solid #ead8aa;

    transition:.25s;
}

.feature:hover{
    transform:
        scale(1.02);

    box-shadow:
        0 12px 30px #0000000c;
}

.feature .emoji{
    font-size:41px;
    margin-bottom:8px;
}

.feature h3{
    color:
        #795006;
}

.feature p{
    color:#71685f;
    font-size:13px;
}

.photo-section{
    display:grid;

    grid-template-columns:
        minmax(
            280px,
            1fr
        )
        minmax(
            300px,
            1fr
        );

    gap:30px;

    align-items:center;
}

.main-photo{
    width:100%;
    height:400px;

    object-fit:cover;

    border-radius:25px;

    border:
        5px solid #f6e3a7;

    box-shadow:
        0 20px 50px rgba(85,51,10,.18);

    transition:.35s;
}

.main-photo:hover{
    transform:
        scale(1.015);
}

.photo-info{
    background:white;

    padding:32px;

    border-radius:25px;

    border:
        1px solid #ead4a0;

    box-shadow:
        0 15px 40px #80500f12;
}

.photo-info h2{
    color:
        #6d4100;

    font-size:30px;

    margin-bottom:12px;
}

.photo-info p{
    color:
        #615950;

    margin-bottom:12px;
}

.event-card{
    background:
        white;

    border-radius:22px;

    overflow:hidden;

    border:
        1px solid #ead8ac;

    box-shadow:
        0 12px 35px #79500f12;

    transition:.3s;
}

.event-card:hover{
    transform:
        translateY(-7px);

    box-shadow:
        0 18px 45px #79500f1c;
}

.event-card img{
    width:100%;
    height:220px;

    object-fit:cover;
    display:block;
}

.event-content{
    padding:20px;
}

.event-content h3{
    color:
        #704200;
}

.event-date{
    color:
        #a26804;

    font-weight:800;

    margin:
        8px 0;
}

.gallery{
    display:grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                220px,
                1fr
            )
        );

    gap:17px;
}

.gallery-item{
    position:relative;

    height:240px;

    border-radius:20px;

    overflow:hidden;

    background:
        linear-gradient(
            135deg,
            #ecddb6,
            #fff8e9
        );

    box-shadow:
        0 12px 30px #7a501014;
}

.gallery-item img{
    width:100%;
    height:100%;

    object-fit:cover;

    transition:.4s;
}

.gallery-item:hover img{
    transform:
        scale(1.08);
}

.gallery-caption{
    position:absolute;

    left:0;
    right:0;
    bottom:0;

    padding:13px;

    color:white;

    background:
        linear-gradient(
            transparent,
            rgba(0,0,0,.75)
        );
}

.donation{
    position:relative;

    overflow:hidden;

    border-radius:28px;

    padding:
        55px 30px;

    text-align:center;

    color:white;

    background:
        linear-gradient(
            135deg,
            #563000,
            #a86c08,
            #d39b27,
            #714006
        );

    box-shadow:
        0 22px 50px #6b3c1425;
}

.donation::before{
    content:"✦";

    position:absolute;

    font-size:180px;

    right:-20px;
    top:-80px;

    color:
        rgba(255,255,255,.08);
}

.donation h2{
    font-size:
        clamp(
            30px,
            4vw,
            44px
        );
}

.donation p{
    margin:
        10px auto 23px;

    max-width:700px;

    color:#fff5d0;
}

.contact-grid{
    display:grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                220px,
                1fr
            )
        );

    gap:18px;
}

.contact-box{
    background:white;

    padding:28px;

    text-align:center;

    border-radius:20px;

    border:
        1px solid #ead6a5;

    box-shadow:
        0 12px 32px #79500f11;
}

.contact-box .icon{
    font-size:40px;
    margin-bottom:8px;
}

.contact-box h3{
    color:
        #724400;

    margin-bottom:5px;
}

.contact-box p{
    color:
        #655d54;
}

footer{
    margin-top:40px;

    background:
        linear-gradient(
            135deg,
            #180b03,
            #4c2808,
            #1b0b03
        );

    color:white;

    text-align:center;

    padding:
        40px 20px;

    border-top:
        3px solid #d9a832;
}

footer h3{
    color:
        #e4b84d;

    font-size:25px;

    margin-bottom:4px;
}

footer p{
    color:
        #d7cbbd;

    font-size:14px;
}

.footer-gold{
    margin-top:12px;

    color:
        #bda77a;

    font-size:12px;
}

@media(max-width:950px){

    .topbar{
        flex-direction:
            column;
    }

    nav{
        width:100%;
    }

    .photo-section{
        grid-template-columns:
            1fr;
    }

    .about{
        grid-template-columns:
            1fr;
    }
}

@media(max-width:650px){

    .topbar{
        padding:
            12px;
    }

    nav{
        gap:3px;
    }

    nav a{
        font-size:11px;

        padding:
            7px 8px;
    }

    .hero{
        min-height:
            600px;
    }

    .hero-content{
        padding:
            28px 17px;

        border-radius:
            22px;
    }

    section{
        padding:
            60px 15px;
    }

    .feature-grid{
        grid-template-columns:
            1fr;
    }

    .main-photo{
        height:
            300px;
    }
}

</style>

</head>

<body>

<header>

    <div class="topbar">

        <div class="brand">

            <div class="brand-icon">
                ॐ
            </div>

            <div class="brand-text">

                <h1>
                    मैढ़ स्वर्णकार समाज
                </h1>

                <p>
                    Jodhpur, Rajasthan
                </p>

            </div>

        </div>

        <nav>

            <a href="#home">
                🏠 Home
            </a>

            <a href="#about">
                🏛️ समाज
            </a>

            <a href="#bhawan">
                🏢 भवन
            </a>

            <a href="#members">
                👥 सदस्य
            </a>

            <a href="#business">
                🏪 व्यवसाय
            </a>

            <a href="#news">
                📰 समाचार
            </a>

            <a href="#education">
                🎓 शिक्षा
            </a>

            <a href="#gallery">
                📸 Gallery
            </a>

            <a href="#contact">
                📞 Contact
            </a>

        </nav>

    </div>

</header>

<div
    class="hero"
    id="home"
>

    <div class="hero-content">

        <div class="hero-badge">

            🙏 जय श्री अजमेरजी महाराज 🙏

        </div>

        <h2>
            मैढ़ स्वर्णकार समाज
        </h2>

        <h3>
            Jodhpur, Rajasthan
        </h3>

        <p>
            समाज की एकता,
            सेवा,
            संस्कार और विकास
            के लिए एक डिजिटल मंच
        </p>

        <div class="hero-buttons">

            <a
                href="#about"
                class="btn btn-gold"
            >
                🏛️ समाज के बारे में
            </a>

            <a
                href="#bhawan"
                class="btn btn-light"
            >
                🏢 समाज भवन
            </a>

            <a
                href="#events"
                class="btn btn-green"
            >
                🎉 कार्यक्रम
            </a>

        </div>

    </div>

</div>

<section id="about">

    <div class="section-title">

        <span>
            OUR COMMUNITY
        </span>

        <h2>
            समाज के बारे में
        </h2>

        <div class="ornament"></div>

        <p>
            मैढ़ स्वर्णकार समाज — जोधपुर, राजस्थान
        </p>

    </div>

    <div class="about">

        <div class="about-box">

            <h2>
                मैढ़ स्वर्णकार समाज
            </h2>

            <div class="gold-line"></div>

            <p>
                मैढ़ स्वर्णकार समाज समाज के
                सदस्यों को जोड़ने, समाज की
                गतिविधियों को बढ़ावा देने और
                समाज की जानकारी को डिजिटल
                रूप में उपलब्ध कराने का मंच है।
            </p>

            <p>
                इस वेबसाइट पर समाज भवन,
                समाज के कार्यक्रम, समाचार,
                शिक्षा एवं सहायता, सदस्य जानकारी
                और समाज से जुड़ी महत्वपूर्ण
                जानकारी उपलब्ध कराई जाएगी।
            </p>

            <div
                class="hero-buttons"
                style="justify-content:flex-start"
            >

                <a
                    class="btn btn-gold"
                    href="#news"
                >
                    📰 नवीन जानकारी
                </a>

                <a
                    class="btn btn-blue"
                    href="#contact"
                >
                    📞 संपर्क
                </a>

            </div>

        </div>

        <div class="feature-grid">

            <div class="feature">

                <div class="emoji">
                    🤝
                </div>

                <h3>
                    समाज एकता
                </h3>

                <p>
                    समाज के सदस्यों को
                    एक मंच पर जोड़ना।
                </p>

            </div>

            <div class="feature">

                <div class="emoji">
                    🏛️
                </div>

                <h3>
                    समाज विकास
                </h3>

                <p>
                    समाज की गतिविधियों
                    और विकास को बढ़ावा देना।
                </p>

            </div>

            <div class="feature">

                <div class="emoji">
                    ❤️
                </div>

                <h3>
                    समाज सेवा
                </h3>

                <p>
                    जरूरतमंद सदस्यों
                    एवं समाज की सहायता।
                </p>

            </div>

            <div class="feature">

                <div class="emoji">
                    📱
                </div>

                <h3>
                    Digital Society
                </h3>

                <p>
                    समाज की जानकारी
                    को आधुनिक डिजिटल मंच देना।
                </p>

            </div>

        </div>

    </div>

</section>

<section id="bhawan">

    <div class="section-title">

        <span>
            SAMAJ BHAWAN
        </span>

        <h2>
            समाज भवन
        </h2>

        <div class="ornament"></div>

        <p>
            समाज भवन की जानकारी एवं सुविधाएँ
        </p>

    </div>

    <div class="photo-section">

        <div>

            <img
                class="main-photo"
                src="/static/samaj_bhawan.jpg"
                alt="समाज भवन"
            >

        </div>

        <div class="photo-info">

            <h2>
                🏢 समाज भवन
            </h2>

            <p>
                मैढ़ स्वर्णकार समाज के समाज भवन
                से संबंधित जानकारी यहाँ प्रदर्शित
                की जाएगी।
            </p>

            <p>
                भवन में समाज के कार्यक्रम,
                बैठक, सामाजिक समारोह और
                अन्य आवश्यक कार्यक्रम आयोजित
                किए जा सकते हैं।
            </p>

            <div
                class="hero-buttons"
                style="justify-content:flex-start"
            >

                <a
                    class="btn btn-gold"
                    href="#events"
                >
                    📅 कार्यक्रम
                </a>

                <a
                    class="btn btn-blue"
                    href="#contact"
                >
                    📍 Location
                </a>

            </div>

        </div>

    </div>

</section>

<section>

    <div class="section-title">

        <span>
            आस्था
        </span>

        <h2>
            🙏 धार्मिक एवं आध्यात्मिक
        </h2>

        <div class="ornament"></div>

    </div>

    <div class="photo-section">

        <div class="photo-info">

            <h2>
                🛕 भगवान का आशीर्वाद
            </h2>

            <p>
                समाज की परंपरा, संस्कार और
                आध्यात्मिक भावना को सम्मान देते
                हुए यह स्थान समाज से जुड़े
                धार्मिक संदेशों और तस्वीरों के
                लिए रखा गया है।
            </p>

            <p>
                🙏 जय श्री अजमेरजी महाराज 🙏
            </p>

            <a
                class="btn btn-purple"
                href="#gallery"
            >
                📸 धार्मिक Gallery
            </a>

        </div>

        <div>

            <img
                class="main-photo"
                src="/static/bhagwan.jpg"
                alt="भगवान"
            >

        </div>

    </div>

</section>

<section id="members">

    <div class="section-title">

        <span>
            MEMBER DIRECTORY
        </span>

        <h2>
            👥 समाज सदस्य
        </h2>

        <div class="ornament"></div>

        <p>
            समाज के सदस्यों की जानकारी
        </p>

    </div>

    <div class="cards">

        {% for member in members %}

        <div class="card">

            <div class="card-icon">
                👤
            </div>

            <h3>
                {{ member.name }}
            </h3>

            <p>
                <b>
                    व्यवसाय:
                </b>
                {{ member.business }}
            </p>

            <p>
                <b>
                    क्षेत्र:
                </b>
                {{ member.area }}
            </p>

            <br>

            <a
                href="#contact"
                class="btn btn-blue"
            >
                Contact
            </a>

        </div>

        {% endfor %}

    </div>

</section>

<section id="business">

    <div class="section-title">

        <span>
            BUSINESS DIRECTORY
        </span>

        <h2>
            🏪 व्यापार / व्यवसाय
        </h2>

        <div class="ornament"></div>

        <p>
            समाज के व्यवसाय एवं दुकानों की जानकारी
        </p>

    </div>

    <div class="cards">

        {% for business in businesses %}

        <div class="card">

            <div class="card-icon">
                💎
            </div>

            <h3>
                {{ business.name }}
            </h3>

            <p>
                <b>
                    संचालक:
                </b>

                {{ business.owner }}

            </p>

            <p>
                <b>
                    स्थान:
                </b>

                {{ business.area }}

            </p>

            <br>

            <a
                href="#contact"
                class="btn btn-green"
            >
                संपर्क करें
            </a>

        </div>

        {% endfor %}

    </div>

</section>

<section id="events">

    <div class="section-title">

        <span>
            EVENTS & PROGRAMMES
        </span>

        <h2>
            🎉 समाज के कार्यक्रम
        </h2>

        <div class="ornament"></div>

        <p>
            समाज के समारोह, बैठक एवं कार्यक्रम
        </p>

    </div>

    <div class="cards">

        {% for event in events %}

        <div class="event-card">

            <img
                src="/static/{{ event.photo }}"
                alt="{{ event.title }}"
            >

            <div class="event-content">

                <h3>
                    🎉 {{ event.title }}
                </h3>

                <div class="event-date">

                    📅
                    {{ event.date }}

                </div>

                <p>

                    📍
                    {{ event.place }}

                </p>

                <br>

                <a
                    href="#contact"
                    class="btn btn-gold"
                >
                    अधिक जानकारी
                </a>

            </div>

        </div>

        {% endfor %}

    </div>

</section>

<section id="news">

    <div class="section-title">

        <span>
            NEWS & UPDATES
        </span>

        <h2>
            📰 समाचार एवं सूचनाएँ
        </h2>

        <div class="ornament"></div>

    </div>

    <div class="cards">

        {% for item in news %}

        <div class="card">

            <div class="card-icon">
                📢
            </div>

            <h3>
                {{ item.title }}
            </h3>

            <p>
                {{ item.text }}
            </p>

            <br>

            <a
                href="#contact"
                class="btn btn-gold"
            >
                जानकारी
            </a>

        </div>

        {% endfor %}

    </div>

</section>

<section id="education">

    <div class="section-title">

        <span>
            EDUCATION & HELP
        </span>

        <h2>
            🎓 शिक्षा एवं सहायता
        </h2>

        <div class="ornament"></div>

        <p>
            समाज के विद्यार्थियों एवं जरूरतमंद सदस्यों के लिए
        </p>

    </div>

    <div class="cards">

        <div class="card">

            <div class="card-icon">
                🎓
            </div>

            <h3>
                शिक्षा सहायता
            </h3>

            <p>
                विद्यार्थियों की शिक्षा से संबंधित
                सहायता एवं महत्वपूर्ण जानकारी।
            </p>

            <br>

            <a
                href="#contact"
                class="btn btn-blue"
            >
                जानकारी
            </a>

        </div>

        <div class="card">

            <div class="card-icon">
                🏆
            </div>

            <h3>
                प्रतिभा सम्मान
            </h3>

            <p>
                समाज के प्रतिभाशाली विद्यार्थियों
                एवं सदस्यों की उपलब्धियों का सम्मान।
            </p>

            <br>

            <a
                href="#news"
                class="btn btn-purple"
            >
                उपलब्धियाँ
            </a>

        </div>

        <div class="card">

            <div class="card-icon">
                ❤️
            </div>

            <h3>
                समाज सहायता
            </h3>

            <p>
                जरूरतमंद समाज सदस्यों के लिए
                सहायता संबंधी जानकारी।
            </p>

            <br>

            <a
                href="#contact"
                class="btn btn-green"
            >
                सहायता
            </a>

        </div>

        <div class="card">

            <div class="card-icon">
                📢
            </div>

            <h3>
                महत्वपूर्ण सूचना
            </h3>

            <p>
                शिक्षा और सहायता से संबंधित
                announcements यहाँ दिखाई जाएँगी।
            </p>

            <br>

            <a
                href="#news"
                class="btn btn-gold"
            >
                Notices
            </a>

        </div>

    </div>

</section>

<section>

    <div class="donation">

        <h2>
            ❤️ समाज के लिए सहयोग
        </h2>

        <p>
            समाज के विकास,
            सेवा कार्यों एवं सामाजिक गतिविधियों
            में अपना सहयोग प्रदान करें।
        </p>

        <div class="hero-buttons">

            <a
                href="#contact"
                class="btn btn-light"
            >
                💰 सहयोग की जानकारी
            </a>

            <a
                href="#about"
                class="btn btn-gold"
            >
                🤝 समाज सेवा
            </a>

        </div>

    </div>

</section>

<section id="gallery">

    <div class="section-title">

        <span>
            PHOTO GALLERY
        </span>

        <h2>
            📸 समाज Gallery
        </h2>

        <div class="ornament"></div>

        <p>
            समाज भवन, धार्मिक एवं कार्यक्रमों की तस्वीरें
        </p>

    </div>

    <div class="gallery">

        <div class="gallery-item">

            <img
                src="/static/samaj_bhawan.jpg"
                alt="समाज भवन"
            >

            <div class="gallery-caption">
                🏢 समाज भवन
            </div>

        </div>

        <div class="gallery-item">

            <img
                src="/static/ajmerji_maharaj.jpg"
                alt="अजमेरजी महाराज"
            >

            <div class="gallery-caption">
                🙏 अजमेरजी महाराज
            </div>

        </div>

        <div class="gallery-item">

            <img
                src="/static/bhagwan.jpg"
                alt="भगवान"
            >

            <div class="gallery-caption">
                🛕 भगवान
            </div>

        </div>

        <div class="gallery-item">

            <img
                src="/static/function1.jpg"
                alt="समाज कार्यक्रम"
            >

            <div class="gallery-caption">
                🎉 समाज कार्यक्रम
            </div>

        </div>

        <div class="gallery-item">

            <img
                src="/static/function2.jpg"
                alt="समाज कार्यक्रम"
            >

            <div class="gallery-caption">
                🎊 समाज समारोह
            </div>

        </div>

        <div class="gallery-item">

            <img
                src="/static/function3.jpg"
                alt="समाज कार्यक्रम"
            >

            <div class="gallery-caption">
                👥 समाज मिलन
            </div>

        </div>

        <div class="gallery-item">

            <img
                src="/static/function4.jpg"
                alt="समाज कार्यक्रम"
            >

            <div class="gallery-caption">
                ✨ यादगार पल
            </div>

        </div>

        <div class="gallery-item">

            <img
                src="/static/samaj_bhawan.jpg"
                alt="भवन"
            >

            <div class="gallery-caption">
                🏛️ समाज भवन
            </div>

        </div>

    </div>

</section>

<section id="contact">

    <div class="section-title">

        <span>
            CONTACT US
        </span>

        <h2>
            📞 संपर्क करें
        </h2>

        <div class="ornament"></div>

        <p>
            मैढ़ स्वर्णकार समाज, Jodhpur
        </p>

    </div>

    <div class="contact-grid">

        <div class="contact-box">

            <div class="icon">
                📍
            </div>

            <h3>
                पता
            </h3>

            <p>
                Jodhpur, Rajasthan
            </p>

            <br>

            <a
                class="btn btn-blue"
                href="https://www.google.com/maps/search/Jodhpur+Rajasthan"
                target="_blank"
            >
                🗺️ Map
            </a>

        </div>

        <div class="contact-box">

            <div class="icon">
                📞
            </div>

            <h3>
                संपर्क
            </h3>

            <p>
                समाज की contact information
                यहाँ उपलब्ध होगी।
            </p>

        </div>

        <div class="contact-box">

            <div class="icon">
                📧
            </div>

            <h3>
                Email
            </h3>

            <p>
                समाज की official email
                यहाँ उपलब्ध होगी।
            </p>

        </div>

        <div class="contact-box">

            <div class="icon">
                🙏
            </div>

            <h3>
                जय श्री अजमेरजी महाराज
            </h3>

            <p>
                मैढ़ स्वर्णकार समाज
            </p>

        </div>

    </div>

</section>

<footer>

    <h3>
        💎 मैढ़ स्वर्णकार समाज
    </h3>

    <p>
        Jodhpur, Rajasthan
    </p>

    <p>
        समाज की एकता • सेवा • संस्कार • विकास
    </p>

    <div class="footer-gold">

        🙏 जय श्री अजमेरजी महाराज 🙏

    </div>

</footer>

</body>

</html>
"""


# ============================================================
# HOME ROUTE
# ============================================================

@app.route("/")
def home():

    return render_template_string(

        BASE_HTML,

        title="Home",

        members=MEMBERS,

        businesses=BUSINESSES,

        news=NEWS,

        events=EVENTS

    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("          मैढ़ स्वर्णकार समाज - WEBSITE")
    print("          Jodhpur, Rajasthan")
    print("=" * 65)
    print()
    print("Browser में खोलें:")
    print("http://127.0.0.1:5000")
    print()
    print("Developer: KRISHNA")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )
