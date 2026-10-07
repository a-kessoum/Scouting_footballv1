import sqlite3

DATABASE = "football_data.db"


def nettoyer_taille_poids(cursor):
    # on enleve cm de la taille pour nos données
    cursor.execute("UPDATE joueurs_bruts SET taille = REPLACE(taille, ' cm', '')")

    # on enleve kg du poids pour nos données
    cursor.execute("UPDATE joueurs_bruts SET poids = REPLACE(poids, ' kg', '')")


def creer_table_300_minutes(cursor):
    # on supprime l'ancienne table si elle existe
    cursor.execute("DROP TABLE IF EXISTS joueurs_300_minutes")

    # on garde uniquement les joueurs avec plus de 300 minutes
    cursor.execute("CREATE TABLE joueurs_300_minutes AS SELECT * FROM joueurs_bruts WHERE minutes_jouees > 300 ")


def compter_joueurs(cursor):
    # on compte le nombre de joueurs restants
    cursor.execute("SELECT COUNT(*) FROM joueurs_300_minutes")
    nombre = cursor.fetchone()[0]
    return nombre


def nettoyage():

    # connexion à la base
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # nettoyage taille et poids
    nettoyer_taille_poids(cursor)

    # création de la table avec les joueurs > 300 minutes
    creer_table_300_minutes(cursor)

    # sauvegarde des modifications
    conn.commit()

    # nombre de joueurs
    nombre = compter_joueurs(cursor)

    print(nombre, "joueurs ont joué plus de 300 minutes.")

    # fermeture de la base
    conn.close()

nettoyage()
