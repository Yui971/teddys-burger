#!/usr/bin/env python3
"""Génère les pages du site Teddy's Burger à partir de tools/menu.json.

Usage : python3 tools/build.py   (depuis la racine du projet)
Pour changer un prix ou un plat : modifier tools/menu.json puis relancer.
Aperçu GitHub Pages : python3 tools/build.py --base /teddys-burger/ --preview
  (--base : dossier où le site est servi, pour les chemins de la 404 ;
   --preview : pages en noindex pour ne pas concurrencer le vrai site)
"""
import html
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARGS = sys.argv[1:]
BASE = ARGS[ARGS.index("--base") + 1] if "--base" in ARGS else "/"
PREVIEW = "--preview" in ARGS
MENU = json.loads((ROOT / "tools" / "menu.json").read_text(encoding="utf-8"))

SITE_URL = "https://www.teddysburger.com"
ORDER_URL = ("https://www.foodbooking.com/ordering/restaurant/menu"
             "?company_uid=f4e176ff-b0b0-4b32-a2d7-f04510ba4fc4"
             "&restaurant_uid=5dd35384-f3b1-45e0-9185-c5fd94e0f00c&facebook=false")
PHONE_HREF = "tel:+590690317713"
PHONE = "0690 31 77 13"
ADDRESS_LINES = ["22 rue des Goyaviers", "Grand Fond Macaille", "97121 Anse-Bertrand"]
ADDRESS_ONE = "22 rue des Goyaviers, Grand Fond Macaille, 97121 Anse-Bertrand, Guadeloupe"
PLACE_ID = "ChIJTRhRaHIwE4wRmwLr2E7x73U"
MAPS = "https://www.google.com/maps/dir/?api=1&destination=Teddy%27s%20Burger%20Anse-Bertrand&destination_place_id=" + PLACE_ID
REVIEW_WRITE = "https://search.google.com/local/writereview?placeid=" + PLACE_ID
REVIEW_READ = "https://www.google.com/maps/place/?q=place_id:" + PLACE_ID
WAZE = "https://waze.com/ul?ll=16.467261,-61.503232&navigate=yes"
GLEENCE = "https://gleence.com/en/gleence.html"
DESIGNER = "Chrisnaël Berdier"
DESIGNER_URL = "https://chrisnaelberdier.com"
DESIGNER_MAIL = "berdierchrisnael@gmail.com"
FACEBOOK = "https://www.facebook.com/teddysburger97121"
INSTAGRAM = "https://www.instagram.com/teddys_burger"

e = html.escape


def price(p):
    return f"{p:,.2f}".replace(".", ",") + " €"


def ext(label):
    return f'{label}<span class="sr-only"> (nouvel onglet)</span>'


def order_btn(label="Commander à emporter", cls="btn"):
    return f'<a class="{cls}" href="{ORDER_URL}" target="_blank" rel="noopener">{ext(e(label))}</a>'


STATUS = ('<p class="status" data-status data-state="closed" aria-live="polite">'
          '<span class="status__dot" aria-hidden="true"></span>'
          '<span><span class="status__text">Ouvert du mercredi au dimanche, le soir</span>'
          '<span class="status__sub">Pas de livraison, à emporter uniquement</span></span></p>')

LOADER = """<div class="loader" id="loader" role="status" aria-label="Chargement">
  <div class="loader__stack" aria-hidden="true">
    <span class="loader__layer" style="top:238px;height:27px;background-position:0 -238px;animation-delay:0ms"></span>
    <span class="loader__layer" style="top:173px;height:65px;background-position:0 -173px;animation-delay:90ms"></span>
    <span class="loader__layer" style="top:150px;height:23px;background-position:0 -150px;animation-delay:180ms"></span>
    <span class="loader__layer" style="top:60px;height:90px;background-position:0 -60px;animation-delay:270ms"></span>
    <span class="loader__layer" style="top:0;height:60px;background-position:0 0;animation-delay:380ms"></span>
    <span class="loader__label">Teddy's Burger</span>
  </div>
</div>"""


def head(title, desc, path, extra=""):
    canonical = SITE_URL + "/" + ("" if path == "index.html" else path)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.classList.add("js");</script>
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#cf1f25">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Teddy's Burger">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/assets/og-image.jpg">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="apple-touch-icon" href="assets/favicon-180.png">
<link rel="preload" href="assets/fonts/bricolage-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/logo-teddys.webp" as="image">
<link rel="stylesheet" href="css/style.css">
<script src="js/site.js" defer></script>
{extra}</head>
"""


def header(current):
    def nav(href, label, key, cls=""):
        cur = ' aria-current="page"' if key == current else ""
        c = f' class="{cls}"' if cls else ""
        return f'<a href="{href}"{cur}{c}>{label}</a>'
    return f"""<a class="skip" href="#contenu">Aller au contenu</a>
