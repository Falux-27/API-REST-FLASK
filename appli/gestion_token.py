import datetime
import jwt
from functools import wraps
from flask import request, jsonify
from authentification import secret_key

#Créer le générateur de token

def generateur_token(user_id, prenom , role , id_group= None):
    date_expiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 24)
    #Creation d'entete
    header = {
            'alg': 'HS256',
            'typ': 'JWT'
            }
    #La payload
    payload = {
            'user_id': user_id , 
            'username' : prenom,
            'role': role,
            'group_id': id_group,
            'exp': date_expiration
            }
    #Combinaison des elements
    token = jwt.encode(payload,secret_key,algoritm = 'HS256',headers = header) 
    return token


#Vérification du token 
def verificateur_token(roles = None):
    def decorateur(func_protected):
        @wraps(func_protected)
        def decoration(*args, **kwargs):
            #Extraction du token depuis  l'en-tête
            token = request.headers.get('Authorization')
            if not token:
                return jsonify ({'message':Pas autorisé}),401
            #Retirer l'emballage 'Bearer'
            if token.startswith ('Bearer '):
                token = token [7:]
            try:
                #Vérification de la signature et décodage du token
                infos_token = jwt.decode(token, secret_key, algorithms=['HS256'])

                #Extraction des informations utilisateur
                user_role = infos_token.get('role')

                #Vérification des priviléges en fonction des roles
                if roles is not None and user_role not in roles
                    return jsonify({'msg': 'Accès non autorisé'}), 403
                request.user = infos_token
                #Erreur si le token est expiré
            except jwt.ExpiredSignatureError:
                return jsonify({'msg': Token expiré}), 401
            #Erreur si le token est invalide
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Token invalide'}), 401
            #Exécution de la fonction protégée si tout est correct
            return func_protected(*args, **kwargs)
        return decoration
    return decorateur
