from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    #APPLICATION MEMBRE
    path("medias/", views.liste_medias, name="liste_medias"),

    #CONNEXION / DECONNEXION
    path("bibliothecaire/login/", auth_views.LoginView.as_view(template_name='gestion/login.html'), name="login"),
    path("bibliothecaire/logout/", auth_views.LogoutView.as_view(next_page='login'), name="logout"),

    #APPLICATION BIBLIOTHÉCAIRE
    path("bibliothecaire/", views.accueil_bibliothecaire, name="accueil_bibliothecaire"),
    path("bibliothecaire/medias/", views.bibliothecaire_medias, name="bibliothecaire_medias"),

    #CRUD pour tous les médias
    path("bibliothecaire/medias/ajouter/<str:type_media>/", views.ajouter_media, name="ajouter_media"),
    path("bibliothecaire/medias/modifier/<str:type_media>/<int:media_id>/", views.modifier_media, name="modifier_media"),
    path("bibliothecaire/medias/supprimer/<str:type_media>/<int:media_id>/", views.supprimer_media, name="supprimer_media"),

    #Emprunts et retours
    path("bibliothecaire/medias/emprunter/<str:type_media>/<int:media_id>/", views.emprunter_media, name="emprunter_media"),
    path("bibliothecaire/medias/rendre/<str:type_media>/<int:media_id>/", views.rendre_media, name="rendre_media"),

    #CRUD Membres
    path("bibliothecaire/membres/", views.liste_membres, name="liste_membres"),
    path("bibliothecaire/membres/ajouter/", views.ajouter_membre, name="ajouter_membre"),
    path("bibliothecaire/membres/modifier/<int:id>/", views.modifier_membre, name="modifier_membre"),
    path("bibliothecaire/membres/supprimer/<int:id>/", views.supprimer_membre, name="supprimer_membre"),
]