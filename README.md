# Twitter Replica

A full-stack Twitter-inspired social media application built with **FastAPI**, **Firebase Authentication**, and **Cloud Firestore**.

The application allows users to create accounts, post tweets with optional images, follow other users, view profiles, search content, and manage their own tweets.

## Features

* User registration and login with Firebase Authentication
* Create tweets with optional image uploads
* Edit and delete your own tweets
* Follow and unfollow other users
* View user profiles and recent tweets
* Search users and tweet content
* Responsive interface built with HTML, CSS, JavaScript, and Bootstrap
* Cloud Firestore for storing users and tweets
* Local image storage for development

---

## Screenshots

### Login & Sign Up

<img width="1418" height="799" alt="Login page" src="https://github.com/user-attachments/assets/2d51f850-8ec5-406b-86a5-4b00097e2582" />


### Home Feed

<img width="1417" height="664" alt="Home page" src="https://github.com/user-attachments/assets/0cb4a6f5-836d-490c-a88e-1ffa76b70b23" />

### Create Tweet

<img width="1411" height="686" alt="Added tweet" src="https://github.com/user-attachments/assets/8d874854-d0a0-4b75-9ae7-d08cd2152f91" />

<img width="1402" height="753" alt="tweet wih image" src="https://github.com/user-attachments/assets/bdc332f9-467e-4f03-8ebc-0e3f3ec8dbd1" />


### Follow & Unfollow Users

<img width="1354" height="701" alt="Follow feature" src="https://github.com/user-attachments/assets/31d2488e-da2b-48fc-981f-b213938ffd26" />


### User Profile

<img width="1341" height="811" alt="User profile page" src="https://github.com/user-attachments/assets/e244f80f-e0db-4a4b-ab09-0c9e2aeeef86" />


---

## Tech Stack

### Backend

* Python 3
* FastAPI
* Uvicorn
* Jinja2

### Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap

### Database & Authentication

* Firebase Authentication
* Google Cloud Firestore

### Development Tools

* Git
* GitHub
* VS Code
* Google Cloud CLI

---

## Project Structure

```text
Twitter-Replica/
│
├── main.py
├── local_constants.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── home.html
│   ├── main.html
│   ├── userDetails.html
│   └── users.html
│
└── static/
    ├── firebase-login.js
    ├── styles.css
    └── uploads/
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/JoelMaju/Twitter-Replica.git
```

### 2. Navigate to the project

```bash
cd Twitter-Replica
```

### 3. Create a virtual environment

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows

```powershell
py -m venv .venv
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Firebase Setup

Create a Firebase project and enable:

* Firebase Authentication

  * Enable Email/Password sign-in
* Cloud Firestore

Update the Firebase web configuration in:

```text
static/firebase-login.js
```

Update the Google Cloud project configuration in:

```text
local_constants.py
```

Authenticate Google Cloud locally:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

---

## Running the Application

Start the FastAPI development server:

```bash
python -m uvicorn main:app --reload
```

Then open the application in your browser:

```text
http://127.0.0.1:8000
```

---

## Image Uploads

For local development, uploaded images are stored in:

```text
static/uploads/
```

Firebase Storage was originally used for image uploads. The project was later adapted to use local image storage for development without requiring a paid Google Cloud billing account.

Uploaded test images are excluded from Git using `.gitignore`.

---

## Development Challenges

While improving the project, I worked through several practical development challenges, including:

* Integrating Firebase Authentication with FastAPI
* Configuring Google Cloud Application Default Credentials
* Integrating Cloud Firestore
* Replacing Firebase Storage with local image uploads
* Fixing tweet rendering on user profile pages

---

## What I Learned

This project strengthened my understanding of:

* FastAPI routing and request handling
* Firebase Authentication
* Cloud Firestore
* File uploads in Python
* Frontend and backend integration
* Git and GitHub workflows
* Debugging full-stack web applications

---

## Future Improvements

* Like and comment functionality
* User profile pictures
* Pagination or infinite scrolling
* Improved form validation and error handling
* Automated testing
* Cloud deployment

---

## Author

**Joel Michael**

GitHub: https://github.com/JoelMaju