<header class="site-header">
  <a class="brand" href="index.html" data-logo aria-label="Teddy's Burger, retour à l'accueil">
    <img src="assets/logo-badge.webp" alt="" width="196" height="162">
  </a>
  <nav class="site-nav" aria-label="Navigation principale">
    {nav("carte.html", "La carte", "carte")}
    {nav("index.html#infos", "Horaires et accès", "infos", "nav-hide-sm")}
    {order_btn("Commander", "btn")}
  </nav>
</header>
"""


CREDITS_INDEX = ('Photo de la section « Venir au snack » : <a href="https://commons.wikimedia.org/w/index.php?curid=102979565">« Porte d\'Enfer Anse-Bertrand (Guadeloupe) »</a> '
                 'par Daniel Jolivet, <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, via Wikimedia Commons.')
CREDITS = ('Photos de la commune : <a href="https://commons.wikimedia.org/w/index.php?curid=102979565">« Porte d\'Enfer Anse-Bertrand (Guadeloupe) »</a> '
           'par Daniel Jolivet, <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a> ; '
           '<a href="https://commons.wikimedia.org/w/index.php?curid=81625195">« Pointe de la Grande Vigie (Anse-Bertrand) »</a> '
           'par Gauthier Geoffroy, <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> ; via Wikimedia Commons.')


def footer(credits=False):
    return f"""<footer class="site-footer">
  <div class="site-footer__photo">
    <img src="assets/burger-campeche-serre.webp" alt="Le Big Campêche en gros plan : steak haché, poulet pané et sauce fromage" width="590" height="590" loading="lazy">
  </div>
  <div class="site-footer__body">
    <a class="site-footer__brand" href="index.html" data-logo aria-label="Teddy's Burger, retour à l'accueil"><img src="assets/logo-badge.webp" alt="" width="196" height="162" loading="lazy"></a>
    <nav class="foot-menu" aria-label="Pied de page">
      <a href="index.html" data-logo>Accueil</a>
      <a href="carte.html">La carte</a>
      <a href="{ORDER_URL}" target="_blank" rel="noopener">{ext("Commander")}</a>
      <a href="index.html#fidelite">Fidélité</a>
      <a href="index.html#infos">Horaires et accès</a>
    </nav>
    <div class="foot-info">
      <div>
        <strong>Teddy's Burger</strong>
        {"<br>".join(e(l) for l in ADDRESS_LINES)}<br>
        <a href="{PHONE_HREF}">{PHONE}</a>
      </div>
      <div>
        <strong>Suis le snack</strong>
        <a href="{FACEBOOK}" target="_blank" rel="noopener">{ext("Facebook")}</a><br>
        <a href="{INSTAGRAM}" target="_blank" rel="noopener">{ext("Instagram")}</a>
      </div>
    </div>
    <div class="foot-legal">
      <p>© <span data-year>2026</span> Teddy's Burger · <a href="mentions-legales.html">Mentions légales</a> · <a href="confidentialite.html">Confidentialité</a> · <a href="confidentialite.html#cookies">Cookies</a></p>
      <p>Site conçu et réalisé par <a href="{DESIGNER_URL}" target="_blank" rel="noopener">{ext("Chrisnaël Berdier")}</a></p>
      <p>L'abus d'alcool est dangereux pour la santé, à consommer avec modération.</p>
      {f'<p class="credits">{CREDITS_INDEX}</p>' if credits else ""}
    </div>
  </div>
</footer>
"""


MOBILE_BAR = f"""<div class="mbar" role="region" aria-label="Commander">
  <p class="mbar__status" data-status data-state="closed"><span class="status__dot" aria-hidden="true"></span><span class="status__text">Mer. au dim., le soir</span></p>
  <a class="mbar__call" href="{PHONE_HREF}" aria-label="Appeler le snack au {PHONE}"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg></a>
  {order_btn("Commander", "btn mbar__order")}
