from django.db import models
from django.utils import timezone
from datetime import timedelta

# Classe pour les médias empruntables
class Media(models.Model):
    name = models.CharField(max_length=200)
    disponible = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @property
    def emprunt(self):
        """Retourne l'emprunt actif si le média est emprunté, sinon None."""
        try:
            return Emprunt.objects.get(
                media_type=self.__class__.__name__.lower(),
                media_id=self.id,
                date_retour__isnull=True
            )
        except Emprunt.DoesNotExist:
            return None

    @property
    def est_disponible(self):
        """Retourne True si le média est disponible."""
        return self.disponible

# Médias empruntables
class Livre(Media):
    auteur = models.CharField(max_length=100)

class CD(Media):
    artiste = models.CharField(max_length=100)

class DVD(Media):
    realisateur = models.CharField(max_length=100)

# Jeux de plateau NON empruntables
class JeuDePlateau(models.Model):
    name = models.CharField(max_length=200)
    createur = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Membre
class Membre(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

# Emprunt
class Emprunt(models.Model):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    media_type = models.CharField(max_length=50)
    media_id = models.PositiveIntegerField()
    date_emprunt = models.DateTimeField(default=timezone.now)
    date_retour = models.DateTimeField(null=True, blank=True)

    @property
    def media(self):
        """Retourne l'objet Media réel."""
        mapping = {"livre": Livre, "cd": CD, "dvd": DVD}
        ModelClass = mapping[self.media_type]
        return ModelClass.objects.get(id=self.media_id)

    @property
    def est_retarde(self):
        """Retour après 1 semaine."""
        return timezone.now() > self.date_emprunt + timedelta(days=7) and not self.date_retour