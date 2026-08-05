# Twitter Replica

A full-stack Twitter-inspired social media application built with **FastAPI**, **Firebase Authentication**, and **Cloud Firestore**. Users can create an account, post tweets with images, follow other users, and manage their own content through a clean web interface.

## Features

* User registration and login using Firebase Authentication
* Create tweets with optional image uploads
* Edit and delete your own tweets
* Follow and unfollow other users
* View user profiles and their recent tweets
* Responsive web interface using HTML, CSS, and JavaScript
* Cloud Firestore integration for storing users and tweets
* Local image storage for development without requiring Firebase Storage billing

---

## Tech Stack

### Backend

* Python 3
* FastAPI
* Uvicorn

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

### Database & Authentication

* Firebase Authentication
* Google Cloud Firestore

### Development Tools

* Git
* GitHub
* VS Code

---

## Project Structure

Twitter-Replica/
│
├── main.py
├── local_constants.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── home.html
│   ├── main.html
│   ├── userDetails.html
│   └── users.html
│
├── static/
│   ├── firebase-login.js
│   ├── styles.css
│   └── uploads/
│
└── .gitignore

---

## Installation

### 1. Clone the repository

bash
git clone https://github.com/JoelMaju/Twitter-Replica.git

### 2. Navigate to the project

bash
cd Twitter-Replica


### 3. Create a virtual environment

#### macOS / Linux

bash
python3 -m venv .venv
source .venv/bin/activate


#### Windows

powershell
py -m venv .venv
.venv\Scripts\activate


### 4. Install dependencies

bash
pip install -r requirements.txt


### 5. Configure Firebase

Create a Firebase project and enable:

* Firebase Authentication (Email/Password)
* Cloud Firestore

Update the Firebase configuration in:

static/firebase-login.js


Update the project settings in:


local_constants.py


Authenticate Google Cloud locally:

bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID


---

## Running the Application

Start the development server:

bash
python -m uvicorn main:app --reload


Open your browser and visit:

http://127.0.0.1:8000


---

## Image Uploads

For local development, uploaded images are stored in:


static/uploads/


This project uses local image storage instead of Firebase Storage to avoid requiring a Google Cloud billing account during development.

---

## Challenges Solved

During development, several improvements and fixes were implemented:

* Configured Firebase Authentication with FastAPI
* Integrated Google Cloud Firestore
* Fixed Google Cloud authentication (Application Default Credentials)
* Corrected Google Cloud Storage client initialization
* Replaced Firebase Storage uploads with local image storage
* Fixed tweet rendering on user profile pages
* Improved Git repository structure using `.gitignore`
* Cleaned project configuration for local development

---

## Future Improvements

* Like and unlike tweets
* Comment functionality
* Search users and tweets
* User profile pictures
* Pagination for tweet feeds
* Deploy the application using Docker and Google Cloud Run
* CI/CD with GitHub Actions

---

## Learning Outcomes

This project helped strengthen my understanding of:

* RESTful web application development
* FastAPI routing and request handling
* Firebase Authentication
* Cloud Firestore integration
* File upload handling in Python
* Git and GitHub workflows
* Debugging and troubleshooting full-stack applications

---

## Author

Joel Michael

GitHub: https://github.com/JoelMaju

