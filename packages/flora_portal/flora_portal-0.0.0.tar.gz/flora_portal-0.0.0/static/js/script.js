var sidenavShown = false;

$("#toggle-sidenav").click(function() {
  if (sidenavShown) {
    sidenavShown = false;
    $("#sidenav").css("width", "0");
  } else {
      sidenavShown = true;
    if ($(window).width() <= 400 ) {
      $("#sidenav").css("width", "100%");
    } else {
      $("#sidenav").css("width", "250px");
    }
  }
});

$("#close-sidenav").click(function() {
  sidenavShown = false;
  $("#sidenav").css("width", "0");
});

$(window).resize(function() {
  if (sidenavShown) {
    if ($(window).width() <= 400 ) {
      $("#sidenav").css("width", "100%");
    } else {
      $("#sidenav").css("width", "250px");
    }
  }
});


