import firebase_admin
from firebase_admin import credentials, storage
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if you use one
load_dotenv()

# Default path to 'file.json' if the environment variable is not set
cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", os.path.join(os.path.dirname(__file__), 'file.json'))

if not os.path.exists(cred_path):
    raise FileNotFoundError(f"No such file or directory: '{cred_path}'")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")})