</div>"""


def page(title, desc, path, current, main, extra_head="", credits=False):
    return (head(title, desc, path, extra_head) + "<body>\n" + LOADER + "\n" + header(current)
            + f'<main id="contenu">\n{main}\n</main>\n' + footer(credits) + MOBILE_BAR + "\n</body>\n</html>\n")


def hours_table(cls="hours"):
    rows = [
        ("Lundi et mardi", "1,2", "Fermé", True),
        ("Mercredi", "3", "18h30 à 22h", False),
        ("Jeudi", "4", "18h30 à 22h", False),
        ("Vendredi", "5", "18h30 à 22h", False),
        ("Samedi", "6", "18h30 à 22h", False),
        ("Dimanche", "0", "17h30 à 21h", False),
    ]
    closed_attr = ' class="is-closed"'
    today_tag = '<span class="today-tag sr-only" hidden> (aujourd&#39;hui)</span>'
    trs = "\n".join(
        f'<tr data-days="{d}"{closed_attr if closed else ""}><th scope="row">{day}{today_tag}</th><td>{t}</td></tr>'
        for day, d, t, closed in rows)
    return f'<table class="{cls}"><caption class="sr-only">Horaires d\'ouverture</caption><tbody>\n{trs}\n</tbody></table>'


IMG = set(MENU["item_images"])


def all_items():
    for cat in MENU["categories"]:
        for it in cat["items"]:
            yield cat, it



# Avis Google réels (extraits fidèles, fautes de frappe corrigées), relevés le 26/10/2026
REVIEWS = [
    ("Le pain brioché est au top. On sent que c'est du fait maison. La viande est parfaite, les portions de frites sont très généreuses.", "isa59 Gege", "août 2026"),
    ("Très bonne adresse. Les burgers sont bons et faits maison. Bon accueil.", "Estelle W.", "avril 2026"),
    ("Choisissez le Teddy's burger, c'est énorme ! Commande effectuée via le site web, temps indiqué respecté, commande prête à mon arrivée.", "Cédric", "juillet 2026"),
    ("Le pain est moelleux et brioché, la garniture au top, c'est copieux, bref un sans-faute. Tout le personnel est accueillant et chaleureux.", "Cécilia M.", "janvier 2022"),
    ("Bons, copieux et d'un très bon rapport qualité-prix. Commande par téléphone : accueil avec le sourire.", "Claire D.", "novembre 2024"),
    ("Une adresse qui vaut le détour à Anse-Bertrand.", "isa59 Gege", "août 2026"),
]


def reviews_section():
    def card(q, who, when, hidden=False):
        aria = ' aria-hidden="true"' if hidden else ""
        return (f'<li class="review"{aria}><blockquote><p>« {e(q)} »</p></blockquote>'
                f'<p class="review__who"><strong>{e(who)}</strong><span>Avis Google · {e(when)}</span></p></li>')
    cards = "".join(card(*r) for r in REVIEWS)
    clones = "".join(card(*r, hidden=True) for r in REVIEWS)
    return f"""<section class="reviews" id="avis" aria-labelledby="avis-titre">
  <div class="reviews__head">
    <h2 class="reveal" id="avis-titre">Ce qu'en disent les clients</h2>
    <div class="reviews__score reveal" style="--d:80ms">
      <p class="reviews__note"><span class="tabular">4,4</span><span>/5</span></p>
      <p>Sur 255 avis Google, dont 217 à 4 ou 5 étoiles.</p>
    </div>
  </div>
  <div class="marquee" data-marquee>
    <ul class="marquee__track">{cards}{clones}</ul>
  </div>
  <div class="reviews__actions">
    <a class="btn" href="{REVIEW_WRITE}" target="_blank" rel="noopener">{ext("Laisser un avis sur Google")}</a>
    <a class="btn btn--cream" href="{REVIEW_READ}" target="_blank" rel="noopener">{ext("Lire tous les avis")}</a>
    <button class="chip marquee__toggle" type="button" data-marquee-toggle aria-pressed="false">Mettre en pause</button>
  </div>
</section>
"""

# ---------------------------------------------------------------- accueil
def build_index():
    burgers = next(c for c in MENU["categories"] if c["id"] == "burgers")
    rows = []
    for it in burgers["items"]:
        photo = f'assets/menu/{it["id"]}.webp'
        cls = "row row--house" if it.get("house") else "row"
        place = f'Quartier : {e(it["place"])}' if it.get("place") else ("Le burger de la maison" if it.get("house") else ("Végétarien" if it.get("veg") else ""))
        rows.append(f"""<li class="{cls}" data-photo="{photo}" data-name="{e(it['name'])}" tabindex="0">
  <img class="row__thumb" src="{photo}" alt="" width="192" height="192" loading="lazy">
  <span class="row__text"><span class="row__name">{e(it['name'])}</span><span class="row__note">{e(it['desc'])}</span></span>
  <span class="row__place">{place}</span>
  <span class="row__price">{price(it['price'])}</span>
