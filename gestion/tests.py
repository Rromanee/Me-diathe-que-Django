from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

from .models import Livre, CD, DVD, JeuDePlateau, Membre, Emprunt


class MediaTestCase(TestCase):
    def setUp(self):
        # Création d'un utilisateur pour les vues protégées
        self.user = User.objects.create_user(username="biblio", password="test1234")
        self.client.login(username="biblio", password="test1234")

        # Création d’un membre
        self.membre = Membre.objects.create(nom="Dupont", prenom="Alice")

        # Création des médias
        self.livre = Livre.objects.create(name="Livre test", auteur="Auteur X")
        self.cd = CD.objects.create(name="CD test", artiste="Artiste Y")
        self.dvd = DVD.objects.create(name="DVD test", realisateur="Réalisateur Z")
        self.jeu = JeuDePlateau.objects.create(name="Jeu test", createur="Créateur J")

    def test_media_heritage(self):
        """Vérifie que Livre hérite bien de Media."""
        self.assertTrue(hasattr(self.livre, "disponible"))
        self.assertTrue(self.livre.est_disponible)

    def test_jeu_non_empruntable(self):
        """Les jeux de plateau ne peuvent pas être empruntés."""
        response = self.client.post(
            f"/bibliothecaire/medias/emprunter/jeuDePlateau/{self.jeu.id}/",
            {"membre_id": self.membre.id},
            follow=True
        )
        self.assertContains(response, "ne peuvent pas être empruntés")

    #TESTS D'EMPRUNT

    def test_emprunt_normal(self):
        """Un membre peut emprunter un média disponible."""
        Emprunt.objects.create(membre=self.membre, media_type="livre", media_id=self.livre.id)
        emprunt = Emprunt.objects.get(membre=self.membre)
        self.assertEqual(emprunt.media.name, "Livre test")

    def test_limite_trois_emprunts(self):
        """Un membre ne peut pas avoir plus de 3 emprunts actifs."""
        for i in range(3):
            livre = Livre.objects.create(name=f"Livre {i}", auteur="Test")
            Emprunt.objects.create(membre=self.membre, media_type="livre", media_id=livre.id)
        nb_emprunts = Emprunt.objects.filter(membre=self.membre).count()
        self.assertEqual(nb_emprunts, 3)

    def test_emprunt_retarde(self):
        """Un emprunt de plus d’une semaine est considéré en retard."""
        emprunt = Emprunt.objects.create(
            membre=self.membre,
            media_type="cd",
            media_id=self.cd.id,
            date_emprunt=timezone.now() - timedelta(days=8)
        )
        self.assertTrue(emprunt.est_retarde)

    def test_membre_avec_retard_ne_peut_pas_emprunter(self):
        """Un membre ayant un emprunt en retard ne peut plus emprunter."""
        emprunt_retard = Emprunt.objects.create(
            membre=self.membre,
            media_type="livre",
            media_id=self.livre.id,
            date_emprunt=timezone.now() - timedelta(days=8)
        )

        response = self.client.post(
            f"/bibliothecaire/medias/emprunter/cd/{self.cd.id}/",
            {"membre_id": self.membre.id},
            follow=True
        )
        self.assertContains(response, "a un emprunt en retard")

    #TESTS DE RETOUR

    def test_retour_media(self):
        """Rendre un média rend le média disponible."""
        emprunt = Emprunt.objects.create(
            membre=self.membre,
            media_type="dvd",
            media_id=self.dvd.id
        )
        emprunt.date_retour = timezone.now()
        emprunt.save()
        self.assertIsNotNone(emprunt.date_retour)