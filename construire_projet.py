from pathlib import Path

root = Path(__file__).resolve().parent

files = {
    "app.py": r'''
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort

app = Flask(__name__)
app.secret_key = "taskflow-cle-de-developpement"

# Donnees de depart pour les exercices Flask.
taches = [
    {"id": 1, "titre": "Comprendre les routes Flask", "description": "Decouvrir les routes et les vues.", "priorite": "Haute", "terminee": True},
    {"id": 2, "titre": "Apprendre Jinja2", "description": "Afficher les donnees dans un template.", "priorite": "Normale", "terminee": False},
    {"id": 3, "titre": "Creer un formulaire", "description": "Envoyer et valider les donnees.", "priorite": "Basse", "terminee": False},
]

PRIORITES = ["Basse", "Normale", "Haute"]


def trouver_tache(identifiant):
    for tache in taches:
        if tache["id"] == identifiant:
            return tache
    abort(404)


@app.route("/")
def index():
    filtre = request.args.get("filtre")
    if filtre in ("toutes", "actives", "terminees"):
        session["filtre"] = filtre
    else:
        filtre = session.get("filtre", "toutes")

    visibles = taches
    if filtre == "actives":
        visibles = [t for t in taches if not t["terminee"]]
    elif filtre == "terminees":
        visibles = [t for t in taches if t["terminee"]]

    recherche = request.args.get("q", "").strip()
    if recherche:
        visibles = [t for t in visibles if recherche.casefold() in t["titre"].casefold()]

    return render_template(
        "index.html",
        taches=visibles,
        filtre=filtre,
        recherche=recherche,
        total=len(taches),
        restantes=sum(not t["terminee"] for t in taches),
        terminees=sum(t["terminee"] for t in taches),
    )


@app.route("/taches/<int:identifiant>")
def detail(identifiant):
    tache = trouver_tache(identifiant)
    return render_template("detail.html", tache=tache)


@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        description = request.form.get("description", "").strip()
        priorite = request.form.get("priorite", "Normale")

        erreurs = []
        if not titre:
            erreurs.append("Le titre est obligatoire.")
        if len(titre) > 100:
            erreurs.append("Le titre ne doit pas depasser 100 caracteres.")
        if any(t["titre"].casefold() == titre.casefold() for t in taches):
            erreurs.append("Une tache avec ce titre existe deja.")
        if priorite not in PRIORITES:
            erreurs.append("La priorite selectionnee est invalide.")

        if erreurs:
            for erreur in erreurs:
                flash(erreur, "erreur")
            return render_template("ajouter.html", titre=titre,
                                   description=description, priorite=priorite)

        nouvel_id = max((t["id"] for t in taches), default=0) + 1
        taches.append({
            "id": nouvel_id,
            "titre": titre,
            "description": description,
            "priorite": priorite,
            "terminee": False,
        })
        flash("La tache a ete ajoutee avec succes.", "succes")
        return redirect(url_for("index"))

    return render_template("ajouter.html", titre="", description="", priorite="Normale")


@app.post("/taches/<int:identifiant>/basculer")
def basculer(identifiant):
    tache = trouver_tache(identifiant)
    tache["terminee"] = not tache["terminee"]
    message = "Tache terminee." if tache["terminee"] else "Tache reactivee."
    flash(message, "succes")
    return redirect(request.referrer or url_for("index"))


@app.post("/taches/<int:identifiant>/supprimer")
def supprimer(identifiant):
    tache = trouver_tache(identifiant)
    taches.remove(tache)
    flash("La tache a ete supprimee.", "succes")
    return redirect(url_for("index"))


@app.errorhandler(404)
def page_introuvable(erreur):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
''',

    "templates/base.html": r'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}TaskFlow{% endblock %} | Haritriniaina</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
<div class="app-shell">
    <aside class="sidebar">
        <a class="brand" href="{{ url_for('index') }}">
            <span class="brand-mark">T</span>
            <span>TaskFlow<small>ESPACE PERSONNEL</small></span>
        </a>
        <p class="nav-caption">MENU PRINCIPAL</p>
        <a class="nav-link {% if request.endpoint == 'index' %}active{% endif %}" href="{{ url_for('index') }}">
            <span>▦</span> Tableau de bord
        </a>
        <a class="nav-link {% if request.endpoint == 'ajouter' %}active{% endif %}" href="{{ url_for('ajouter') }}">
            <span>＋</span> Nouvelle tâche
        </a>
        <div class="sidebar-bottom">
            <div class="profile-avatar">H</div>
            <div class="profile-text"><strong>Haritriniaina</strong><small>Étudiant</small></div>
        </div>
    </aside>

    <main class="main-content">
        <header class="topbar">
            <div><span class="eyebrow">ORGANISATION PERSONNELLE</span><h1>{% block heading %}Tableau de bord{% endblock %}</h1></div>
            <a class="button button-primary" href="{{ url_for('ajouter') }}">＋ Nouvelle tâche</a>
        </header>

        <section class="content">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <div class="flash-list">
                    {% for categorie, message in messages %}
                        <div class="flash {{ categorie }}">{{ message }}</div>
                    {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}
            {% block content %}{% endblock %}
        </section>
        <footer>TaskFlow <span>·</span> TP Python &amp; Flask</footer>
    </main>
</div>
</body>
</html>
''',

    "templates/index.html": r'''
{% extends "base.html" %}
{% block title %}Mes tâches{% endblock %}
{% block heading %}Mes tâches{% endblock %}
{% block content %}
<div class="welcome-row">
    <div><h2>Bonjour, Haritriniaina.</h2><p>Voici un aperçu de ton organisation aujourd'hui.</p></div>
    <span class="date-chip">ESPACE DE TRAVAIL</span>
</div>

<div class="stats-grid">
    <article class="stat-card"><span class="stat-icon violet">▦</span><span class="stat-label">Toutes les tâches</span><strong>{{ total }}</strong><small>Enregistrées dans la liste</small></article>
    <article class="stat-card"><span class="stat-icon orange">◷</span><span class="stat-label">À réaliser</span><strong>{{ restantes }}</strong><small>Encore en cours</small></article>
    <article class="stat-card"><span class="stat-icon green">✓</span><span class="stat-label">Terminées</span><strong>{{ terminees }}</strong><small>Déjà accomplies</small></article>
</div>

<div class="section-heading"><div><h2>Liste des tâches</h2><p>Consulte et organise tes activités.</p></div></div>

<form class="search-form" action="{{ url_for('index') }}" method="get">
    <label class="search-box"><span>⌕</span><input type="search" name="q" value="{{ recherche }}" placeholder="Rechercher une tâche..."></label>
    <input type="hidden" name="filtre" value="{{ filtre }}">
    <button class="button button-light" type="submit">Rechercher</button>
</form>

<nav class="filter-tabs" aria-label="Filtres">
    <a class="{% if filtre == 'toutes' %}selected{% endif %}" href="{{ url_for('index', filtre='toutes', q=recherche) }}">Toutes</a>
    <a class="{% if filtre == 'actives' %}selected{% endif %}" href="{{ url_for('index', filtre='actives', q=recherche) }}">À faire</a>
    <a class="{% if filtre == 'terminees' %}selected{% endif %}" href="{{ url_for('index', filtre='terminees', q=recherche) }}">Terminées</a>
</nav>

<div class="task-list">
{% for tache in taches %}
    <article class="task-card">
        <form action="{{ url_for('basculer', identifiant=tache.id) }}" method="post">
            <button class="check-button {% if tache.terminee %}checked{% endif %}" type="submit" aria-label="Changer le statut">{% if tache.terminee %}✓{% endif %}</button>
        </form>
        <div class="task-main">
            <a class="task-title {% if tache.terminee %}done{% endif %}" href="{{ url_for('detail', identifiant=tache.id) }}">{{ tache.titre }}</a>
            <p>{{ tache.description or "Aucune description fournie." }}</p>
            <div class="task-meta"><span class="priority priority-{{ tache.priorite|lower }}">{{ tache.priorite }}</span><span>ID #{{ tache.id }}</span></div>
        </div>
        <div class="task-actions">
            <a class="text-action" href="{{ url_for('detail', identifiant=tache.id) }}">Détails ↗</a>
            <form action="{{ url_for('supprimer', identifiant=tache.id) }}" method="post" onsubmit="return confirm('Supprimer cette tâche ?')">
                <button class="delete-action" type="submit" aria-label="Supprimer">×</button>
            </form>
        </div>
    </article>
{% else %}
    <div class="empty-state"><div class="empty-icon">⌕</div><h3>Aucune tâche trouvée</h3><p>Modifie ton filtre ou ajoute une nouvelle tâche.</p><a class="button button-primary" href="{{ url_for('ajouter') }}">Créer une tâche</a></div>
{% endfor %}
</div>
{% endblock %}
''',

    "templates/ajouter.html": r'''
{% extends "base.html" %}
{% block title %}Nouvelle tâche{% endblock %}
{% block heading %}Nouvelle tâche{% endblock %}
{% block content %}
<div class="form-intro"><a class="back-link" href="{{ url_for('index') }}">← Retour aux tâches</a><h2>Ajouter une activité</h2><p>Décris ce que tu souhaites accomplir et choisis son niveau de priorité.</p></div>
<form class="task-form" method="post" action="{{ url_for('ajouter') }}">
    <div class="form-field">
        <label for="titre">Titre de la tâche <span>*</span></label>
        <input id="titre" name="titre" type="text" maxlength="100" required value="{{ titre }}" placeholder="Ex. Terminer le TP Flask">
        <small>100 caractères maximum.</small>
    </div>
    <div class="form-field">
        <label for="description">Description</label>
        <textarea id="description" name="description" rows="5" placeholder="Ajoute quelques détails...">{{ description }}</textarea>
    </div>
    <fieldset class="form-field priority-field">
        <legend>Priorité</legend>
        <div class="priority-options">
            {% for choix in ["Basse", "Normale", "Haute"] %}
            <label class="priority-choice">
                <input type="radio" name="priorite" value="{{ choix }}" {% if priorite == choix %}checked{% endif %}>
                <span>{{ choix }}</span>
            </label>
            {% endfor %}
        </div>
    </fieldset>
    <div class="form-footer"><a class="button button-light" href="{{ url_for('index') }}">Annuler</a><button class="button button-primary" type="submit">Créer la tâche →</button></div>
</form>
{% endblock %}
''',

    "templates/detail.html": r'''
{% extends "base.html" %}
{% block title %}Détail de la tâche{% endblock %}
{% block heading %}Détail de la tâche{% endblock %}
{% block content %}
<a class="back-link" href="{{ url_for('index') }}">← Retour à la liste</a>
<article class="detail-card">
    <div class="detail-top"><span class="priority priority-{{ tache.priorite|lower }}">{{ tache.priorite }}</span><span class="detail-id">TÂCHE #{{ tache.id }}</span></div>
    <h2 class="{% if tache.terminee %}done{% endif %}">{{ tache.titre }}</h2>
    <p>{{ tache.description or "Aucune description fournie." }}</p>
    <div class="detail-status"><span>Statut</span><strong>{% if tache.terminee %}Terminée{% else %}À réaliser{% endif %}</strong></div>
    <form action="{{ url_for('basculer', identifiant=tache.id) }}" method="post"><button class="button button-primary" type="submit">{% if tache.terminee %}Réactiver la tâche{% else %}Marquer comme terminée{% endif %}</button></form>
</article>
{% endblock %}
''',

    "templates/404.html": r'''
{% extends "base.html" %}
{% block title %}Page introuvable{% endblock %}
{% block heading %}Page introuvable{% endblock %}
{% block content %}
<div class="empty-state error-state"><div class="error-code">404</div><h2>Cette tâche n'existe pas</h2><p>L'identifiant demandé ne correspond à aucune tâche disponible.</p><a class="button button-primary" href="{{ url_for('index') }}">Retour au tableau de bord</a></div>
{% endblock %}
''',

    "static/style.css": r'''
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--ink:#20253a;--muted:#858ba0;--line:#e9eaf1;--paper:#f6f7fb;--purple:#6558d9;--purple-dark:#5144c5;--sidebar:#20243a;--green:#218b68}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:'DM Sans',sans-serif;font-size:14px}
a{color:inherit;text-decoration:none}
button,input,textarea{font:inherit}
button,a{ -webkit-tap-highlight-color:transparent}
.app-shell{min-height:100vh}
.sidebar{position:fixed;inset:0 auto 0 0;width:245px;background:var(--sidebar);padding:30px 19px;color:#fff;display:flex;flex-direction:column;z-index:2}
.brand{display:flex;align-items:center;gap:12px;font-family:Manrope,sans-serif;font-weight:800;font-size:20px;padding:0 7px 43px}
.brand-mark{display:grid;place-items:center;width:39px;height:39px;border-radius:12px;background:var(--purple);font-size:21px}
.brand small{display:block;font:600 9px 'DM Sans',sans-serif;letter-spacing:1.4px;color:#a7abc0;margin-top:4px}
.nav-caption{font-size:10px;letter-spacing:1.5px;font-weight:700;color:#858ba7;margin:0 10px 12px}
.nav-link{display:flex;align-items:center;gap:13px;padding:13px 14px;border-radius:9px;color:#b9bdd0;margin-bottom:6px;font-weight:500;transition:.2s}
.nav-link span{font-size:20px;width:20px;text-align:center}
.nav-link:hover,.nav-link.active{background:#343951;color:#fff}
.nav-link.active{box-shadow:inset 3px 0 #9e93ff}
.sidebar-bottom{margin-top:auto;border-top:1px solid #3a3e52;padding:22px 5px 0;display:flex;align-items:center;gap:11px}
.profile-avatar{width:36px;height:36px;display:grid;place-items:center;border-radius:50%;background:#d9d5ff;color:#5144c5;font-weight:700}
.profile-text strong,.profile-text small{display:block}.profile-text small{margin-top:4px;color:#a7abc0;font-size:12px}
.main-content{margin-left:245px;min-height:100vh;display:flex;flex-direction:column}
.topbar{min-height:112px;background:#fff;border-bottom:1px solid var(--line);padding:24px 5%;display:flex;align-items:center;justify-content:space-between;gap:18px}
.eyebrow{font-size:9px;letter-spacing:1.7px;color:var(--muted);font-weight:700}
h1,h2,h3,p{margin-top:0}
h1{font:800 25px Manrope,sans-serif;margin:7px 0 0;letter-spacing:-.7px}
h2{font:700 18px Manrope,sans-serif;letter-spacing:-.3px}
p{color:var(--muted);line-height:1.65}
.content{width:100%;max-width:1100px;margin:0 auto;padding:34px 5% 55px;flex:1}
.button{border:0;border-radius:8px;padding:11px 16px;display:inline-flex;align-items:center;justify-content:center;gap:8px;font-weight:600;cursor:pointer;transition:background .2s,transform .2s;font-size:13px}
.button:hover{transform:translateY(-1px)}
.button-primary{background:var(--purple);color:#fff}.button-primary:hover{background:var(--purple-dark)}
.button-light{background:#fff;border:1px solid var(--line);color:#555c72}
.welcome-row{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:25px}
.welcome-row h2{margin-bottom:5px}.welcome-row p{margin-bottom:0}
.date-chip{border:1px solid #e4e2fa;background:#f0efff;color:var(--purple);border-radius:7px;padding:9px 11px;font-size:9px;letter-spacing:1px;font-weight:700}
.stats-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-bottom:36px}
.stat-card{position:relative;background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px;min-height:150px;box-shadow:0 4px 15px #292e4705}
.stat-icon{display:grid;place-items:center;width:35px;height:35px;border-radius:10px;font-size:19px;margin-bottom:16px}
.violet{background:#eeecff;color:var(--purple)}.orange{background:#fff0e3;color:#c77b32}.green{background:#e4f6ef;color:var(--green)}
.stat-label{display:block;color:#73798e;font-size:12px}.stat-card strong{display:block;font:800 27px Manrope,sans-serif;margin:7px 0}.stat-card small{font-size:11px;color:#a0a4b3}
.section-heading{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}.section-heading h2{margin-bottom:5px}.section-heading p{margin:0;font-size:12px}
.search-form{display:flex;gap:10px;margin-bottom:15px}
.search-box{flex:1;display:flex;align-items:center;gap:9px;border:1px solid var(--line);border-radius:8px;background:#fff;padding:0 12px;color:#9ba0b1}
.search-box span{font-size:23px}.search-box input{width:100%;border:0;outline:0;background:transparent;padding:12px 0;color:var(--ink)}
.filter-tabs{display:flex;gap:22px;border-bottom:1px solid var(--line);margin-bottom:15px}
.filter-tabs a{padding:12px 2px;color:#888da0;font-size:12px;border-bottom:2px solid transparent}
.filter-tabs a.selected{color:var(--purple);border-color:var(--purple);font-weight:700}
.task-list{display:grid;gap:11px}
.task-card{display:flex;align-items:flex-start;gap:14px;background:#fff;border:1px solid var(--line);border-radius:11px;padding:18px 17px;transition:box-shadow .2s,border .2s}
.task-card:hover{border-color:#d8d4fa;box-shadow:0 6px 20px #292e4708}
.check-button{width:22px;height:22px;flex:0 0 22px;border-radius:7px;border:1.5px solid #d7d9e5;background:#fff;color:#fff;cursor:pointer;font-weight:700}
.check-button.checked{background:var(--green);border-color:var(--green)}
.task-main{flex:1;min-width:0}
.task-title{font-weight:700;font-size:14px;display:inline-block;margin:1px 0 5px}
.task-title:hover{color:var(--purple)}.task-title.done{text-decoration:line-through;color:#9da2b2}
.task-main p{font-size:12px;margin:0 0 11px;overflow-wrap:anywhere}
.task-meta{display:flex;align-items:center;gap:12px;font-size:10px;color:#9a9fb0}
.priority{display:inline-block;padding:5px 8px;border-radius:5px;font-size:10px;font-weight:700}
.priority-haute{background:#ffebeb;color:#c94b58}.priority-normale{background:#fff1dd;color:#b57927}.priority-basse{background:#e4f6ee;color:#278461}
.task-actions{display:flex;align-items:center;gap:11px;margin-left:8px}
.task-actions form{margin:0}.text-action{font-size:11px;color:var(--purple);font-weight:600;white-space:nowrap}
.delete-action{width:27px;height:27px;border:0;border-radius:7px;background:#fff0f0;color:#c35b65;font-size:20px;cursor:pointer}
.empty-state{text-align:center;padding:55px 20px;background:#fff;border:1px dashed #dfe1eb;border-radius:12px}
.empty-icon{margin:0 auto 12px;width:44px;height:44px;display:grid;place-items:center;background:#f0efff;color:var(--purple);border-radius:13px;font-size:24px}
.empty-state h3{font:700 16px Manrope,sans-serif;margin-bottom:7px}.empty-state p{font-size:12px;margin-bottom:20px}
.flash-list{display:grid;gap:8px;margin-bottom:18px}.flash{border-radius:8px;padding:12px 15px;font-size:13px}.flash.succes{background:#e6f6ee;color:#1d7657;border:1px solid #c8ebda}.flash.erreur{background:#fff0f0;color:#a83b48;border:1px solid #f5d0d4}
.form-intro{margin:20px 0 24px}.back-link{display:inline-block;color:var(--purple);font-size:12px;font-weight:600;margin-bottom:18px}.form-intro h2{margin-bottom:7px}.form-intro p{font-size:13px;margin-bottom:0}
.task-form{max-width:720px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:28px}
.form-field{border:0;padding:0;margin:0 0 23px}.form-field>label,.form-field legend{display:block;font-weight:700;font-size:12px;margin-bottom:9px}.form-field label span{color:#d24d5b}
.form-field input[type=text],.form-field textarea{width:100%;border:1px solid #dfe1eb;border-radius:8px;padding:12px 13px;outline:none;color:var(--ink);background:#fff}
.form-field input:focus,.form-field textarea:focus{border-color:var(--purple);box-shadow:0 0 0 3px #6558d918}
.form-field textarea{resize:vertical;min-height:115px}.form-field small{display:block;color:#999eb0;font-size:10px;margin-top:7px}
.priority-options{display:flex;gap:10px}.priority-choice{flex:1;cursor:pointer}.priority-choice input{position:absolute;opacity:0}.priority-choice span{display:block;text-align:center;padding:12px 8px;border:1px solid var(--line);border-radius:8px;color:#73798d}
.priority-choice input:checked+span{border-color:var(--purple);background:#f2f0ff;color:var(--purple);font-weight:700}
.form-footer{display:flex;justify-content:flex-end;gap:10px;border-top:1px solid var(--line);padding-top:20px}
.detail-card{max-width:720px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:28px;margin-top:15px}
.detail-top{display:flex;justify-content:space-between;align-items:center}.detail-id{font-size:10px;letter-spacing:1px;color:#999eb0;font-weight:700}
.detail-card h2{font-size:24px;margin:24px 0 10px;overflow-wrap:anywhere}.detail-card p{margin-bottom:28px}
.detail-status{border-top:1px solid var(--line);padding:18px 0;margin-bottom:8px;display:flex;justify-content:space-between;font-size:12px;color:var(--muted)}.detail-status strong{color:var(--ink)}
.error-state{margin-top:20px}.error-code{font:800 64px Manrope,sans-serif;color:var(--purple);margin-bottom:10px}
footer{border-top:1px solid var(--line);padding:18px 5%;color:#9b9fb0;font-size:11px}footer span{padding:0 6px;color:var(--purple)}
@media(max-width:850px){.sidebar{width:200px}.main-content{margin-left:200px}.stats-grid{gap:9px}.stat-card{padding:14px}.content{padding-top:25px}}
@media(max-width:650px){.sidebar{position:static;width:auto;padding:15px;flex-direction:row;align-items:center;flex-wrap:wrap;gap:6px}.brand{padding:0;margin-right:auto}.brand-mark{width:34px;height:34px}.nav-caption,.sidebar-bottom{display:none}.nav-link{padding:9px 10px;margin:0;font-size:12px}.nav-link span{font-size:16px}.main-content{margin-left:0}.topbar{min-height:88px;padding:18px 5%}.topbar h1{font-size:21px}.topbar>.button{font-size:11px;padding:10px}.content{padding:24px 5% 35px}.welcome-row{align-items:flex-start}.date-chip{display:none}.stats-grid{grid-template-columns:1fr;gap:10px}.stat-card{min-height:0;padding:14px 15px;display:grid;grid-template-columns:38px 1fr auto;align-items:center;column-gap:12px}.stat-icon{grid-row:span 2;margin:0}.stat-label{align-self:end}.stat-card strong{grid-column:3;grid-row:1/3;margin:0}.stat-card small{display:none}.task-card{gap:10px;padding:14px 11px}.task-actions{flex-direction:column;gap:7px}.task-form,.detail-card{padding:19px}.priority-options{gap:5px}.priority-choice span{font-size:11px}.search-form{gap:6px}.search-form .button{padding:10px}.filter-tabs{gap:17px}}
''',

    "README.md": r'''
# TaskFlow — Gestionnaire de tâches

Projet pédagogique réalisé avec Python, Flask, Jinja2, HTML et CSS.

## Fonctionnalités
- Affichage et détail des tâches
- Ajout avec validation côté serveur
- Détection des titres en double
- Priorités et statut terminé / à faire
- Recherche et filtres
- Messages flash et filtre mémorisé en session
- Page 404 personnalisée

## Lancer le projet
1. Activer l'environnement : `source .venv/bin/activate`
2. Installer Flask : `python -m pip install Flask`
3. Lancer l'application : `python app.py`
4. Ouvrir `http://127.0.0.1:5000`

Les tâches sont conservées en mémoire pendant l'exécution : elles sont réinitialisées au redémarrage. Ce choix reste adapté aux exercices sur les routes, les formulaires, Jinja2, flash et session.
''',

    "JOURNAL.md": r'''
# Journal de bord — TaskFlow

**Étudiant :** Haritriniaina  
**Projet :** Gestionnaire de tâches avec Flask  
**Branche Git :** `main`

Ce journal présente le travail réalisé, les observations et les notions comprises. Il doit être adapté si les essais réellement effectués diffèrent de ceux décrits ici.

## Mission 1 — Découvrir Flask

**Objectif :** lancer une application web et comprendre le lien entre une route et une fonction Python.

**Réalisation :** l'application est définie dans `app.py` avec `Flask(__name__)`. La route `/` est associée à la fonction `index`. La commande `python app.py` lance le serveur de développement.

**Observation à vérifier :** ouvrir `http://127.0.0.1:5000` dans le navigateur. Flask affiche la page d'accueil si le serveur démarre correctement.

**Ce que j'ai compris :** une route associe une URL à une fonction Python qui prépare la réponse envoyée au navigateur.

## Mission 2 — Jouer avec les URL dynamiques

**Objectif :** utiliser un identifiant dans une URL et répondre correctement lorsqu'une tâche n'existe pas.

**Réalisation :** la route `/taches/<int:identifiant>` récupère un entier. La fonction `trouver_tache` recherche la tâche correspondante et appelle `abort(404)` si elle est absente.

**Tests à effectuer :**
- ouvrir `/taches/2` et vérifier le détail de la deuxième tâche ;
- ouvrir `/taches/999` et vérifier le code HTTP 404.

**Ce que j'ai compris :** le convertisseur `int` limite la route aux identifiants numériques. Une erreur 404 indique que la ressource demandée est introuvable.

## Mission 3 — Afficher les tâches avec Jinja2

**Objectif :** transmettre des données Python à un template HTML.

**Réalisation :** la fonction `index` transmet la liste des tâches à `templates/index.html`. Le template utilise une boucle `{% for %}` pour afficher les tâches et des conditions `{% if %}` pour distinguer les statuts.

**Tests à effectuer :** vérifier les titres, les priorités, les tâches terminées et l'état vide lorsqu'aucune tâche ne correspond au filtre.

**Ce que j'ai compris :** Jinja2 sépare les données et la présentation. La boucle évite de recopier le même HTML pour chaque tâche.

## Mission 4 — Organiser les templates et le CSS

**Objectif :** partager la structure des pages et utiliser les fonctions de génération d'URL de Flask.

**Réalisation :** `base.html` contient la structure commune, la navigation, les messages et le pied de page. Les autres templates utilisent `{% extends %}` et définissent leurs blocs. Les liens et formulaires utilisent `url_for`. Le style est dans `static/style.css`.

**Observation :** le design utilise une barre latérale sombre, un fond clair, des cartes et une mise en page responsive.

**Ce que j'ai compris :** l'héritage évite de dupliquer le code commun et `url_for` génère les liens à partir du nom des fonctions de route.

## Mission 5 — Ajouter et valider une tâche

**Objectif :** recevoir des données avec un formulaire GET/POST et contrôler les entrées côté serveur.

**Réalisation :** la route `/ajouter` affiche le formulaire en GET et traite les données en POST. Le serveur vérifie le titre obligatoire, sa longueur, les doublons et la priorité. En cas de succès, il ajoute la tâche puis redirige vers l'accueil.

**Tests à effectuer :**
- soumettre un titre vide ;
- ajouter une tâche valide ;
- réutiliser le même titre en changeant sa casse ;
- choisir chaque priorité.

**Ce que j'ai compris :** la validation HTML aide l'utilisateur, mais la validation côté serveur reste indispensable. Le modèle POST/Redirect/GET évite de renvoyer le formulaire lors d'un simple rafraîchissement après succès.

## Mission 6 — Messages flash, session et filtres

**Objectif :** informer l'utilisateur et conserver une préférence entre plusieurs requêtes.

**Réalisation :** `flash` affiche des messages temporaires après l'ajout, la suppression ou le changement de statut. La session mémorise le filtre choisi. La recherche utilise le paramètre `q` dans l'URL.

**Tests à effectuer :**
- choisir « À faire » puis revenir sur la page d'accueil ;
- ajouter une tâche et vérifier le message de confirmation ;
- rechercher un titre existant et un titre absent ;
- changer le statut d'une tâche.

**Ce que j'ai compris :** les messages flash sont temporaires. La session Flask permet de mémoriser des informations propres à un visiteur entre plusieurs requêtes.

## Bilan

Ce projet met en pratique les routes Flask, les paramètres d'URL, les templates Jinja2, les formulaires, la validation, les redirections, les messages flash et les sessions. Les tâches sont stockées dans une liste Python en mémoire ; elles ne sont donc pas conservées après le redémarrage du serveur.

**Améliorations possibles :** ajouter une base de données SQLite, des tests automatisés et une authentification si le périmètre du cours le permet.
'''
}

for relative_path, content in files.items():
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip(), encoding="utf-8")
    print("Créé :", relative_path)

print("\nTous les fichiers ont été générés.")
