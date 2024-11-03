function guide() {
	window.location.href="/guides/Recyclo_Guide_Textile.pdf";
}

function storeTextileQuantity() {
    const quantity = document.getElementById('textileQuantity').value;


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
        window.location.href="/textiles2";
    }
    else
    {
        sessionStorage.setItem("category","clothesbin");
        window.location.href="/map";
    }
}


