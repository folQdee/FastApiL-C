from datetime import datetime, timedelta
from jose import JWTError, jwt
import dotenv
import os

dotenv.load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


def create_access_token(data: dict, expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES):
    copy_data = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta if expires_delta else ACCESS_TOKEN_EXPIRE_MINUTES
    )
    copy_data.update({"exp":expire})
    encoded = jwt.encode(copy_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def decode_access_token(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except:
        return None
