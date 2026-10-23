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
