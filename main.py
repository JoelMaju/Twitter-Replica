import json
import os
import uuid
from datetime import datetime

from fastapi import (
    FastAPI,
    Request,
    Form,
    HTTPException,
    UploadFile,
    Cookie,
    File,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from google.cloud import firestore
from google.auth.transport import requests
import google.oauth2.id_token

import local_constants


# ---------------------------------------------------------
# Application setup
# ---------------------------------------------------------

app = FastAPI()

firestore_db = firestore.Client(
    project=local_constants.PROJECT_NAME
)

firebase_request_adapter = requests.Request()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

templates = Jinja2Templates(directory="templates")

UPLOAD_DIRECTORY = "static/uploads"


# ---------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------

def validate_firebase_token(id_token):
    """
    Validate a Firebase ID token.

    Returns the decoded Firebase token when valid,
    otherwise returns None.
    """
    if not id_token:
        return None

    try:
        return google.oauth2.id_token.verify_firebase_token(
            id_token,
            firebase_request_adapter,
            clock_skew_in_seconds=100,
        )
    except ValueError as err:
        print(f"Firebase token validation error: {err}")
        return None


def get_user(user_token):
    """
    Get the current user from Firestore.

    If the user does not already exist in Firestore,
    create a user document automatically.
    """
    user_id = user_token["user_id"]

    user_ref = (
        firestore_db
        .collection("User")
        .document(user_id)
    )

    user_snapshot = user_ref.get()

    if not user_snapshot.exists:
        user_data = {
            "email": user_token.get("email"),
            "user_id": user_id,
        }

        user_ref.set(user_data)

    return user_ref


def require_authenticated_user(request: Request):
    """
    Validate the Firebase token stored in the cookie
    and return both the Firebase token and Firestore user.
    """
    id_token = request.cookies.get("token")

    user_token = validate_firebase_token(id_token)

    if not user_token:
        raise HTTPException(
            status_code=403,
            detail="Authentication required",
        )

    user_ref = get_user(user_token)
    user_data = user_ref.get().to_dict()

    if not user_data:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user_token, user_ref, user_data


# ---------------------------------------------------------
# Image helpers
# ---------------------------------------------------------

async def save_image_locally(
    image: UploadFile | None,
) -> str | None:
    """
    Save uploaded images inside static/uploads.

    Only JPG, PNG, and WebP files are accepted.
    Maximum upload size is 5 MB.
    """
    if not image or not image.filename:
        return None

    allowed_types = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    extension = allowed_types.get(image.content_type)

    if not extension:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and WebP images are allowed",
        )

    image_data = await image.read()

    max_size = 5 * 1024 * 1024

    if len(image_data) > max_size:
        raise HTTPException(
            status_code=400,
            detail="Image must be smaller than 5 MB",
        )

    os.makedirs(
        UPLOAD_DIRECTORY,
        exist_ok=True,
    )

    filename = f"{uuid.uuid4().hex}{extension}"

    file_path = os.path.join(
        UPLOAD_DIRECTORY,
        filename,
    )

    with open(file_path, "wb") as output_file:
        output_file.write(image_data)

    return f"/static/uploads/{filename}"


def delete_local_image(image_url):
    """
    Delete a locally stored tweet image when possible.

    Only files inside /static/uploads/ are removed.
    """
    if not image_url:
        return

    prefix = "/static/uploads/"

    if not image_url.startswith(prefix):
        return

    filename = image_url.removeprefix(prefix)

    file_path = os.path.join(
        UPLOAD_DIRECTORY,
        filename,
    )

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as err:
            print(f"Could not delete image: {err}")


# ---------------------------------------------------------
# Login page
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    id_token = request.cookies.get("token")

    user_token = validate_firebase_token(id_token)

    if user_token:
        get_user(user_token)

    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "user_token": user_token,
            "error_message": None,
            "user_info": None,
        },
    )


