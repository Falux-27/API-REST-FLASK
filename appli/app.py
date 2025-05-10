from flask import Flask
import psycopg2
app = Flask(__name__)
#Configuration de labase de donnée 
username = "postgres"
pass_word = "beta47"
port = 5432
database_name = "base_api"

try :
    connexion = psycopg2.connect (
            dbname = database_name,
            user = username, 
            password = pass_word , 
            port = port , 
            host= 'localhost'  )
#Initialisation de l'objet cursor:
#Cette objet permet d'executer des requetes sur la base de donnnee connectée                                              
    curseur = connexion.cursor()                                                                                          
    #Ceci est un test                                    
    curseur.execute("SELECT version();")
    result = curseur.fetchone()
    print ("La version de PostgresSQL est:",result)
    curseur.close()
    connexion.close()
except psycopg2.Error as erreur:
     print("Erreur de connexion à la base de données :", erreur)
if __name__ == '__main__':
    app.run(debug=True)

