submitButton = document.getElementById("submitButton");
submitButton.addEventListener("click", function(event){
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    console.log("Email",email);
    console.log("Password",password);
});