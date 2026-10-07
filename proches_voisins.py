import pandas as pd
import sqlite3
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

DATABASE = "football_data.db"


def creer_pd():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT * FROM joueurs_300_minutes", conn)
    conn.close()
    return df


def changer_90_min(df):
    # on applique la formule stat/90min = stat/minutes_jouees * 90
    debut = df.columns.get_loc("tirs")
    df.iloc[:, debut:] = df.iloc[:, debut:].div(df["minutes_jouees"], axis=0) * 90
    return df


def standardiser(df):
    # on standardise toutes les variables à partir de apparitions
    # je vais changer ça psk ça a aucun sens
    debut = df.columns.get_loc("apparitions")
    scaler = StandardScaler()
    df.iloc[:, debut:] = scaler.fit_transform(df.iloc[:, debut:])
    X = df.iloc[:, debut:]
    return df, X


def proches_voisins_distance_euclidienne(df, X, nom_joueur):
    # création du modèle avec distance euclidienne
    modele = NearestNeighbors(n_neighbors=6, metric="euclidean")
    modele.fit(X)

    # recherche du joueur
    joueur = df[df["nom"] == nom_joueur]

    if joueur.empty:
        print("Joueur non trouvé.")
        return

    # récupération de la position du joueur
    index_joueur = joueur.index[0]

    # recherche des 6 voisins
    distances, indices = modele.kneighbors(X.loc[[index_joueur]])

    # on enlève le joueur lui-même
    indices = indices[0][1:]
    distances = distances[0][1:]

    # récupération des 5 joueurs les plus proches
    joueurs_proches = df.iloc[indices]

    return joueurs_proches


def proches_voisins_distance_cosinus(df, X, nom_joueur):
    # création du modèle avec distance cosinus
    modele = NearestNeighbors(n_neighbors=6, metric="cosine")
    modele.fit(X)

    # recherche du joueur
    joueur = df[df["nom"] == nom_joueur]

    if joueur.empty:
        print("Joueur non trouvé.")
        return

    # récupération de la position du joueur
    index_joueur = joueur.index[0]

    # recherche des 6 voisins
    distances, indices = modele.kneighbors(X.loc[[index_joueur]])

    # on enlève le joueur lui-même
    indices = indices[0][1:]
    distances = distances[0][1:]

    # récupération des 5 joueurs les plus proches
    joueurs_proches = df.iloc[indices]

    return joueurs_proches


def proches_voisins_distance_mahalanobis(df, X, nom_joueur):
    # calcul de la matrice de covariance
    covariance = np.cov(X, rowvar=False)

    # calcul de l'inverse de la matrice de covariance
    inverse_covariance = np.linalg.pinv(covariance)

    # création du modèle avec distance de Mahalanobis
    modele = NearestNeighbors(
        n_neighbors=6,
        metric="mahalanobis",
        metric_params={"VI": inverse_covariance}
    )
    modele.fit(X)

    # recherche du joueur
    joueur = df[df["nom"] == nom_joueur]

    if joueur.empty:
        print("Joueur non trouvé.")
        return

    # récupération de la position du joueur
    index_joueur = joueur.index[0]

    # recherche des 6 voisins
    distances, indices = modele.kneighbors(X.loc[[index_joueur]])

    # on enlève le joueur lui-même
    indices = indices[0][1:]
    distances = distances[0][1:]

    # récupération des 5 joueurs les plus proches
    joueurs_proches = df.iloc[indices]

    return joueurs_proches


def proche_voisins():
    df = creer_pd()
    df = changer_90_min(df)
    df, X = standardiser(df)

    nom_joueur = input("Entrez le nom d'un joueur : ")

    joueurs_euclidienne = proches_voisins_distance_euclidienne(df, X, nom_joueur)
    joueurs_cosinus = proches_voisins_distance_cosinus(df, X, nom_joueur)
    joueurs_mahalanobis = proches_voisins_distance_mahalanobis(df, X, nom_joueur)

    print("\nDistance euclidienne :")
    print(joueurs_euclidienne[["nom", "equipe", "poste"]])

    print("\nDistance cosinus :")
    print(joueurs_cosinus[["nom", "equipe", "poste"]])

    print("\nDistance de Mahalanobis :")
    print(joueurs_mahalanobis[["nom", "equipe", "poste"]])