# ---------------------------------------------------------
# Tweet feed
# ---------------------------------------------------------

def get_twitter_list(followers, username):
    """
    Return tweets from the current user and users
    that the current user follows.
    """
    response = (
        firestore_db
        .collection("Tweet")
        .get()
    )

    tweet_list = []

    followers = followers or []

    for tweet in response:
        data = tweet.to_dict()

        data["id"] = tweet.id

        tweet_username = data.get("username")

        if (
            tweet_username == username
            or tweet_username in followers
        ):
            tweet_list.append(data)

    tweet_list.sort(
        key=lambda tweet: tweet.get(
            "date",
            datetime.min,
        ),
        reverse=True,
    )

    return tweet_list[:20]


@app.get("/home", response_class=HTMLResponse)
async def home(
    request: Request,
    token: str = Cookie(None),
):
    user_token = validate_firebase_token(token)

    if not user_token:
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    user_ref = get_user(user_token)
    user_data = user_ref.get().to_dict() or {}

    username = user_data.get("username")
    user_id = user_data.get("user_id")
    followers = user_data.get("followers", [])

    tweet_list = get_twitter_list(
        followers,
        username,
    )

    error = request.query_params.get("error")

    for tweet in tweet_list:
        tweet_date = tweet.get("date")

        if tweet_date:
            tweet["date"] = tweet_date.isoformat()

    tweet_list_json = json.dumps(tweet_list)

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "token": token,
            "username": username,
            "tweetList": tweet_list_json,
            "error": error,
            "userId": user_id,
        },
    )


# ---------------------------------------------------------
# Username setup
# ---------------------------------------------------------

@app.post("/set-username")
async def set_username(request: Request):
    user_token, user_ref, user_data = (
        require_authenticated_user(request)
    )

    form_data = await request.form()

    username = str(
        form_data.get("username", "")
    ).strip()

    if not username:
        return RedirectResponse(
            url="/home?error=Username is required",
            status_code=303,
        )

    if len(username) > 30:
        return RedirectResponse(
            url="/home?error=Username is too long",
            status_code=303,
        )

    if user_data.get("username"):
        return RedirectResponse(
            url="/home?error=Username already set",
            status_code=303,
        )

    existing_usernames = (
        firestore_db
        .collection("User")
        .where("username", "==", username)
        .get()
    )

    if existing_usernames:
        return RedirectResponse(
            url="/home?error=Username already exists",
            status_code=303,
        )

    user_ref.update({
        "username": username
    })

    return RedirectResponse(
        url="/home",
        status_code=303,
    )


# ---------------------------------------------------------
# Add tweet
# ---------------------------------------------------------

@app.post("/add-tweet")
async def add_tweet(
    request: Request,
    tweetContent: str = Form(...),
    tweetImage: UploadFile | None = File(None),
):
    _, _, user_data = require_authenticated_user(
        request
    )

    username = user_data.get("username")

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username not set",
        )

    tweet_content = tweetContent.strip()

    if not tweet_content:
        raise HTTPException(
            status_code=400,
            detail="Tweet content cannot be empty",
        )

    if len(tweet_content) > 140:
        raise HTTPException(
            status_code=400,
            detail="Tweet exceeds 140 characters",
        )

    image_url = await save_image_locally(
        tweetImage
    )

    tweet = {
        "username": username,
        "content": tweet_content,
        "image_url": image_url,
        "date": datetime.now(),
    }

    firestore_db.collection("Tweet").add(tweet)

    return RedirectResponse(
        url="/home",
        status_code=303,
    )


# ---------------------------------------------------------
# Edit tweet
# ---------------------------------------------------------

