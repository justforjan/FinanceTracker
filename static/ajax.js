function changeMonthIndex(dir) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById('monthly_expenses').innerHTML = this.responseText;
    }
  };
  xhttp.open("GET", "/changeMonth/" + dir , true);
  xhttp.send();
}





function changeMonthCat(dir) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById('monthly_expenses').innerHTML = this.responseText;
    }
  };
  xhttp.open("GET", "/statistics/changeMonth/" + dir , true);
  xhttp.send();
}







function changeMonthTrip(dir) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById('monthly_expenses').innerHTML = this.responseText;
    }
  };
  xhttp.open("GET", "/trips/changeMonth/" + dir , true);
  xhttp.send();
}