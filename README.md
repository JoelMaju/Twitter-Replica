# Twitter-Replica
# 🐦 Twitter Clone – FastAPI + Firebase + Google Cloud

A full-stack Twitter-like social media backend built using **FastAPI**, **Firebase Authentication**, **Google Firestore**, and **Google Cloud Storage**.  
This project simulates core social media functionalities such as posting tweets, following users, and media uploads.

---

## 🚀 Features

### 👤 User System
- Firebase Authentication integration
- Automatic user creation on first login
- Username setup and uniqueness validation

### 📝 Tweet System
- Create tweets (max 140 characters)
- Upload images with tweets
- Edit and delete tweets
- View timeline feed (latest tweets first)

### 🔁 Social Features
- Follow / Unfollow users
- Personalized feed based on followers
- View user profiles and their tweets

### ☁️ Cloud Integration
- Google Firestore for database storage
- Google Cloud Storage for image uploads
- Secure file handling using temporary storage

---

## 🏗️ Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** Google Firestore (NoSQL)
- **Authentication:** Firebase Auth (ID Token verification)
- **Storage:** Google Cloud Storage
- **Frontend:** Jinja2 Templates (HTML)
- **Hosting Ready:** Cloud Run / App Engine compatible

---

## 📁 Project Structure

---

## ⚙️ Installation & Setup

### 1. Clone repository
git clone https://github.com/JoelMaju/Twitter-Replica.git
cd Twitter-Replica

## Create Virtual Enviornment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

## Install requirements
pip install -r requirements.txt

## Configure Firebase & Google Cloud

PROJECT_NAME = "your-gcp-project-id"
PROJECT_STORAGE_BUCKET = "your-bucket-name"

## Run the application
uvicorn main:app --reload
