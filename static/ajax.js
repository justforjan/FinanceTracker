
function changeToPrevMonth() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById('monthly_expenses').innerHTML = this.responseText;
      console.log(this.responseText);
    }
  };
  xhttp.open("GET", "/changeToPrevMonth" , true);
  console.log(xhttp);
  xhttp.send();
}

function changeToNextMonth() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById('monthly_expenses').innerHTML = this.responseText;
      console.log(this.responseText);
    }
  };
  xhttp.open("GET", "/changeToNextMonth" , true);
  console.log(xhttp);
  xhttp.send();
}




function changeToPrevMonthStat() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById('monthly_statistics').innerHTML = this.responseText;
      console.log(this.responseText);
    }
  };
  xhttp.open("GET", "/changeToPrevMonthStat" , true);
  console.log(xhttp);
  xhttp.send();
}

function changeToNextMonthStat() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById('monthly_statistics').innerHTML = this.responseText;
      console.log(this.responseText);
    }
  };
  xhttp.open("GET", "/changeToNextMonthStat" , true);
  console.log(xhttp);
  xhttp.send();
}
