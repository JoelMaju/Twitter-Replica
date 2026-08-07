"use strict";

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.6/firebase-app.js";

import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.6.6/firebase-auth.js";


const firebaseConfig = {
  apiKey: "AIzaSyDVT1EjEtFLZ66xzMM9Bk9J72ahrDMR3EY",
  authDomain: "clean-terminal-414810.firebaseapp.com",
  projectId: "clean-terminal-414810",
  storageBucket: "clean-terminal-414810.appspot.com",
  messagingSenderId: "768883084765",
  appId: "1:768883084765:web:f5c5938ce8e7a6a7703a34",
};


const app = initializeApp(firebaseConfig);
const auth = getAuth(app);


document.addEventListener("DOMContentLoaded", function ()  {
  updateUI(document.cookie);

  const loginButton = document.getElementById("login");
  const signUpButton = document.getElementById("sign-up");
  const signOutButton = document.getElementById("sign-out");


  if (loginButton) {
    loginButton.addEventListener("click", loginUser);
  }


  if (signUpButton) {
    signUpButton.addEventListener("click", registerUser);
  }


  if (signOutButton) {
    signOutButton.addEventListener("click", logoutUser);
  }
});


async function loginUser() {
  const email = document
    .getElementById("email")
    .value
    .trim();

  const password = document
    .getElementById("password")
    .value;


  if (!email || !password) {
    alert("Please enter your email and password.");
    return;
  }


  try {
    const userCredential =
      await signInWithEmailAndPassword(
        auth,
        email,
        password
      );

    const token =
      await userCredential.user.getIdToken();

    setAuthCookie(token);

    window.location.href = "/home";

  } catch (error) {
    alert(getFriendlyAuthError(error.code));
  }
}


async function registerUser() {
  const email = document
    .getElementById("email")
    .value
    .trim();

  const password = document
    .getElementById("password")
    .value;


  if (!email || !password) {
    alert("Please enter your email and password.");
    return;
  }


  try {
    const userCredential =
      await createUserWithEmailAndPassword(
        auth,
        email,
        password
      );

    const token =
      await userCredential.user.getIdToken();

    setAuthCookie(token);

    alert("Account created successfully.");

    window.location.href = "/home";

  } catch (error) {
    alert(getFriendlyAuthError(error.code));
  }
}


async function logoutUser() {
  try {
    await signOut(auth);

    clearAuthCookie();

    window.location.href = "/";

  } catch (error) {
    alert("Unable to sign out. Please try again.");
  }
}


function setAuthCookie(token) {
  document.cookie =
    `token=${token}; path=/; SameSite=Strict`;
}


function clearAuthCookie() {
  document.cookie =
    "token=; path=/; Max-Age=0; SameSite=Strict";
}


function updateUI(cookie) {
  const token = parseCookieToken(cookie);

  const signOutButton =
    document.getElementById("sign-out");

  if (!signOutButton) {
    return;
  }

  signOutButton.hidden = !token;
}


function parseCookieToken(cookie) {
  const cookies = cookie.split(";");

  for (const item of cookies) {
    const [name, ...valueParts] =
      item.trim().split("=");

    if (name === "token") {
      return valueParts.join("=");
    }
  }

  return "";
}


function getFriendlyAuthError(errorCode) {
  switch (errorCode) {
    case "auth/invalid-email":
      return "Please enter a valid email address.";

    case "auth/missing-password":
      return "Please enter your password.";

    case "auth/weak-password":
      return "Password should be at least 6 characters.";

    case "auth/email-already-in-use":
      return "An account already exists with this email.";

    case "auth/user-not-found":
    case "auth/wrong-password":
    case "auth/invalid-login-credentials":
    case "auth/invalid-credential":
      return "Invalid email or password.";

    case "auth/too-many-requests":
      return "Too many attempts. Please try again later.";

    default:
      return "Authentication failed. Please try again.";
  }
}