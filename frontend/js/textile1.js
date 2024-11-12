function storeTextileQuantity() {
    const quantity = document.getElementById('textileQuantity').value;
  
    if (Number.isInteger(Number(quantity))== false|| quantity <= 0)
        { alert("Quantity must be a whole number greater than 0"); 
            return false; 
        }

    if (quantity >= 10) {
     
        sessionStorage.setItem("textileQuantity", quantity);
        return true; 
    } 
    else
    {
        return false;
    }
}

function redirect() {
   
    const isValidQuantity = storeTextileQuantity();

    if (isValidQuantity) {
        window.location.href="textile2.html";
    }
    else
    {
        sessionStorage.setItem("textile","clothesbin");
        window.location.href="mappage.html"
    }
}


