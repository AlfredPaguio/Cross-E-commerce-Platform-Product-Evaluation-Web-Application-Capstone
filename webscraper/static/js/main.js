const openBtn = document.querySelector('.open-btn');
const closeBtn = document.querySelector('.close-btn');
const offcanvasMenu = document.querySelector('.offcanvas-menu')

openBtn.addEventListener('click', function(e) {
    e.preventDefault();
    offcanvasMenu.classList.add('active');
});

closeBtn.addEventListener('click', function (e) {
    e.preventDefault();
    offcanvasMenu.classList.remove('active');
});

function loading(){
    $("#staticLoadingModal").modal("show")
    $("#staticLoadingModal").style.display = 'block';
 }
 
 $(document).ready(function(){
    $("#staticLoadingModal").modal("hide")
 });

function password_show_register() {
  //register page
  var x = document.getElementById("password1");
  var y = document.getElementById("password2");

  if (x.type === "password" && y.type === "password") {
    x.type = "text";
    y.type = "text";
  } else {
    x.type = "password";
    y.type = "password";
  }
}

function password_show_login() {
  //login page
  var z = document.getElementById("password");

  if (z.type === "password") {
    z.type = "text";
  } else {
    z.type = "password";
  }
}

function password_show_account() {
  //register page
  var x = document.getElementById("old_password");
  var y = document.getElementById("new_password");
  var z = document.getElementById("confirm_new_password");

  if (x.type === "password" && y.type === "password" && z.type === "password") {
    x.type = "text";
    y.type = "text";
    z.type = "text";
  } else {
    x.type = "password";
    y.type = "password";
    z.type = "password";
  }
}

