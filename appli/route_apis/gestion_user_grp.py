from flask import Flask, request, jsonify
from app import connexion , curseur
from gestion_token import generateur_token

#Endpoint pour ajouter un user

@app.route('/admin/add_user', methods = ['POST'])
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

#Endpoint pour creer groupe

@app.route('/admin/add_group', methods = ['POST'])
@verificateur_token(roles = ['admin'])
def creer_group():
    donnee = request.get_json()
    id_groupe = donnee.get('id_groupe')
    name = donnee.get ('name')

    #Validation des donnees
    id not id_groupe:
        return jsonify ({
            'echec': True,
            'msg':'L\'id du groupe est requis'
            }), 400
    # Vérifier si le groupe existe déjà
    try:
        curseur.execute("SELECT id_groupe FROM groupe WHERE name = %s",(name,))
        if curseur.fetchone():
            return jsonify ({
                'echec':True,
                'msg': 'ce groupe existe deja'
                })
    #Inserer le nouveau groupe
        curseur.execute(
            INSERT INTO groupe (id_groupe , name) VALUES (%s,%s),(id_groupe , name))

        id_groupe = curseur.fetchone()[0]
        connexion.commit()
        return jsonify({
            'echec': False,
            'group':{
                'id_groupe': id_groupe,
                'name':name
                },
            'msg':'Groupe créé avec succès'
        }),201
    except Exception as erreur:
        connexion.rollback()
        return jsonify({
            'echec': True,
            'message': f'Erreur lors de la création du groupe: {str(erreur)}'
        }), 500
    finally:
        curseur.close()
        connexion.close()

#Endpoint pour ajouter un utilisateur à un groupe

@app.route('/admin/change_group/<int:user_id>/group', methods=['PUT'])
@verificateur_token(roles=['admin'])
def assign_group(user_id):
    donnee = request.get_json()
    id_groupe = donnee.get('id_groupe')
    if not id_groupe:
        return jsonify({
            'success': False,
            'message': 'L\'ID du groupe est requis'
        }), 400
    try:
        #Vérifier si l'utilisateur existe
        curseur.execute("SELECT user_id FROM utilisateur WHERE user_id = %s", (user_id,))
        if not curseur.fetchone():
            return jsonify({
                'echec': True,
                'message': 'Utilisateur non trouvé'
            }), 404

        #Vérifier si le groupe existe
        curseur.execute("SELECT id_groupe FROM groupe WHERE id_groupe = %s", (id_groupe,))
        if not curseur.fetchone():
            return jsonify({
                'success': False,
                'message': 'Groupe non trouvé'
            }), 404


        #### Sinon
        curseur.execute(
                "UPDATE utilisateur SET id_groupe = %s WHERE id_user = %s",(id_groupe, user_id)
                )
        connexion.commit()
        return jsonify({
            'echec': False,
            'message': f'Utilisateur {user_id} ajouté au groupe {id_groupe}'
        }), 200

        except Exception as erreur:
        connexion.rollback()
        return jsonify({
            'echec': True,
            'message': f'Erreur lors de l\'ajout de l\'utilisateur au groupe: {str(erreur)}'
        }), 500
    finally:
        curseur.close()
        connexion.close()
