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

def get_users_list(username):
    response = firestore_db.collection('User').get()
    users_list = []
    for user in response:
        data = user.to_dict()
        data["id"] = user.id
        if "username" in data and data["username"] == username:
            continue
        users_list.append(data)
    return users_list



@app.get("/users", response_class=HTMLResponse)
async def users(request: Request, token: str = Cookie(None)):
    error=None
    user_token = validate_firebase_token(token)
    if not user_token:
        return RedirectResponse(url="/", status_code=303)
    if request.query_params.get("error"):
        error = request.query_params.get("error")
    user_ref = get_user(user_token)
    user_data = user_ref.get().to_dict()
    username = user_data.get('username') if user_data else None
    userId = user_data.get('user_id') if user_data else None
    followers = user_data.get('followers') if user_data else []
    followers = None if [] else followers
    users = get_users_list(username)
    return templates.TemplateResponse('users.html', {'request': request, "token": token,  "error":error,"users":users,"userId":userId,"followers":followers})


def upload_image_to_storage(image_data, image_filename):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(image_filename)
    blob.upload_from_string(image_data, content_type="image/jpeg") 
    blob.make_public() 
    return blob.public_url


@app.post("/add-tweet")
async def add_tweet(request: Request, tweetContent: str = Form(...), tweetImage: UploadFile = Form(...)):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        raise HTTPException(status_code=403, detail="Authentication required")

    user_ref = get_user(user_token)
    user_data = user_ref.get().to_dict()
    if not user_data or not user_data.get('username'):
        raise HTTPException(status_code=400, detail="Username not set")

    if len(tweetContent) > 140:
        raise HTTPException(status_code=400, detail="Tweet exceeds 140 characters")

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(tweetImage.file, tmp)
        tmp.close()
        with open(tmp.name, "rb") as f:
            image_data = f.read()

    image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.jpg"
    image_url = upload_image_to_storage(image_data, image_filename)

    tweet = {
        'username': user_data['username'],
        'content': tweetContent,
        'image_url': image_url,
        'date': datetime.now()
    }
    firestore_db.collection('Tweet').add(tweet)

    return RedirectResponse(url="/home", status_code=303)

from fastapi import HTTPException

@app.post("/edit-tweet/{tweet_id}")
async def edit_tweet(tweet_id: str, request: Request, tweetContent: str = Form(...), tweetImage: UploadFile = Form(...)):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        raise HTTPException(status_code=403, detail="Authentication required")
    user_ref = get_user(user_token)
    user_data = user_ref.get().to_dict()
    if not user_data or not user_data.get('username'):
        raise HTTPException(status_code=400, detail="Username not set")

    if len(tweetContent) > 140:
        raise HTTPException(status_code=400, detail="Tweet exceeds 140 characters")

    tweet_ref = firestore_db.collection('Tweet').document(tweet_id)
    tweet_data = tweet_ref.get().to_dict()
    if not tweet_data:
        raise HTTPException(status_code=404, detail="Tweet not found")

    if tweet_data['username'] != user_data['username']:
        raise HTTPException(status_code=403, detail="You are not allowed to edit this tweet")

    image_data = None
    if tweetImage:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            shutil.copyfileobj(tweetImage.file, tmp)
            tmp.close()
            with open(tmp.name, "rb") as f:
                image_data = f.read()

    updated_tweet = {
        'content': tweetContent,
        'date': datetime.now()
    }

    if image_data:

        image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.jpg"
        image_url = upload_image_to_storage(image_data, image_filename)
        updated_tweet['image_url'] = image_url

    tweet_ref.update(updated_tweet)

    return RedirectResponse(url="/home", status_code=303)



@app.get("/delete_tweet")
async def deltetTweet(request: Request,):
    try:
        id=request.query_params.get("id")
        firestore_db.collection('Tweet').document(id).delete()
        return {"message": "Tweet deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete tweet: {str(e)}")

async def add_follower(user_id: str, follower_id: str):
    user_ref = firestore_db.collection('User').document(follower_id)
    user_data = user_ref.get().to_dict()
    if user_data:
        if "followers" not in user_data:
            user_data["followers"] = []
        if user_id not in user_data["followers"]:
            user_data["followers"].append(user_id)
            user_ref.update({"followers": user_data["followers"]})
        return {"message": "Successfully followed user"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

async def remove_follower(follower_id: str, user_id: str):
    user_ref = firestore_db.collection('User').document(user_id)
    user_data = user_ref.get().to_dict()
    if user_data:
        if "followers" in user_data:
            if follower_id in user_data["followers"]:
                user_data["followers"].remove(follower_id)
                user_ref.update({"followers": user_data["followers"]})
                return {"message": "Successfully unfollowed user"}
            else:
                raise HTTPException(status_code=404, detail="User not followed")
        else:
            raise HTTPException(status_code=404, detail="User has no followers")
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/follow")
async def follow_user(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    current_user_id=data.get("current_user_id")
    if not user_id:
        raise HTTPException(status_code=422, detail="Missing user_id in request body")
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    await add_follower(user_id, current_user_id)
    return {"message": "Successfully followed user"}


@app.post("/unfollow")
async def unfollow_user(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    current_user_id=data.get("current_user_id")
    if not user_id:
        raise HTTPException(status_code=422, detail="Missing user_id in request body")
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized") 
    await remove_follower(user_id, current_user_id)
    return {"message": "Successfully UnFollowed user"}
def userTwitterList(userName):
    response = firestore_db.collection('Tweet').where('username', '==', userName).get()
    tweet_list = []
    for tweet in response:
        data = tweet.to_dict()
        data["id"] = tweet.id
        data['date'] = data['date'].isoformat()
        tweet_list.append(data)
    
    last_10_tweets = tweet_list[-10:]
    return last_10_tweets


def get_user_by_id(user_id):
    user_ref = firestore_db.collection('User').document(user_id)
    user_data = user_ref.get().to_dict()
    return user_data


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def user_details(request: Request,user_id:str, token: str = Cookie(None),):
    user_token = validate_firebase_token(token)
    if not user_token:
        return RedirectResponse(url="/", status_code=303)
    if request.query_params.get("error"):
        error = request.query_params.get("error")
    userData = get_user_by_id(user_id)
    username = userData.get('username') if userData else None
    tweetsData = userTwitterList(username)
    user_ref = get_user(user_token)
    user_data = user_ref.get().to_dict()
    followers = user_data.get('followers') if user_data else None
    userId = user_data.get('user_id') if user_data else None
    return templates.TemplateResponse('userDetails.html', {'request': request, "token": token,"userData":userData,"tweetList":tweetsData,"followers":followers,"userId":userId})