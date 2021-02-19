function passBuyString(symbol){
    window.localStorage.setItem("buy_symbol", symbol);
}

function passSellString(symbol){
    window.localStorage.setItem("sell_symbol", symbol);
}

function buyString(){
    document.getElementById("buy").value =
        window.localStorage.getItem("buy_symbol");
}

function sellString(){
    document.getElementById("sell").value =
        window.localStorage.getItem("sell_symbol");
}

function clearForm(){
    window.localStorage.clear();
}


$(function () {
  $('[data-toggle="popover"]').popover()
})

Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});

$(document).ready( function() {
    $('#expDate').val(new Date().toDateInputValue());
    $('#incDate').val(new Date().toDateInputValue());
});