from flask import Flask, request, jsonify
from passlib.hash import sha256_crypt
from app import connexion , curseur
from gestion_token import generateur_token

#Endpoint pour ajouter un user:
@app.route('/authentification/admin/add_user', methods = ['POST'])
@verificateur_token(roles = ['admin'])
def create_user ():
    #Récuperer les donnees de la requete
    donnee = request.get_json()
    user_id = donnee.get('user_id')
    prenom = donnee.get('prenom')
    email = donnee.get ('email')
    password = donnee.get ('password')
    role = donnee.get('role','user')
    id_groupe = donnee.get('id_groupe')
    #Validation des entrées
    if not prenom or not password or user_id is None:
        return jsonify({
            'echec': True,
            'message':'Le nom d\'utulisateur et le mot de passe sont obligatoires'
            }); 400
    #Hachage du mot de passe
    #mdp_crypted = hash_password(password)
    
    #Verifier si l'user existe deja
    try:
        curseur.execute("SELECT user_id FROM utilisateur WHERE user_id = %s",(user_id,))
        if curseur.fetchone():
           return jsonify ({
               'echec':True,
               'message': 'Cet utilisateur existe déja'
               }),409
    #Ajout de l'user non existant
        curseur.execute(
        "INSERT INTO utilisateur(user_id ,prenom,email,password,role, id_groupe) 
        VALUES (%s, %s, %s, %s, %s, %s)",(user_id ,prenom,email,password,role, id_groupe))
    #Confirmer l'ajout 
        connexion.commit()
            return jsonify({
                'echec': False,
                'user': {
                    'user_id': user_id,
                    'prenom': prenom,
                    'email': email,
                    'role': role,
                    'id_groupe': id_groupe
                },
                'message':'Utilisateur créé avec succès'
            }),201
    except Exception as erreur:
        #Annuler l'ajout en cas d'erreur
        connexion.rollback()
        return jsonify({
            'echec':True,
            'message': f'Erreur lors de la création de l\'utilisateur: {str(erreur)}'
        
        }), 500 


#Endpoint pour le login

@app.route('/authentification/login')
@verificateur_token(roles = ['admin','user'])
def log_In ():
    donnee = request.get_json()
    prenom = donnee.get('prenom')
    email = donnee.get('email')
    password = donnee.get ('password')
    #Verification
    curseur.execute("SELECT user_id, prenom,email,password,role, id_groupe FROM utilisateur WHERE email = %s",(email,))
    #Recuperer le resultat de la requete
    user = curseur.fetchone()
    #Generer le token sur les donnees du recuperée
    if user:

        token = generateur_token (user[0],user[1],user[2],user[3],user[4])
        return jsonify({
            'echec':False,
            'token':token,
            'user':{
            'user_id': user_id ,
            'username' : prenom,
            'role': role,
            'group_id': id_group,
            'exp': date_expiration
            }
                }
        })
    return jsonify({'echec': True, 'message': 'Identifiants incorrects'}), 401
