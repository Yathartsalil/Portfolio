// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDCHknoyleRF93F-5RVCgEupD94q6FfSVY",
  authDomain: "portfolio-53c0c.firebaseapp.com",
  projectId: "portfolio-53c0c",
  storageBucket: "portfolio-53c0c.firebasestorage.app",
  messagingSenderId: "350937409740",
  appId: "1:350937409740:web:79fd9941e23187504dfa69",
  measurementId: "G-2DYXTGBZS5"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);