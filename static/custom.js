//const AWS = require('aws-sdk');
//const AmazonCognitoIdentity = require('amazon-cognito-identity-js');

// Configure Amazon Cognito
var poolData = {
    UserPoolId: 'eu-north-1_3n4iDE5UW',
    Region: 'eu-north-1',
    ClientId: '23o6uajhrj1nkl02tgo8nkmju5'
};

var userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);


// Signup function
function signup() {
    var email = document.getElementById('email').value;
    var matricNumber = document.getElementById('matricNumber').value;
    var password = document.getElementById('password').value;
    var confirmPassword = document.getElementById('confirmPassword').value;

    // Check if passwords match
    if (password !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }

    // Check if matriculation number is valid
    var matricNumberPattern = /^U\d{4}\/\d{7}$/;
    if (!matricNumberPattern.test(matricNumber)) {
        alert('Please enter a valid matriculation number (e.g., U2015/3030002)');
        return;
    }

    // Use the correct route for the signup form submission
    var signupForm = document.getElementById('signupForm');
    signupForm.action = '/signup';  // Update the action attribute


    // Create a Cognito user
    var attributeList = [];
    var dataEmail = {
        Name: 'email',
        Value: email
    };
    var attributeEmail = new AmazonCognitoIdentity.CognitoUserAttribute(dataEmail);

    var dataMatricNumber = {
        Name: 'custom:matricNumber',
        Value: matricNumber
    };
    var attributeMatricNumber = new AmazonCognitoIdentity.CognitoUserAttribute(dataMatricNumber);
    
    attributeList.push(attributeEmail);
    attributeList.push(attributeMatricNumber);

    userPool.signUp(email, password, attributeList, null, function (err, result) {
        if (err) {
            alert(err.message || JSON.stringify(err));
            return;
        }
        var cognitoUser = result.user;
        console.log('user name is ' + cognitoUser.getUsername());
        alert('Signup successful. Please check your email for verification.');
    });
}

// Login function
function login() {
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;

    var authenticationData = {
        Username: email,
        Password: password,
    };
    
    var authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);

    var userData = {
        Username: email,
        Pool: userPool
    };

    var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: function (session) {
            console.log('Authentication successful', session);
            alert('Login successful');
            
            // Redirect to the home page
            window.location.href = "/"; // Change this to the URL of your home page
        },
        onFailure: function (err) {
            alert(err.message || JSON.stringify(err));
        },
        newPasswordRequired: function (userAttributes, requiredAttributes) {
            // User needs to set a new password
            alert('Please set a new password.');
            // Redirect or perform additional actions as needed
        }
    });

    // Prevent the default form submission
    return false;
}

