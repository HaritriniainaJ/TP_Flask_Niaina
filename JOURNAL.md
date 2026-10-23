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
