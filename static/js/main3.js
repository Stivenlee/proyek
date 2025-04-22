const passwordInput = document.getElementById("password");
const togglePassword = document.getElementById("toggle-password");

togglePassword.addEventListener("click", function () {
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    this.textContent = "Sembunyikan Password";
  } else {
    passwordInput.type = "password";
    this.textContent = "Tunjukkan Password";
  }
});

document.getElementById("signin-form").addEventListener("submit", function () {
  
});


