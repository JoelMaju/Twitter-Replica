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
  appId: "1:768883084765:web:f5c5938ce8e7a6a7703a34"
};

window.addEventListener("load", function () {
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  updateUI(document.cookie);

  
  document.getElementById("login").addEventListener("click", function () {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        const user = userCredential.user;
        console.log("logged in");

        user.getIdToken().then((token) => {
          document.cookie = "token=" + token + ";path=/;SameSite=Strict";
       
        window.location.href = "/home"
        });
      })

      .catch((error) => {
       
        console.log(error.code + error.message);

        alert(error.message);
      });
  });

  
  
  document.getElementById("sign-up").addEventListener("click", function () {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    createUserWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        
        const user = userCredential.user;
        console.log("logged in");

        
        user.getIdToken().then((token) => {
          document.cookie = "token=" + token + ";path=/;SameSite=Strict";
            alert("User Registered Successfully")
            window.location.reload();
        });
      })

      .catch((error) => {
       
        console.log(error.code + error.message);
        alert(error.message);
      });
  });

  
  document.getElementById("sign-out").addEventListener("click", function () {
    signOut(auth).then((output) => {
     
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


function parseCookieToken(cookie) {
  
  var strings = cookie.split(":");

  
  for (let i = 0; i < strings.length; i++) {
   
    var temp = strings[i].split("=");
    if (temp[0] == "token") return temp[1];
  }

  return "";
}
