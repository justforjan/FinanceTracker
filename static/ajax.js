
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



function changeToPrevMonth() {
    $.ajax({
        url: "/changeToPrevMonth",
        type: "POST",
        dataType: "json",
        success: function(data){
            $('monthly_expenses').replace(data)
        }
    });
}