@app.post("/edit-tweet/{tweet_id}")
async def edit_tweet(
    tweet_id: str,
    request: Request,
    tweetContent: str = Form(...),
    tweetImage: UploadFile | None = File(None),
):
    _, _, user_data = require_authenticated_user(
        request
    )

    username = user_data.get("username")

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username not set",
        )

    tweet_content = tweetContent.strip()

    if not tweet_content:
        raise HTTPException(
            status_code=400,
            detail="Tweet content cannot be empty",
        )

    if len(tweet_content) > 140:
        raise HTTPException(
            status_code=400,
            detail="Tweet exceeds 140 characters",
        )

    tweet_ref = (
        firestore_db
        .collection("Tweet")
        .document(tweet_id)
    )

    tweet_snapshot = tweet_ref.get()

    if not tweet_snapshot.exists:
        raise HTTPException(
            status_code=404,
            detail="Tweet not found",
        )

    tweet_data = tweet_snapshot.to_dict()

    if tweet_data.get("username") != username:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to edit this tweet",
        )

    updated_tweet = {
        "content": tweet_content,
        "date": datetime.now(),
    }

    if tweetImage and tweetImage.filename:
        new_image_url = await save_image_locally(
            tweetImage
        )

        old_image_url = tweet_data.get(
            "image_url"
        )

        updated_tweet["image_url"] = (
            new_image_url
        )

        delete_local_image(old_image_url)

    tweet_ref.update(updated_tweet)

    return RedirectResponse(
        url="/home",
        status_code=303,
    )


# ---------------------------------------------------------
# Delete tweet
# ---------------------------------------------------------

@app.get("/delete_tweet")
async def delete_tweet(request: Request):
    """
    Keeps the existing GET endpoint so that the current
    home.html JavaScript continues to work.

    Authentication and ownership are now checked before
    deleting a tweet.
    """
    _, _, user_data = require_authenticated_user(
        request
    )

    tweet_id = request.query_params.get("id")

    if not tweet_id:
        raise HTTPException(
            status_code=400,
            detail="Tweet ID is required",
        )

    tweet_ref = (
        firestore_db
        .collection("Tweet")
        .document(tweet_id)
    )

    tweet_snapshot = tweet_ref.get()

    if not tweet_snapshot.exists:
        raise HTTPException(
            status_code=404,
            detail="Tweet not found",
        )

    tweet_data = tweet_snapshot.to_dict()

    if (
        tweet_data.get("username")
        != user_data.get("username")
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this tweet",
        )

    image_url = tweet_data.get("image_url")

    tweet_ref.delete()

    delete_local_image(image_url)

    return {
        "message": "Tweet deleted successfully"
    }


# ---------------------------------------------------------
# Users
# ---------------------------------------------------------

def get_users_list(username):
    response = (
        firestore_db
        .collection("User")
        .get()
    )

    users_list = []

    for user in response:
        data = user.to_dict()

        data["id"] = user.id

        if not data.get("username"):
            continue

        if data.get("username") == username:
            continue

        users_list.append(data)

    return users_list


@app.get("/users", response_class=HTMLResponse)
async def users(
    request: Request,
    token: str = Cookie(None),
):
    user_token = validate_firebase_token(token)

    if not user_token:
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    user_ref = get_user(user_token)
    user_data = user_ref.get().to_dict() or {}

    username = user_data.get("username")
    user_id = user_data.get("user_id")
    followers = user_data.get("followers", [])

    users_list = get_users_list(username)

    error = request.query_params.get("error")

    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "token": token,
            "error": error,
            "users": users_list,
            "userId": user_id,
            "followers": followers,
        },
    )


# ---------------------------------------------------------
# Follow / Unfollow
# ---------------------------------------------------------

def follow_username(
    current_user_id: str,
    target_username: str,
):
    """
    Add a username to the current user's following list.
    """
    user_ref = (
        firestore_db
        .collection("User")
        .document(current_user_id)
    )

    user_snapshot = user_ref.get()

    if not user_snapshot.exists:
        raise HTTPException(
            status_code=404,
            detail="Current user not found",
        )

    user_data = user_snapshot.to_dict()

    followers = user_data.get(
        "followers",
        [],
    )

    if target_username not in followers:
        followers.append(target_username)

        user_ref.update({
            "followers": followers
        })


