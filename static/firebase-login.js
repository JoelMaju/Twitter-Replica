"use strict";
// import firebase
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.6/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.6.6/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAQZZcaB_Q386W1b1x5l6b5f7XnYFawtvM",
  authDomain: "twitter-f6929.firebaseapp.com",
  projectId: "twitter-f6929",
  storageBucket: "twitter-f6929.appspot.com",
  messagingSenderId: "701186557667",
  appId: "1:701186557667:web:a18faac01263e30acd67d6"
};

window.addEventListener("load", function () {
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  updateUI(document.cookie);

  // login of a user to firebase
  document.getElementById("login").addEventListener("click", function () {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        // we have a signed in user
        const user = userCredential.user;
        console.log("logged in");

        // get the id token for the user who just logged in and force a redirect to home
        user.getIdToken().then((token) => {
          document.cookie = "token=" + token + ";path=/;SameSite=Strict";
        //   window.location = "/";
        window.location.href = "/home"
        });
      })

      .catch((error) => {
        // issue with signup that we will drop to console
        console.log(error.code + error.message);

        alert(error.message);
      });
  });

  // signup of a new user to firebase
  
  document.getElementById("sign-up").addEventListener("click", function () {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    createUserWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        // we have signed in user
        const user = userCredential.user;
        console.log("logged in");

        // get the id token for the user who just logged in and force a redirect to home
        user.getIdToken().then((token) => {
          document.cookie = "token=" + token + ";path=/;SameSite=Strict";
            alert("User Registered Successfully")
            window.location.reload();
        });
      })

      .catch((error) => {
        // issue with signup that we will drop to console
        console.log(error.code + error.message);
        alert(error.message);
      });
  });

  // sign-out from firebase
  document.getElementById("sign-out").addEventListener("click", function () {
    signOut(auth).then((output) => {
      // remove the ID token for the user and force a redirect to /
      document.cookie = "token=;path=/;SameSite=Strict";
      window.location = "/";
    });
  });
});



function updateUI(cookie) {
  var token = parseCookieToken(cookie);
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  if (token.length > 0) {
    document.getElementById("sign-out").hidden = false;
    
  } else {
    document.getElementById("sign-out").hidden = true;
  }
}

// function that will take the and will return the value associated with it to the caller
function parseCookieToken(cookie) {
  // split the cookie out on the basis of semi colon
  var strings = cookie.split(":");

  // go through each of strings
  for (let i = 0; i < strings.length; i++) {
    // split string based on = sign. if LHS is token then return RHS immediately
    var temp = strings[i].split("=");
    if (temp[0] == "token") return temp[1];
  }

  // if we got to this point then token wasn't in cookie so return empty string
  return "";
}
