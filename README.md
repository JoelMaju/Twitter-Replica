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

<img width="1340" height="721" alt="Login and signup page" src="https://github.com/user-attachments/assets/a2fad37f-b56e-4549-ba90-98dc492ad86b" />



### Home Feed
<img width="1402" height="686" alt="Home page" src="https://github.com/user-attachments/assets/13b3f4ad-232a-4192-9fde-b1c800f5b59f" />


### Create Tweet

<img width="1349" height="691" alt="Add tweet" src="https://github.com/user-attachments/assets/7650747a-c30d-4a15-a988-2a168d14bf4e" />



### Follow & Unfollow Users

<img width="1314" height="764" alt="Unfollow users" src="https://github.com/user-attachments/assets/af4fb9dc-f254-4370-bb57-92bdc5ec27d2" />
<img width="1268" height="766" alt="Follow users" src="https://github.com/user-attachments/assets/e3d1c10a-8cc9-4dc0-9f80-bf64988302fe" />




### User Profile

<img width="1286" height="808" alt="user profile" src="https://github.com/user-attachments/assets/71217228-bec5-4acd-ba07-bc462bfcfd66" />



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
