import datetime
import jwt
from authentifcation import secret_key

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