</li>""")
    places = [it["place"] for it in burgers["items"] if it.get("place")]
    places_html = "".join(f"<li>{e(p)}</li>" for p in places)

    main = f"""<section class="hero" aria-labelledby="titre">
  <div class="hero__copy">
    <h1 class="hero__title" id="titre">Teddy's Burger</h1>
    <div class="hero__tagline">
      <p class="hero__lead">LA référence fast food à <span class="nowrap">Anse-Bertrand</span>.</p>
      <p class="hero__info">Burgers faits à la commande · <span class="nowrap">à emporter le soir</span> · <span class="nowrap">pas de livraison</span></p>
    </div>
    <div class="hero__actions">
      {STATUS}
      <div class="hero__btns">
        {order_btn()}
        <a class="btn btn--cream" href="{MAPS}" target="_blank" rel="noopener">{ext("Itinéraire")}</a>
      </div>
    </div>
  </div>
  <div class="hero__stage">
    <div class="plinth">
      <div class="plinth__item plinth__item--logo is-on"><img src="assets/logo-teddys.webp" alt="Le logo de Teddy's Burger : un ourson posé sur un double cheeseburger" width="348" height="658" fetchpriority="high"></div>
      <div class="plinth__item plinth__item--photo"><img src="assets/burger-massioux.webp" alt="Le Big Massioux : poisson pané, poulet pané, salade et sauces" width="944" height="780"></div>
      <div class="plinth__item plinth__item--photo"><img src="assets/burger-campeche-serre.webp" alt="Le Big Campêche : steak haché, poulet pané, salade et sauce fromage" width="590" height="590"></div>
    </div>
  </div>
</section>

<section class="ride" aria-labelledby="burgers">
  <div class="ride__track">
    <div class="ride__rail" aria-hidden="true">
      <div class="ride__object"><img class="obj-logo" src="assets/logo-teddys.webp" alt="" width="348" height="658"><img class="obj-photo" src="assets/menu/big-teddys.webp" alt="" width="192" height="192"></div>
    </div>
    <h2 class="ride__head" id="burgers"><span>Burgers</span><span class="gap" aria-hidden="true"></span><span>ansois</span></h2>
    <div class="ride__intro">
      <p class="reveal">Steak haché de 150 g, poulet ou poisson pané, préparés quand tu commandes.</p>
      <p class="reveal" style="--d:90ms">Passe sur un burger pour le voir en photo.</p>
    </div>
    <div class="ride__list">
      <ul>
{chr(10).join(rows)}
      </ul>
    </div>
  </div>
  <div class="ride__more">
    <a class="btn btn--cream" href="carte.html">Toute la carte, avec les wraps et les Big Dog</a>
  </div>
</section>

<section class="quartiers" aria-labelledby="quartiers-titre">
  <div class="panel">
    <div class="panel__left">
      <h2 class="panel__title reveal" id="quartiers-titre">Un burger, un quartier</h2>
      <div class="panel__shape reveal" style="--d:120ms"><img src="assets/burger-massioux.webp" alt="Le Big Massioux en gros plan, découpé en tête d'ours" width="944" height="780" loading="lazy"></div>
    </div>
    <div class="panel__right">
      <div class="panel__block reveal" style="--d:80ms">
        <h3>Un snack de famille, à Anse-Bertrand</h3>
        <p>Teddy's Burger est installé à Grand Fond Macaille. Chaque burger porte le nom d'un coin de la commune. Trouve le tien :</p>
        <ul class="places" aria-label="Les quartiers de la carte">{places_html}</ul>
      </div>
      <div class="panel__block reveal" style="--d:160ms">
        <h3>Fait à la commande</h3>
        <p>Rien n'attend sous une lampe chauffante. On prépare ton burger au moment où tu le commandes : ça prend quelques minutes de plus qu'une grande chaîne, et c'est ce qui fait la différence.</p>
      </div>
      <div class="reveal" style="--d:220ms"><a class="btn" href="carte.html">Voir la carte</a></div>
    </div>
  </div>
</section>

