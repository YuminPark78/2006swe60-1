function storeTextileQuantity() {
    const quantity = document.getElementById('textileQuantity').value;

    // Check if quantity is valid
    if (quantity >= 10) {
        // Store the quantity in session storage
        sessionStorage.setItem("textileQuantity", quantity);
        return true; // Valid quantity
    } 
    else
    {
        return false;
    }
}

function selectMethod() {
    // This function can handle showing the drop-off and pick-up options
    const isValidQuantity = storeTextileQuantity();

    if (isValidQuantity) {
        window.location.href="textile2.html";
    }
    else
    {
        window.location.href="mappage.html"
    }
}

function selectDropOff() {
    // Assuming you handle the redirection to select the recycling location
    document.getElementById('qrCodeContainer').classList.remove('hidden');

    // Generate QR code based on the user's choice, if applicable
    // Update the src of the QR code based on the generated location
    document.getElementById('qrCode').src = "path/to/generated-qr-code.png"; // Change this to your QR code path
}

function redirectToRefash() {
    // Redirect to the Refash website
    window.location.href = "https://www.refash.com"; // Replace with the actual URL
}
