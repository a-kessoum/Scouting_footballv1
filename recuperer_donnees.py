import os
import sqlite3
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("APISPORTS_KEY")

HEADERS = {"x-apisports-key": API_KEY}

BASE_URL = "https://v3.football.api-sports.io"

# On recupere championnat par championnat on va changer les id et le nom à la main due aux contraintes du site API-Football
LEAGUE_ID = 140
LIGUE_NOM = "La Liga"
SAISON = 2023

MAX_PAGES = 4

DATABASE = "football_data.db"


def get_stat(stats, categorie, statistique, valeur_defaut=0):
    # fonction qui recupère une stat
    valeur = stats.get(categorie, {}).get(statistique)

    if valeur is None:
        return valeur_defaut

    return valeur


def recuperer_equipes():
    # fonction qui récupère toutes les équipes d'un championnat
    res = requests.get(f"{BASE_URL}/teams", headers=HEADERS,params={"league": LEAGUE_ID,"season": SAISON})
    data = res.json()
    teams_data = data.get("response", [])
    equipes = [(t["team"]["id"], t["team"]["name"]) for t in teams_data]

    print(f"{len(equipes)} équipes trouvées.\n")
    return equipes


def recuperer_joueurs_equipe(team_id, team_nom):
    # on recupere les joueurs d'une équipe
    print("Extraction pour :",team_nom, ", ID :", team_id)
    joueurs_equipe = []
    page = 1
    total_pages = 1

    while page <= total_pages and page <= MAX_PAGES:

        params = {"team": team_id, "league": LEAGUE_ID, "season": SAISON,"page": page}
        res = requests.get(f"{BASE_URL}/players",headers=HEADERS,params=params)
        data = res.json()
        total_pages = data.get("paging", {}).get("total", 1)
        joueurs = data.get("response", [])

        print(
            f"   Page {page}/{total_pages} : "
            f"{len(joueurs)} joueurs"
        )


        # traitement de chaque joueur
        for item in joueurs:
            joueur = traiter_joueur(item,team_nom)
            joueurs_equipe.append(joueur)


        page += 1

        # attente de sécurité pour éviter d'envoyer trop de requêtes
        time.sleep(6.5)

    return joueurs_equipe


def traiter_joueur(item, team_nom):

    # informations générales
    info = item.get("player", {})

    # statistiques
    stats_list = item.get("statistics", [])

    stats = (stats_list[0] if stats_list else {})


    # on recupère toutes les infos et les stats du joueurs

    joueur_id = info.get("id")
    nom = info.get("name")
    prenom = info.get("firstname")
    nom_famille = info.get("lastname")
    age = info.get("age")
    nationalite = info.get("nationality")
    taille = info.get("height")
    poids = info.get("weight")
    equipe = team_nom
    poste = get_stat(stats,"games","position","Inconnu")
    apparitions = get_stat(stats, "games", "appearences")
    titularisations = get_stat(stats, "games", "lineups")
    minutes_jouees = get_stat(stats, "games", "minutes")
    note = get_stat(stats, "games", "rating", None)
    tirs = get_stat(stats, "shots", "total")
    tirs_cadres = get_stat(stats, "shots", "on")
    buts = get_stat(stats, "goals", "total")
    passes_decisives = get_stat(stats, "goals", "assists")
    passes = get_stat(stats, "passes", "total")
    passes_cles = get_stat(stats, "passes", "key")
    precision_passes = get_stat(stats,"passes","accuracy",None)
    tacles = get_stat(stats, "tackles", "total")
    blocs = get_stat(stats, "tackles", "blocks")
    interceptions = get_stat(stats,"tackles","interceptions")
    duels = get_stat(stats, "duels", "total")
    duels_gagnes = get_stat(stats, "duels", "won")
    dribbles_tentes = get_stat(stats, "dribbles", "attempts")
    dribbles_reussis = get_stat(stats,"dribbles","success")
    fautes_subies = get_stat(stats, "fouls", "drawn")
    fautes_commises = get_stat(stats,"fouls","committed")
    cartons_jaunes = get_stat(stats,"cards","yellow")

    cartons_rouges = get_stat(stats,"cards","red")

    return (
    joueur_id,
    nom,
    prenom,
    nom_famille,
    nationalite,
    equipe,
    LEAGUE_ID,
    LIGUE_NOM,
    SAISON,
    poste,

    age,
    taille,
    poids,
    apparitions,
    titularisations,
    minutes_jouees,
    note,
    precision_passes,

    tirs,
    tirs_cadres,
    buts,
    passes_decisives,
    passes,
    passes_cles,
    tacles,
    blocs,
    interceptions,
    duels,
    duels_gagnes,
    dribbles_tentes,
    dribbles_reussis,
    fautes_subies,
    fautes_commises,
    cartons_jaunes,
    cartons_rouges)

