from django import forms
from .models import Livre, CD, DVD, JeuDePlateau
from .models import Membre

class LivreForm(forms.ModelForm):
    class Meta:
        model = Livre
        fields = ['name', 'auteur']


class CDForm(forms.ModelForm):
    class Meta:
        model = CD
        fields = ['name', 'artiste']


class DVDForm(forms.ModelForm):
    class Meta:
        model = DVD
        fields = ['name', 'realisateur']

class JeuDePlateauForm(forms.ModelForm):
    class Meta:
        model = JeuDePlateau
        fields = ['name', 'createur']

class MembreForm(forms.ModelForm):
    class Meta:
        model = Membre
        fields = ["nom", "prenom"]