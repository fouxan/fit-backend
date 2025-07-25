from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
from app.config.settings import settings


class GoogleOAuth2:
    """Google OAuth2 authentication helper"""
    
    @staticmethod
    async def verify_token(token: str) -> dict:
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'email': idinfo['email'],
                'email_verified': idinfo['email_verified'],
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture'),
                'given_name': idinfo.get('given_name'),
                'family_name': idinfo.get('family_name'),
                'locale': idinfo.get('locale'),
                'sub': idinfo['sub']  # Google User ID
            }
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )
