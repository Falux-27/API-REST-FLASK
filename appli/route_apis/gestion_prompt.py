from flask import Flask, request, jsonify
from app import connexion , curseur
from gestion_token import verificateur_token


#Endpoint d'ajout de prompt

@app.route('/prompts', methods=['POST'])
@verificateur_token(roles=['user', 'admin'])
def creation_prompt():
    donnee = request.get_json()
    titre = donnee.get('titre')
    contenu = donnee.get('contenu')
    prix = donnee.get('prix')
    moyenne = donnee.get('moyenne_note')
    etat = donnee.get('etat')
    user_id = donnee.get('user_id')
    user_id = get_jwt_identity()

    if not contenu:
        return jsonify({
            'success': False,
            'message': 'prompt ne peut pas etre vide'
        }), 400
    try:
        curseur.execute(
                'INSERT INTO prompt (titre,contenu,prix,moyenne,etat,user_id) VALUES (%s,%s,%s,%s,%s,%s),RETURNING id_prompt',
                (titre,contenu,prix,moyenne_note,etat,user_id,'En attente',1000))
        id_prompt = curseur.fetchone()[0]
        connexion.commit()
        return jsonify({
            'echec':False,
            'msg':'Prompt créé avec succès', 
            'id_prompt' : id_prompt
            }),201
    except Exception as erreur:
        connexion.rollback()
        return jsonify({
            'echec':True,
            'msg':f'Erreur lors de la création du prompt: {str(erreur)}'
            }),500


#Endpoint de validation/refus ou demande de modif à l'admin
@app.route('/prompts/<int:id_prompt>/status', methods=['PUT'])
@verificateur_token(roles=['admin'])
def modifier_etat(id_prompt):
    donnee = request.get_json()
    action = donnee.get('action')
    if not etat or etat not in ['valider', 'refuser', 'modifier','supprimer'] :
        return jsonify({
        'echec': True,
        'msg': 'Action non pris en charge'
        }),400
    try:
        #Vérifier si le prompt existe
        curseur.execute('SELECT id_prompt FROM prompt WHERE id_prompt = %s' ,(id_prompt,))
        prompt = curseur.fetchone()

        if not prompt:
            return jsonify({
                'success': False,
                'message': 'Prompt non trouvé'
            }), 404
        if action == 'valider':
        curseur.execute(
            "UPDATE prompt SET etat = %s WHERE prompt_id = %s",
            ('Activer',id_prompt)
        )
        message = 'Prompt activé avec succès'
    elif action == 'refuser':
        curseur.execute(
            "UPDATE prompt SET etat = %s WHERE id_prompt= %s",
            ('À supprimer', id_prompt)
        )
        message = 'Prompt refusé et marqué pour suppression'
    elif action == 'modifier':
        curseur.execute(
            "UPDATE prompt SET etat = %s WHERE id_prompt = %s",
            ('À revoir', id_prompt)
        )
        message = 'Prompt retourné à l\'auteur pour modifications'
    elif action == 'supprimer':
        curseur.execute("DELETE FROM prompt WHERE id_prompt = %s", (id_prompt,))
        connexion.commit()
        return jsonify({
            'success': True,
            'message': 'Prompt supprimé avec succès'
        }), 200

    # Commit pour les actions autres que 'supprimer'
    connexion.commit()
    return jsonify({
        'success': True,
        'message': message
    }), 200

except Exception as erreur:
    connexion.rollback()
    return jsonify({
        'success': False,
        'message': f'Erreur lors de la mise à jour du prompt: {str(erreur)}'
    }), 500

#Endpoint pour afficher les prompts
@app.route('/prompts', methods=['GET'])
@verificateur_token(roles=['user', 'admin'])  # optionnel si tu veux sécuriser l'accès
def afficher_prompts():
    try:
        curseur.execute("SELECT id_prompt, titre, contenu, prix, moyenne, etat, user_id FROM prompt")
        prompts = curseur.fetchall()

        if not prompts:
            return jsonify({
                'success': True,
                'prompts': [],
                'message': 'Aucun prompt trouvé'
            }), 200

        # Transformer chaque ligne SQL en dictionnaire
        liste_prompts = []
        for prompt in prompts:
            liste_prompts.append({
                'id_prompt': prompt[0],
                'titre': prompt[1],
                'contenu': prompt[2],
                'prix': prompt[3],
                'moyenne': prompt[4],
                'etat': prompt[5],
                'user_id': prompt[6]
            })

        return jsonify({
            'success': True,
            'prompts': liste_prompts
        }), 200

    except Exception as erreur:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des prompts: {str(erreur)}'
        }), 500


