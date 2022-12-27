const offcanvasMenu = document.querySelector('.offcanvas-menu')
const homearrow = document.getElementById("homearrow");
const myDIV = document.getElementById("myDIV");

function loading(){
    $("#staticLoadingModal").modal("show")
    $("#staticLoadingModal").style.display = 'block';
 }
 
 $(document).ready(function(){
    $("#staticLoadingModal").modal("hide")
 });



let animationFrameId = null;

window.onscroll = function () {
  // Cancel the current animation if it's still running
  if (animationFrameId) {
    window.cancelAnimationFrame(animationFrameId);
  }

  // Start a new animation
  animationFrameId = window.requestAnimationFrame(scrollFunction);
};

function scrollFunction() {
  // Reset the animation frame ID so we can start a new animation on the next scroll event
  animationFrameId = null;

  if (
    document.body.scrollTop > 150 ||
    document.documentElement.scrollTop > 150
  ) {
    homearrow.classList.add("show");
  } else {
    homearrow.classList.remove("show");
  }
}
