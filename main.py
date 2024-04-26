import json
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import firestore, storage
from google.auth.transport import requests
import google.oauth2.id_token
import tempfile
import shutil


app = FastAPI()

firestore_db = firestore.Client()

firebase_request_adapter = requests.Request()
storage_client = storage.Client()
bucket_name = "twitter-f6929.firebaseapp.com"

app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")


def get_user(user_token):
    user_ref = firestore_db.collection('User').document(user_token['user_id'])
    user = user_ref.get()
    if not user.exists:
        user_data = {
            'email': user_token['email'],
            'user_id': user_token['user_id']
        }
        user_ref.set(user_data)
    return user_ref


def validate_firebase_token(id_token):
    if not id_token:
        return None

    user_token = None
    try:
        user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter, clock_skew_in_seconds=100)
    except ValueError as err:
        print(str(err))

    return user_token


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        try:
            return templates.TemplateResponse('main.html', {'request': request, 'user_token': None, 'error_message': None, 'user_info': None})            
        except ValueError as err:
            print(str(err))
    user = get_user(user_token)
    return templates.TemplateResponse('main.html', {'request': request})

