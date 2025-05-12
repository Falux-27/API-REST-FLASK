@app.route('/api/prompts/<int:prompt_id>/vote', methods=['POST'])
@token_required(roles=['user', 'admin'])
def vote_on_prompt(prompt_id):
    # Récupérer les informations de l'utilisateur à partir du token
    current_user_id = request.user['user_id']
    current_user_group_id = request.user.get('group_id')
    
    # Vérifier les données de la requête
    try:
        # Connexion à la base de données
        curseur.execute(
            "SELECT user_id, prompt_status, group_id FROM prompts WHERE id = %s", 
            (prompt_id,)
        )
        prompt = curseur.fetchone()
        
        if not prompt:
            return jsonify({
                'success': False,
                'message': 'Prompt non trouvé'
            }), 404
        
        # Vérifier que le prompt est dans un état permettant le vote
        if prompt['prompt_status'] != 'rappel':
            return jsonify({
                'success': False,
                'message': 'Le vote n\'est pas autorisé pour ce prompt'
            }), 400
        
        # Empêcher de voter sur son propre prompt
        if prompt['user_id'] == current_user_id:
            return jsonify({
                'success': False,
                'message': 'Vous ne pouvez pas voter sur votre propre prompt'
            }), 403
        
        # Déterminer la valeur du vote
        vote_value = 2 if current_user_group_id == prompt['group_id'] else 1
        
        # Vérifier si l'utilisateur a déjà voté
        curseur.execute(
            "SELECT vote_id FROM votes WHERE prompt_id = %s AND user_id = %s", 
            (prompt_id, current_user_id)
        )
        existing_vote = curseur.fetchone()
        
        if existing_vote:
            return jsonify({
                'success': False,
                'message': 'Vous avez déjà voté sur ce prompt'
            }), 400
        
        # Insérer le vote
        curseur.execute(
            "INSERT INTO votes (prompt_id, user_id, vote_value) VALUES (%s, %s, %s)",
            (prompt_id, current_user_id, vote_value)
        )
        
        # Calculer le total des votes
        curseur.execute(
            "SELECT SUM(vote_value) as total_votes FROM votes WHERE prompt_id = %s",
            (prompt_id,)
        )
        total_votes = curseur.fetchone()['total_votes']
        
        # Vérifier si le prompt doit être activé
        if total_votes >= 6:
            curseur.execute(
                "UPDATE prompts SET prompt_status = 'activer' WHERE id = %s",
                (prompt_id,)
            )
        
        # Commit de la transaction
        connexion.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vote enregistré avec succès',
            'total_votes': total_votes,
            'prompt_status': 'activer' if total_votes >= 6 else 'rappel'
        }), 200
    
    except Exception as e:
        # Annuler la transaction en cas d'erreur
        connexion.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors du vote : {str(e)}'
        }), 500