def recuperer_tous_joueurs(equipes):
    # fct pour récup tt les joueurs d'une ligue
    joueurs = []

    for team_id, team_nom in equipes:

        joueurs_equipe = recuperer_joueurs_equipe(
            team_id,
            team_nom
        )

        joueurs.extend(joueurs_equipe)


    return joueurs


def creer_table(cursor):
    # on crée la table sql
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS joueurs_bruts (
            id_ligne INTEGER PRIMARY KEY AUTOINCREMENT,
            joueur_id INTEGER,
            nom TEXT,
            prenom TEXT,
            nom_famille TEXT,
            nationalite TEXT,
            equipe TEXT,
            ligue_id INTEGER,
            ligue_nom TEXT,
            saison INTEGER,
            poste TEXT,

            age INTEGER,
            taille TEXT,
            poids TEXT,
            apparitions INTEGER,
            titularisations INTEGER,
            minutes_jouees INTEGER,
            note REAL,
            precision_passes INTEGER,

            tirs INTEGER,
            tirs_cadres INTEGER,
            buts INTEGER,
            passes_decisives INTEGER,
            passes INTEGER,
            passes_cles INTEGER,
            tacles INTEGER,
            blocs INTEGER,
            interceptions INTEGER,
            duels INTEGER,
            duels_gagnes INTEGER,
            dribbles_tentes INTEGER,
            dribbles_reussis INTEGER,
            fautes_subies INTEGER,
            fautes_commises INTEGER,
            cartons_jaunes INTEGER,
            cartons_rouges INTEGER
        )
        """
    )


def inserer_joueurs(cursor, joueurs):
    # on insère les joueurs dans la table sql
    cursor.executemany(
        """
        INSERT INTO joueurs_bruts (
            joueur_id,
            nom,
            prenom,
            nom_famille,
            nationalite,
            equipe,
            ligue_id,
            ligue_nom,
            saison,
            poste,

            age,
            taille,
            poids,
            apparitions,
            titularisations,
            minutes_jouees,
            note,
            precision_passes,

            tirs,
            tirs_cadres,
            buts,
            passes_decisives,
            passes,
            passes_cles,
            tacles,
            blocs,
            interceptions,
            duels,
            duels_gagnes,
            dribbles_tentes,
            dribbles_reussis,
            fautes_subies,
            fautes_commises,
            cartons_jaunes,
            cartons_rouges
        )

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?
        )
        """,

        joueurs
    )



def sauvegarder_joueurs(joueurs):
    # on sauvegarde les joueurs dans la base
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # création de la table si elle n'existe pas
    creer_table(cursor)
    # insertion des joueurs
    inserer_joueurs(cursor,joueurs)
    # sauvegarde
    conn.commit()
    # nombre total de lignes
    cursor.execute("SELECT COUNT(*) FROM joueurs_bruts")
    nombre_total = cursor.fetchone()[0]
    print(
        f"\n{len(joueurs)} lignes ajoutées pour "
        f"{LIGUE_NOM}."
    )

    print(f"{nombre_total} lignes au total dans joueurs_bruts.")

    conn.close()


def recup_donnees():

    print("Championnat : ", LIGUE_NOM)
    equipes = recuperer_equipes()
    time.sleep(1) # sécurité pour pas envoyer toute les requetes d'un coup
    joueurs = recuperer_tous_joueurs(equipes)
    print(len(joueurs), " joueurs récupérés")
    sauvegarder_joueurs(joueurs)
    print("\nTerminé.")
    

recup_donnees()
