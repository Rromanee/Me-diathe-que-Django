# Médiathèque Django

## Instructions pour exécuter le programme

1. **Cloner le projet**
```bash
git clone https://github.com/Rromanee/Me-diathe-que-Django
cd mediatheque
```

2. Installer Python 3 et Django si nécessaire
```bash
pip install django
```

3. Créer la base de données et appliquer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

4.Lancer le serveur Django
```bash
python manage.py runserver
```

5. Accéder à l’application

Espace membre : http://127.0.0.1:8000/medias/
Espace bibliothécaire : http://127.0.0.1:8000/bibliothecaire/
 (login requis)
Espace Django administration : http://127.0.0.1:8000/admin/
 (login requis)
