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

function lookup(id) {
 console.log(id);
 //console.log(transactions);
 for (var i = 0; i < length; i++ ) {
   if (allTransactions[i].id == id) {
     if (allTransactions[i].exp == 1){
       document.getElementById('editExpAmount').value = allTransactions[i].amount;
       document.getElementById('editExpNotes').value = allTransactions[i].notes;
       document.getElementById('editExpDate').value = allTransactions[i].timestamp;
       document.getElementById('editExpTrip').value = allTransactions[i].trip_id;
       document.getElementById('editExpCategory').value = allTransactions[i].expCategory_id;
       document.getElementById('editExpId').value = allTransactions[i].id;
     } else {
       document.getElementById('editIncAmount').value = allTransactions[i].amount;
       document.getElementById('editIncNotes').value = allTransactions[i].notes;
       document.getElementById('editIncDate').value = allTransactions[i].timestamp;
       document.getElementById('editIncId').value = allTransactions[i].id;
     }
   };
 };
};

function deleteTransaction(id) {
 document.getElementById("deleteId").value = id
}