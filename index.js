const functions = require('firebase-functions');
const admin = require('firebase-admin');
const nodemailer = require('nodemailer');

admin.initializeApp();

const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: "YOUR_EMAIL@gmail.com",
    pass: "YOUR_APP_PASSWORD"
  }
});

exports.sendWelcomeEmail = functions.auth.user().onCreate((user)=>{
  const mailOptions = {
    from: '"YK Team" <YOUR_EMAIL@gmail.com>',
    to: user.email,
    subject: "Welcome to the Platform 🎉",
    html: `<h2>Welcome!</h2><p>Thanks for registering.</p>`
  };
  return transporter.sendMail(mailOptions);
});