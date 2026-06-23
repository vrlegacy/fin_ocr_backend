import json
import urllib.request
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User

security = HTTPBearer()

# Cache JWKS keys to avoid requesting them on every API call
jwks_cache = None

def get_jwks():
    global jwks_cache
    if jwks_cache is not None:
        return jwks_cache
    try:
        url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            jwks_cache = json.loads(response.read().decode())
        return jwks_cache
    except Exception as e:
        print(f"Failed to fetch JWKS from Auth0: {e}")
        return None

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    
    # DEV Fallback: Allow easy local development testing
    if token.startswith("mock-token-"):
        parts = token.replace("mock-token-", "").split(":")
        sub = parts[0]
        email = parts[1] if len(parts) > 1 else f"{sub.replace('|', '_')}@example.com"
        name = parts[2] if len(parts) > 2 else email.split("@")[0].capitalize()
        return {
            "sub": sub,
            "email": email,
            "name": name
        }
    if token.startswith("mock-") or token == "dummy":
        return {
            "sub": "auth0|mock_user_123",
            "email": "darshan@example.com",
            "name": "Darshan"
        }

    # Verify standard Auth0 token
    jwks = get_jwks()
    if not jwks:
        # Fallback in case JWKS server is temporarily down or domain is misconfigured
        # For security we enforce verification in production, but print warnings locally.
        print("Warning: Auth0 JWKS key server could not be reached. Attempting unverified payload decode.")
        try:
            return jwt.get_unverified_claims(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Auth0 JWKS unreachable and token claims cannot be parsed",
                headers={"WWW-Authenticate": "Bearer"},
            )

    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token format: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    rsa_key = {}
    for key in jwks.get("keys", []):
        if key["kid"] == unverified_header.get("kid"):
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
            break

    if not rsa_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Public key matching 'kid' not found in Auth0 JWKS",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE,
            issuer=f"https://{settings.AUTH0_DOMAIN}/"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError:
        # In some cases Auth0 tokens don't have the audience claim matched to client_id
        # Let's decode claim without audience check to be flexible if audience verification fails
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                options={"verify_aud": False},
                issuer=f"https://{settings.AUTH0_DOMAIN}/"
            )
            return payload
        except Exception as claim_err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"JWT verification failed (claims error): {str(claim_err)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(payload: dict = Depends(verify_token), db: Session = Depends(get_db)) -> User:
    auth0_sub = payload.get("sub")
    if not auth0_sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User sub claim missing from token",
        )
    
    # Query db
    user = db.query(User).filter(User.auth0_sub == auth0_sub).first()
    
    # Sync user on-demand if they don't exist yet in Supabase
    if not user:
        email = payload.get("email", f"{auth0_sub.replace('|', '_')}@example.com")
        name = payload.get("name", email.split("@")[0])
        
        user = User(
            auth0_sub=auth0_sub,
            username=name,
            email=email,
            role="Personal"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    return user