{reviews_section()}
<section class="order" id="commander" aria-labelledby="commander-titre">
  <div class="order__grid">
    <div class="order__intro">
      <h2 class="reveal" id="commander-titre">Commander, c'est simple</h2>
      <p class="reveal" style="--d:80ms">Pas de livraison : tu commandes, on prépare, tu passes récupérer au snack. Si la commande en ligne est fermée, un coup de fil suffit.</p>
      <div class="reveal" style="--d:140ms">{order_btn("Commander à emporter", "btn btn--ink")}</div>
    </div>
    <div class="slip reveal" style="--d:120ms" role="group" aria-label="Le ticket de commande">
      <div class="slip__top"><span>Ticket de commande</span><img src="assets/logo-badge.webp" alt="" width="196" height="162" loading="lazy"></div>
      <h3>En ligne</h3>
      <div class="slip__row"><span>Choisis tes burgers</span><span class="dots" aria-hidden="true"></span><span>sur la carte</span></div>
      <div class="slip__row"><span>Valide ta commande</span><span class="dots" aria-hidden="true"></span><span>à emporter</span></div>
      <div class="slip__row"><span>Paie</span><span class="dots" aria-hidden="true"></span><span>en ligne ou sur place</span></div>
      <h3>Par téléphone</h3>
      <div class="slip__row"><span>Appelle le snack</span><span class="dots" aria-hidden="true"></span><a href="{PHONE_HREF}">{PHONE}</a></div>
      <h3>Au snack</h3>
      <div class="slip__row"><span>On prépare</span><span class="dots" aria-hidden="true"></span><span>à la commande</span></div>
      <div class="slip__row"><span>Tu récupères</span><span class="dots" aria-hidden="true"></span><span>22 rue des Goyaviers</span></div>
      <div class="slip__row"><span>Moyens de paiement</span><span class="dots" aria-hidden="true"></span><span>espèces, carte, PayPal</span></div>
      <div class="slip__total"><span>Ton burger, chaud, à emporter</span><span>en ligne jusqu'à 21h45</span></div>
    </div>
  </div>
</section>

<section class="loyalty" id="fidelite" aria-labelledby="fidelite-titre">
  <div class="loyalty__media"><img src="assets/ours-teddy.webp" alt="Teddy, l'ours de la marque, croque un burger au milieu des frites et des milkshakes" width="1024" height="1080" loading="lazy"></div>
  <div class="loyalty__text">
    <h2 class="reveal" id="fidelite-titre">Ta carte de fidélité</h2>
    <p class="reveal" style="--d:80ms">La carte de fidélité Teddy's est 100&nbsp;% numérique, dans l'appli Gleence.</p>
    <ol class="loyalty__steps reveal" style="--d:140ms">
      <li>Télécharge l'appli Gleence</li>
      <li>Crée ton compte client</li>
      <li>On scanne ton QR code à chaque passage</li>
    </ol>
    <p class="loyalty__fact reveal" style="--d:180ms">Rien à imprimer, rien à perdre.</p>
    <div class="reveal" style="--d:220ms"><a class="btn" href="{GLEENCE}" target="_blank" rel="noopener">{ext("Découvrir Gleence")}</a></div>
  </div>
</section>

<section class="visit" id="infos" aria-labelledby="infos-titre">
  <div class="visit__photo">
    <img src="assets/porte-d-enfer.webp" alt="Les falaises de la Porte d'Enfer, au nord d'Anse-Bertrand" width="1920" height="1280" loading="lazy">
    <p class="visit__caption">La Porte d'Enfer, à Anse-Bertrand</p>
  </div>
  <div class="visit__card">
    <h2 id="infos-titre">Venir au snack</h2>
    <address class="visit__addr">{"<br>".join(e(l) for l in ADDRESS_LINES)}</address>
    <div class="visit__tools">
      <a class="chip" href="{MAPS}" target="_blank" rel="noopener">{ext("Itinéraire Google Maps")}</a>
      <a class="chip" href="{WAZE}" target="_blank" rel="noopener">{ext("Waze")}</a>
      <button class="chip" type="button" data-copy="{e(ADDRESS_ONE)}">Copier l'adresse</button>
    </div>
    <div class="visit__status">{STATUS}</div>
    {hours_table()}
    <p class="visit__note">Commande en ligne du mercredi au samedi jusqu'à 21h45, le dimanche jusqu'à 20h45. Pas de livraison.</p>
    <a class="visit__phone" href="{PHONE_HREF}">{PHONE}</a>
    {order_btn("Commander à emporter", "btn btn--ink")}
  </div>
