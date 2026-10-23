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