def unfollow_username(
    current_user_id: str,
    target_username: str,
):
    """
    Remove a username from the current user's
    following list.
    """
    user_ref = (
        firestore_db
        .collection("User")
        .document(current_user_id)
    )

    user_snapshot = user_ref.get()

    if not user_snapshot.exists:
        raise HTTPException(
            status_code=404,
            detail="Current user not found",
        )

    user_data = user_snapshot.to_dict()

    followers = user_data.get(
        "followers",
        [],
    )

    if target_username not in followers:
        raise HTTPException(
            status_code=404,
            detail="User is not followed",
        )

    followers.remove(target_username)

    user_ref.update({
        "followers": followers
    })


@app.post("/follow")
async def follow_user(request: Request):
    user_token, _, user_data = (
        require_authenticated_user(request)
    )

    data = await request.json()

    # Existing frontend sends the target username
    # using the key "user_id".
    target_username = data.get("user_id")

    if not target_username:
        raise HTTPException(
            status_code=422,
            detail="Missing user_id in request body",
        )

    current_username = user_data.get(
        "username"
    )

    if target_username == current_username:
        raise HTTPException(
            status_code=400,
            detail="You cannot follow yourself",
        )

    matching_users = (
        firestore_db
        .collection("User")
        .where(
            "username",
            "==",
            target_username,
        )
        .get()
    )

    if not matching_users:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    current_user_id = user_token["user_id"]

    follow_username(
        current_user_id,
        target_username,
    )

    return {
        "message": "Successfully followed user"
    }


@app.post("/unfollow")
async def unfollow_user(request: Request):
    user_token, _, _ = (
        require_authenticated_user(request)
    )

    data = await request.json()

    target_username = data.get("user_id")

    if not target_username:
        raise HTTPException(
            status_code=422,
            detail="Missing user_id in request body",
        )

    current_user_id = user_token["user_id"]

    unfollow_username(
        current_user_id,
        target_username,
    )

    return {
        "message": "Successfully unfollowed user"
    }


# ---------------------------------------------------------
# User profile
# ---------------------------------------------------------

def get_user_tweets(username):
    response = (
        firestore_db
        .collection("Tweet")
        .where(
            "username",
            "==",
            username,
        )
        .get()
    )

    tweet_list = []

    for tweet in response:
        data = tweet.to_dict()

        data["id"] = tweet.id

        tweet_date = data.get("date")

        if tweet_date:
            data["date"] = tweet_date.isoformat()

        tweet_list.append(data)

    tweet_list.sort(
        key=lambda tweet: tweet.get(
            "date",
            "",
        ),
        reverse=True,
    )

    return tweet_list[:10]


def get_user_by_id(user_id):
    user_ref = (
        firestore_db
        .collection("User")
        .document(user_id)
    )

    user_snapshot = user_ref.get()

    if not user_snapshot.exists:
        return None

    return user_snapshot.to_dict()


@app.get(
    "/user/{user_id}",
    response_class=HTMLResponse,
)
async def user_details(
    request: Request,
    user_id: str,
    token: str = Cookie(None),
):
    user_token = validate_firebase_token(token)

    if not user_token:
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    profile_user = get_user_by_id(user_id)

    if not profile_user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    username = profile_user.get("username")

    tweets_data = get_user_tweets(username)

    tweets_json = json.dumps(tweets_data)

    current_user_ref = get_user(user_token)

    current_user_data = (
        current_user_ref
        .get()
        .to_dict()
        or {}
    )

    followers = current_user_data.get(
        "followers",
        [],
    )

    current_user_id = current_user_data.get(
        "user_id"
    )

    return templates.TemplateResponse(
        "userDetails.html",
        {
            "request": request,
            "token": token,
            "userData": profile_user,
            "tweetList": tweets_json,
            "followers": followers,
            "userId": current_user_id,
        },
    )