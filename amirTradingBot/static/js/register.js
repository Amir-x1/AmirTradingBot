
const usernameField = document.querySelector("#usernameField");
const usernameErrorFiled = document.querySelector("#usernameErrorField");
const usernameCheckingFiled = document.querySelector("#usernameCheckingField");

const emailErrorFiled = document.querySelector("#emailErrorField");
const emailCheckingFiled = document.querySelector("#emailCheckingField");
const emailField = document.querySelector("#emailField");

const passwordField = document.querySelector("#passwordField");
const shortPasswordField = document.querySelector("#shortPasswordField");

const repeatPasswordField = document.querySelector("#repeatPasswordField");
const passwordErrorField = document.querySelector("#passwordErrorField");

const passwordVisibilityToggle = document.querySelector("#passwordVisibilityToggle");

const submitBtn = document.querySelector("#submitBtn");

var usernameOk = false;
var emailOk = false;
var passwordOk = false;



usernameField.addEventListener("keyup", (ev) => {
    const usernameVal = ev.target.value;
    console.log(usernameVal)
    usernameField.classList.remove("is-invalid");
    usernameErrorFiled.style.display = 'none';
    if(usernameVal.length > 0) {
        usernameCheckingFiled.style.display = 'block';
        fetch('/authentication/validate-username', {
            body: JSON.stringify({username: usernameVal}),
            method: "POST"
        })
            .then((res)=> res.json())
            .then((data)=>{
                usernameCheckingFiled.style.display = 'none';
                if(data.username_error){
                    usernameOk = false;
                    usernameErrorFiled.innerHTML = data.username_error;
                    usernameField.classList.add("is-invalid");
                    usernameErrorFiled.style.display = 'block';
                }else{
                    usernameOk = true;
                    if(passwordOk && usernameOk && emailOk){
                        submitBtn.disabled = false;
                    }
                }
            })
    }
})

emailField.addEventListener("keyup", (ev) => {
    const emailVal = ev.target.value;
    emailField.classList.remove("is-invalid");
    emailErrorFiled.style.display = 'none';
    if(emailVal.length > 0) {
        emailCheckingFiled.style.display = 'block';
        fetch('/authentication/validate-email', {
            body: JSON.stringify({email: emailVal}),
            method: "POST"
        })
            .then((res)=> res.json())
            .then((data)=>{
                emailCheckingFiled.style.display = 'none';
                if(data.email_error){
                    emailOk = false;
                    emailErrorFiled.innerHTML = data.email_error;
                    emailField.classList.add("is-invalid");
                    emailErrorFiled.style.display = 'block';
                }else{
                    emailOk = true;
                    if(passwordOk && usernameOk && emailOk){
                        submitBtn.disabled = false;
                    }
                }
            })
    }
})

function SamePass(ev){
    passwordField.classList.remove("is-invalid");
    shortPasswordField.style.display = 'none';
    if(document.querySelector("#repeatPasswordField").value === document.querySelector("#passwordField").value){
        repeatPasswordField.classList.remove("is-invalid");
        passwordErrorField.style.display = 'none';
        passwordOk = true;
        if(passwordOk && usernameOk && emailOk){
            submitBtn.disabled = false;
        }
    }else{
            passwordOk = false;
            repeatPasswordField.classList.add("is-invalid");
            passwordErrorField.style.display = 'block';
        }
    if(document.querySelector("#passwordField").value.length < 8){
        passwordField.classList.add("is-invalid");
        shortPasswordField.style.display = 'block';
    }
}

repeatPasswordField.addEventListener("keyup", (ev) => {
    SamePass(ev);
})

passwordField.addEventListener("keyup", (ev) => {
    SamePass(ev);
})

passwordVisibilityToggle.addEventListener("click", (e)=>{
    if(passwordVisibilityToggle.textContent==="SHOW"){
        passwordVisibilityToggle.textContent = "HIDE";
        passwordField.type = "text";
        repeatPasswordField.type = "text";
    }else if(passwordVisibilityToggle.textContent==="HIDE"){
        passwordVisibilityToggle.textContent = "SHOW";
        passwordField.type = "password";
        repeatPasswordField.type = "password";
    }
})