</section>
"""
    schema = {
        "@context": "https://schema.org",
        "@type": "Restaurant",
        "name": "Teddy's Burger",
        "url": SITE_URL,
        "image": SITE_URL + "/assets/logo-teddys.png",
        "telephone": "+590690317713",
        "servesCuisine": ["Burgers", "Fast food"],
        "priceRange": "€",
        "hasMenu": SITE_URL + "/carte.html",
        "acceptsReservations": False,
        "address": {"@type": "PostalAddress", "streetAddress": "22 rue des Goyaviers, Grand Fond Macaille",
                    "postalCode": "97121", "addressLocality": "Anse-Bertrand", "addressRegion": "Guadeloupe", "addressCountry": "GP"},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Wednesday", "Thursday", "Friday", "Saturday"], "opens": "18:30", "closes": "22:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "17:30", "closes": "21:00"},
        ],
        "sameAs": [FACEBOOK, INSTAGRAM],
    }
    extra = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>\n'
    return page("Teddy's Burger · Burgers à emporter à Anse-Bertrand, Guadeloupe",
                "Snack familial à Anse-Bertrand : burgers faits à la commande, wraps, Big Dog et wings. Commande en ligne, à emporter du mercredi au dimanche soir.",
                "index.html", "home", main, extra, credits=True)


# ---------------------------------------------------------------- carte
def build_carte():
    chips = ['<button class="chip" type="button" data-cat="all" aria-pressed="true">Tout</button>']
    secs = []
    total = 0
    for cat in MENU["categories"]:
        chips.append(f'<button class="chip" type="button" data-cat="{cat["id"]}" aria-pressed="false">{e(cat["name"])}</button>')
        dishes = []
        for it in cat["items"]:
            total += 1
            if it["id"] in IMG:
                thumb = f'<img class="dish__thumb" src="assets/menu/{it["id"]}.webp" alt="" width="192" height="192" loading="lazy">'
            else:
                thumb = f'<img class="dish__thumb" src="assets/menu/{cat["image"]}" alt="" width="375" height="130" loading="lazy">'
            tag = ""
            if it.get("house"):
                tag = "<small>de la maison</small>"
            elif it.get("veg"):
                tag = "<small>végétarien</small>"
            place = f" Quartier : {it['place']}." if it.get("place") else ""
            pr = ("à partir de<br>" if it.get("from") else "") + price(it["price"])
            search = " ".join([it["name"], it["desc"], cat["name"], it.get("place", ""), "vegetarien vege" if it.get("veg") else ""])
            dishes.append(f"""<div class="dish reveal" style="--d:{min(len(dishes), 6) * 60}ms" data-search="{e(search)}">
  {thumb}
  <div><p class="dish__name">{e(it['name'])}{tag}</p><p class="dish__desc">{e(it['desc'])}.{e(place)}</p></div>
  <p class="dish__price">{pr}</p>
</div>""")
        secs.append(f"""<section class="menu-cat" id="{cat['id']}" aria-labelledby="t-{cat['id']}">
  <div class="menu-cat__head reveal">
    <h2 id="t-{cat['id']}">{e(cat['name'])}</h2>
    <p>{e(cat['intro'])}</p>
    <img src="assets/menu/{cat['image']}" alt="" width="375" height="130" loading="lazy">
  </div>
  <div class="menu-cat__items">
{chr(10).join(dishes)}
  </div>
</section>""")
    main = f"""<section class="menu-hero" aria-labelledby="titre">
  <h1 id="titre">La carte</h1>
  <div class="menu-hero__side">
    <p>Burgers, wraps, Big Dog, wings, desserts et boissons. Tous les prix sont à emporter.</p>
    {STATUS}
    {order_btn()}
  </div>
</section>
<div class="menu-tools">
  <label class="search">
    <span class="sr-only">Chercher sur la carte</span>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m20 20-4.6-4.6"/></svg>
    <input id="menu-search" type="search" placeholder="Bacon, poulet, végé…" autocomplete="off">
  </label>
  <div class="cats" role="group" aria-label="Catégories">
    {"".join(chips)}
  </div>
  <p class="sr-only" aria-live="polite" data-count>{total} produits</p>
</div>
<div class="menu" id="menu">
  <p class="menu-empty" hidden>Rien sur la carte pour « <span data-q></span> ». <button class="chip" type="button" data-reset>Tout afficher</button></p>
{chr(10).join(secs)}
</div>
<section class="order-band" aria-labelledby="commander-titre">
  <h2 id="commander-titre">Ton choix est fait ?</h2>
  <div class="order-band__side">
    <p>Commande en ligne et récupère au snack, ou appelle le <a href="{PHONE_HREF}">{PHONE}</a>.</p>
    {order_btn()}
  </div>
