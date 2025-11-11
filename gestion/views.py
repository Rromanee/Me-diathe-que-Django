from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Livre, CD, DVD, JeuDePlateau, Membre, Emprunt
from .forms import LivreForm, CDForm, DVDForm, JeuDePlateauForm, MembreForm

import logging

#CONFIGURATION DU LOGGING
logging.basicConfig(
    filename="mediatheque.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S"
)
logger = logging.getLogger()

#MAPPING DES MÉDIAS
MEDIA_MODELS = {
    "livre": Livre,
    "cd": CD,
    "dvd": DVD,
    "jeuDePlateau": JeuDePlateau
}

MEDIA_FORMS = {
    "livre": LivreForm,
    "cd": CDForm,
    "dvd": DVDForm,
    "jeuDePlateau": JeuDePlateauForm
}

#ESPACE MEMBRE
def liste_medias(request):
    return render(request, "gestion/liste_medias.html", {
        "livres": Livre.objects.all(),
        "cds": CD.objects.all(),
        "dvds": DVD.objects.all(),
        "jeux": JeuDePlateau.objects.all()
    })

#ESPACE BIBLIOTHÉCAIRE
@login_required(login_url='login')
def accueil_bibliothecaire(request):
    return render(request, "gestion/bibliothecaire_accueil.html")

@login_required(login_url='login')
def bibliothecaire_medias(request):
    context = {
        "livres": Livre.objects.all(),
        "cds": CD.objects.all(),
        "dvds": DVD.objects.all(),
        "jeux": JeuDePlateau.objects.all(),
        "membres": Membre.objects.all()
    }
    return render(request, "gestion/bibliothecaire_medias.html", context)

# MÉDIAS CRUD UNIFIÉ
@login_required(login_url='login')
def ajouter_media(request, type_media):
    ModelClass = MEDIA_MODELS.get(type_media)
    FormClass = MEDIA_FORMS.get(type_media)
    if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"{type_media.capitalize()} ajouté avec succès.")
            logger.info(f"Ajout d’un nouveau {type_media}.")
            return redirect("bibliothecaire_medias")
    else:
        form = FormClass()
    return render(request, "gestion/ajouter_media.html", {"form": form, "type_media": type_media})

@login_required(login_url='login')
def modifier_media(request, type_media, media_id):
    ModelClass = MEDIA_MODELS.get(type_media)
    FormClass = MEDIA_FORMS.get(type_media)
    media = get_object_or_404(ModelClass, id=media_id)
    if request.method == "POST":
        form = FormClass(request.POST, instance=media)
        if form.is_valid():
            form.save()
            messages.success(request, f"{type_media.capitalize()} modifié avec succès.")
            logger.info(f"{type_media.capitalize()} modifié : {media}")
            return redirect("bibliothecaire_medias")
    else:
        form = FormClass(instance=media)
    return render(request, "gestion/ajouter_media.html", {"form": form, "type_media": type_media})

@login_required(login_url='login')
def supprimer_media(request, type_media, media_id):
    ModelClass = MEDIA_MODELS.get(type_media)
    media = get_object_or_404(ModelClass, id=media_id)
    logger.info(f"Suppression du média : {media}")
    media.delete()
    messages.success(request, f"{type_media.capitalize()} supprimé avec succès.")
    return redirect("bibliothecaire_medias")

#EMPRUNTS
@login_required(login_url='login')
def emprunter_media(request, type_media, media_id):

    # Les jeux de plateau ne peuvent pas être empruntés
    if type_media == "jeuDePlateau":
        messages.error(request, "Les jeux de plateau ne peuvent pas être empruntés.")
        logger.warning("Tentative d'emprunt d'un jeu de plateau.")
        return redirect("bibliothecaire_medias")

    membre_id = request.POST.get("membre_id")
    if not membre_id or membre_id == "0":
        messages.error(request, "Veuillez sélectionner un membre.")
        logger.warning("Aucun membre sélectionné pour l’emprunt.")
        return redirect("bibliothecaire_medias")

    membre = get_object_or_404(Membre, id=membre_id)
    ModelClass = MEDIA_MODELS.get(type_media)
    media = get_object_or_404(ModelClass, id=media_id)

    if not media.est_disponible:
        messages.error(request, "Ce média est déjà emprunté.")
        logger.warning(f"Tentative d’emprunt refusée : {media} déjà emprunté.")
        return redirect("bibliothecaire_medias")

    #Max 3 emprunts
    if Emprunt.objects.filter(membre=membre, date_retour__isnull=True).count() >= 3:
        messages.error(request, f"{membre} a déjà 3 emprunts.")
        logger.warning(f"{membre} a tenté d’emprunter alors qu’il a déjà 3 emprunts.")
        return redirect("bibliothecaire_medias")

    #Pas d'emprunt avec retard
    retard = timezone.now() - timezone.timedelta(days=7)
    if Emprunt.objects.filter(membre=membre, date_retour__isnull=True, date_emprunt__lt=retard).exists():
        messages.error(request, f"{membre} a un emprunt en retard.")
        logger.warning(f"{membre} a tenté d’emprunter alors qu’il a un emprunt en retard.")
        return redirect("bibliothecaire_medias")

    #Enregistrer emprunt
    media.disponible = False
    media.save()
    Emprunt.objects.create(membre=membre, media_type=type_media, media_id=media_id)
    messages.success(request, f"{media} emprunté par {membre}.")
    logger.info(f"{media} emprunté par {membre}.")
    return redirect("bibliothecaire_medias")

@login_required(login_url='login')
def rendre_media(request, type_media, media_id):
    ModelClass = MEDIA_MODELS.get(type_media)
    media = get_object_or_404(ModelClass, id=media_id)
    emprunt = Emprunt.objects.filter(media_type=type_media, media_id=media_id, date_retour__isnull=True).first()
    if emprunt:
        emprunt.date_retour = timezone.now()
        emprunt.save()
        media.disponible = True
        media.save()
        messages.success(request, f"{media} retourné par {emprunt.membre}.")
        logger.info(f"{media} retourné par {emprunt.membre}.")
    else:
        logger.error(f"Tentative de retour d’un média non emprunté : {media}.")
    return redirect("bibliothecaire_medias")

# MEMBRES CRUD
@login_required(login_url='login')
def liste_membres(request):
    return render(request, "gestion/liste_membres.html", {"membres": Membre.objects.all()})

@login_required(login_url='login')
def ajouter_membre(request):
    if request.method == "POST":
        form = MembreForm(request.POST)
        if form.is_valid():
            membre = form.save()
            messages.success(request, "Membre ajouté avec succès.")
            logger.info(f"Nouveau membre ajouté : {membre}")
            return redirect("liste_membres")
    else:
        form = MembreForm()
    return render(request, "gestion/ajouter_membre.html", {"form": form})

@login_required(login_url='login')
def modifier_membre(request, id):
    membre = get_object_or_404(Membre, id=id)
    if request.method == "POST":
        form = MembreForm(request.POST, instance=membre)
        if form.is_valid():
            form.save()
            messages.success(request, "Membre modifié avec succès.")
            logger.info(f"Membre modifié : {membre}")
            return redirect("liste_membres")
    else:
        form = MembreForm(instance=membre)
    return render(request, "gestion/ajouter_membre.html", {"form": form})

@login_required(login_url='login')
def supprimer_membre(request, id):
    membre = get_object_or_404(Membre, id=id)
    logger.info(f"Membre supprimé : {membre}")
    membre.delete()
    messages.success(request, "Membre supprimé avec succès.")
    return redirect("liste_membres")