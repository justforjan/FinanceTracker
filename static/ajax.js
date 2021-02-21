
/*
var prev_month = document.getElementById("prev_month");

prev_month.addEventListener("click", function(){
    $.ajax({
        url: "/changeToPrevMonth",
        type: "POST",
        dataType: "json",
        success: function(data){
            $(monthly_expenses).replace(data)
        };
    });
});
*/

/*
{

    var ajax = new XMLHttpRequest();

    ajax.open('GET', , true);
    ajax.onload = function() {

    }

});
*/

/*
function update_monthly_expenses()
{
    var ajax = new XMLHttpRequest();

    ajax. = function() {

    };

    ajax.open('GET', , true);
    ajax.send();
}
*/


/*
function changeToPrevMonth() {
    $.ajax({
        url: "/changeToPrevMonth",
        type: "POST",
        dataType: "json",
        success: function(data){
            document.getElementById('monthly_expenses').replace(data)
        }
    });
}
*/

function changeToPrevMonth() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById('monthly_expenses').innerHTML = this.responseText;
    }
  };
  xhttp.open("GET", "/changeToPrevMonth" , true);
  xhttp.send();
}

function changeToNextMonth() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById('monthly_expenses').innerHTML = this.responseText;
    }
  };
  xhttp.open("GET", "/changeToNextMonth" , true);
  xhttp.send();
}