</section>
"""
    return page("La carte · Teddy's Burger, Anse-Bertrand",
                "Toute la carte de Teddy's Burger avec les prix : burgers des quartiers d'Anse-Bertrand, burgers spéciaux, Big Dog, wraps, wings, desserts et boissons.",
                "carte.html", "carte", main)


# ---------------------------------------------------------------- mentions légales
def todo(txt):
    return f'<span class="todo">{txt}</span>'


def build_legal():
    main = f"""<div class="plain">
  <div class="plain__head">
    <h1 id="titre">Mentions légales</h1>
    <p>Qui édite ce site, qui l'a conçu, où il est hébergé et ce que tu as le droit d'en faire.</p>
    <div class="plain__media reveal"><img src="assets/grande-vigie.webp" alt="La Pointe de la Grande Vigie, au nord d'Anse-Bertrand" width="1600" height="1200"></div>
  </div>
  <div class="plain__body">
    <h2 class="reveal">Éditeur du site</h2>
    <p>Teddy's Burger, snack.<br>{", ".join(e(l) for l in ADDRESS_LINES)}, Guadeloupe<br>Téléphone : <a href="{PHONE_HREF}">{PHONE}</a></p>
    <p>Forme juridique et capital : {todo("à compléter")}<br>SIRET : {todo("à compléter")}<br>Adresse e-mail : {todo("à compléter")}<br>Directeur de la publication : {todo("à compléter (le ou la gérante)")}</p>

    <h2 class="reveal">Conception et réalisation</h2>
    <p>Site conçu, designé et développé par {DESIGNER}, designer graphique et web en Guadeloupe.</p>
    <p>Contact : <a href="mailto:{DESIGNER_MAIL}">{DESIGNER_MAIL}</a><br>Portfolio : <a href="{DESIGNER_URL}" target="_blank" rel="noopener">{ext("chrisnaelberdier.com")}</a></p>

    <h2 class="reveal">Hébergement</h2>
    <p>{todo("Nom, adresse et téléphone de l'hébergeur, à compléter à la mise en ligne.")}</p>

    <h2 class="reveal">Propriété intellectuelle</h2>
    <p>Le nom, le logo, les visuels, les photos des plats et les textes de ce site appartiennent à Teddy's Burger. Toute reproduction, même partielle, est interdite sans son autorisation écrite.</p>
    <p>{CREDITS} Ces photos montrent la commune, pas le snack.</p>

    <h2 class="reveal">Commandes en ligne</h2>
    <p>Les commandes et les paiements en ligne sont traités par FoodBooking (GloriaFood, Oracle), qui applique ses propres conditions, affichées au moment de commander.</p>

    <h2 class="reveal">Liens externes</h2>
    <p>Le site renvoie vers des services extérieurs (FoodBooking, Gleence, Google Maps, Waze, Facebook, Instagram). Teddy's Burger n'est pas responsable de leur contenu ni de leurs règles.</p>

    <h2 class="reveal">Données personnelles et cookies</h2>
    <p>Tout est expliqué sur la page <a href="confidentialite.html">Confidentialité et cookies</a>.</p>

    <h2 class="reveal">Alcool</h2>
    <p>L'abus d'alcool est dangereux pour la santé, à consommer avec modération. La vente d'alcool est interdite aux mineurs.</p>

    <h2 class="reveal">Droit applicable</h2>
    <p>Ce site et ces mentions sont soumis au droit français.</p>
  </div>
</div>
"""
    return page("Mentions légales · Teddy's Burger", "Mentions légales du site de Teddy's Burger, snack à Anse-Bertrand : éditeur, conception, hébergement, crédits.",
                "mentions-legales.html", "legal", main)


# ---------------------------------------------------------------- confidentialité et cookies
def build_privacy():
    main = f"""<div class="plain">
  <div class="plain__head">
    <h1 id="titre">Confidentialité et cookies</h1>
    <p>En bref : ce site ne dépose aucun cookie et ne collecte aucune donnée sur toi. Le détail est juste à côté.</p>
    <div class="plain__media reveal"><img src="assets/burger-massioux.webp" alt="Le Big Massioux, burger de la maison" width="944" height="780"></div>
  </div>
  <div class="plain__body">
    <h2 class="reveal">Qui est responsable</h2>
    <p>Teddy's Burger, {", ".join(e(l) for l in ADDRESS_LINES)}. Téléphone : <a href="{PHONE_HREF}">{PHONE}</a>.</p>

    <h2 class="reveal">Ce que ce site collecte</h2>
    <p>Rien. Il n'y a ni formulaire, ni compte, ni lettre d'information, ni outil de mesure d'audience. Les polices de caractères, les images et les scripts sont hébergés sur le site lui-même : ta visite n'est transmise à aucun service tiers.</p>
    <p>Comme tout serveur web, l'hébergeur peut garder des journaux techniques (adresse IP, date, page demandée) pour la sécurité du site, pendant une durée limitée. {todo("À préciser selon l'hébergeur choisi.")}</p>

    <h2 id="cookies" class="reveal">Cookies</h2>
    <p>Ce site ne dépose aucun cookie ni aucun autre traceur sur ton appareil. C'est pour ça qu'il n'affiche pas de bandeau de consentement : la CNIL ne l'exige que lorsqu'un site utilise des traceurs.</p>
    <p>Si un jour un outil de mesure d'audience ou une vidéo intégrée est ajouté, cette page sera mise à jour et ton accord sera demandé avant tout dépôt de cookie non nécessaire.</p>

    <h2 class="reveal">Quand tu quittes le site</h2>
    <p>Certains boutons ouvrent des services extérieurs, qui ont leurs propres règles de confidentialité et peuvent déposer leurs propres cookies :</p>
    <ul>
      <li><strong>FoodBooking (GloriaFood, Oracle)</strong> pour commander et payer : nom, téléphone et détail de la commande sont traités pour préparer ta commande. Leur politique et leurs réglages de cookies s'affichent au moment de commander.</li>
      <li><strong>Gleence</strong> pour la carte de fidélité.</li>
      <li><strong>Google Maps et Waze</strong> pour l'itinéraire.</li>
      <li><strong>Facebook et Instagram</strong> pour suivre le snack.</li>
    </ul>

    <h2 class="reveal">Tes droits</h2>
    <p>Pour toute question sur tes données, notamment liées à une commande, tu peux contacter le snack au <a href="{PHONE_HREF}">{PHONE}</a> ou à l'adresse {todo("e-mail à compléter")}. Tu peux demander l'accès, la rectification ou l'effacement de tes données, et t'opposer à leur utilisation.</p>
    <p>Si tu estimes que tes droits ne sont pas respectés, tu peux saisir la CNIL : <a href="https://www.cnil.fr" target="_blank" rel="noopener">{ext("cnil.fr")}</a>.</p>

    <h2 class="reveal">Mise à jour</h2>
    <p>Page mise à jour le 26 octobre 2026.</p>
  </div>
