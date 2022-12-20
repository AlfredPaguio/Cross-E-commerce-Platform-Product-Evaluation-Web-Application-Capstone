const openBtn = document.querySelector('.open-btn');
const closeBtn = document.querySelector('.close-btn');
const offcanvasMenu = document.querySelector('.offcanvas-menu')
const homearrow = document.getElementById("homearrow");
const myDIV = document.getElementById("myDIV");

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
  var x = document.getElementById("password1");
  var y = document.getElementById("password2");

  var type = x.type === "password" ? "text" : "password";
  x.type = type;
  y.type = type;
}

function password_show_login() {

  var z = document.getElementById("passwordForm");
  z.type = z.type === "password" ? "text" : "password";
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

window.onscroll = function () {
  requestAnimationFrame(scrollFunction);
};

function scrollFunction() {
  if (
    document.body.scrollTop > 300 ||
    document.documentElement.scrollTop > 300
  ) {
    homearrow.classList.add("show");
  } else {
    homearrow.classList.remove("show");
  }
}
