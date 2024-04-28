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

def get_twitter_list(followers, username):
    response = firestore_db.collection('Tweet').get()
    tweet_list = []
    for tweet in response:
        data = tweet.to_dict()
        data["id"] = tweet.id
        if data["username"] == username or (followers is not None and data["username"] in followers):
            tweet_list.append(data)
    tweet_list.sort(key=lambda x: x['date'], reverse=True)
    latest_20_tweets = tweet_list[:20]
    return latest_20_tweets


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, token: str = Cookie(None)):
    error=None
    user_token = validate_firebase_token(token)
    if not user_token:
        return RedirectResponse(url="/", status_code=303)
    user_ref = get_user(user_token)
    user_data = user_ref.get().to_dict()
    username = user_data.get('username') if user_data else None
    userId = user_data.get('user_id') if user_data else None
    followers = user_data.get('followers') if user_data else None
    tweet_list = get_twitter_list(followers,username)
    if request.query_params.get("error"):
        error = request.query_params.get("error")
    for tweet in tweet_list:
        tweet['date'] = tweet['date'].isoformat()
    tweet_list_json = json.dumps(tweet_list)
    return templates.TemplateResponse('home.html', {'request': request, "token": token, "username": username, "tweetList": tweet_list_json,"error":error,"userId":userId})

@app.post("/set-username")
async def set_username(request: Request):
    form_data = await request.form()
    username = form_data['username']
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    user_id = user_token.get('user_id') if user_token else None
    user_ref = firestore_db.collection('User').document(user_id)
    user_data = user_ref.get().to_dict() if user_ref.get().exists else {}
    if 'username' in user_data and user_data['username']:
        return RedirectResponse(url="/home?error=User Already Exists", status_code=303)
    existing_usernames = firestore_db.collection('User').where('username', '==', username).get()
    if existing_usernames:
        return RedirectResponse(url="/home?error=User Already Exists", status_code=303)
    user_ref.update({'username': username})
    return RedirectResponse(url="/home", status_code=303)