</div>
"""
    return page("Confidentialité et cookies · Teddy's Burger", "Ce site ne dépose aucun cookie et ne collecte aucune donnée personnelle. Le détail, et tes droits.",
                "confidentialite.html", "privacy", main)


# ---------------------------------------------------------------- 404
def build_404():
    main = f"""<section class="lost" aria-labelledby="titre">
  <div class="lost__text">
    <h1 id="titre" class="reveal">Burger introuvable</h1>
    <p class="reveal" style="--d:80ms">Cette page n'est pas sur la carte : elle n'existe pas, ou quelqu'un l'a mangée. Le reste du snack est toujours là.</p>
    <div class="lost__actions">
      <a class="btn" href="carte.html">Voir la carte</a>
      <a class="btn btn--cream" href="index.html" data-logo>Retour à l'accueil</a>
    </div>
  </div>
  <div class="lost__media reveal" style="--d:120ms">
    <div class="plinth"><img src="assets/logo-teddys.webp" alt="Teddy, l'ourson-burger, un peu perdu" width="348" height="658"></div>
  </div>
</section>
<section class="lost-picks" aria-labelledby="picks-titre">
  <h2 id="picks-titre" class="reveal">Ou laisse-toi tenter</h2>
  <ul class="lost-picks__list">
    <li class="reveal"><a href="carte.html#burgers"><img src="assets/menu/big-teddys.webp" alt="" width="192" height="192"><span>Big Teddy's</span><span class="tabular">12,90 €</span></a></li>
    <li class="reveal" style="--d:80ms"><a href="carte.html#burgers"><img src="assets/menu/big-massioux.webp" alt="" width="192" height="192"><span>Big Massioux</span><span class="tabular">8,00 €</span></a></li>
    <li class="reveal" style="--d:160ms"><a href="carte.html#burgers"><img src="assets/menu/big-campeche.webp" alt="" width="192" height="192"><span>Big Campêche</span><span class="tabular">9,90 €</span></a></li>
  </ul>
</section>
"""
    html_ = page("Page introuvable · Teddy's Burger", "Cette page n'existe pas. Retrouvez la carte de Teddy's Burger, à Anse-Bertrand.",
                 "404.html", "404", main)
    # La 404 peut être servie depuis n'importe quelle adresse : chemins absolus.
    for attr in ('href="', 'src="'):
        for target in ("css/", "js/", "assets/", "index.html", "carte.html", "mentions-legales.html", "confidentialite.html"):
            html_ = html_.replace(attr + target, attr + BASE + target)
    html_ = html_.replace('url("../assets/', 'url("' + BASE + 'assets/')
    if PREVIEW:
        return html_
    return html_.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)


def main():
    out = {
        "index.html": build_index(),
        "carte.html": build_carte(),
        "mentions-legales.html": build_legal(),
        "confidentialite.html": build_privacy(),
        "404.html": build_404(),
    }
    for name, content in out.items():
        if PREVIEW:
            content = content.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)
        (ROOT / name).write_text(content, encoding="utf-8")
        print("écrit", name, len(content), "octets")


if __name__ == "__main__":
    main()
