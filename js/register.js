
async function onSubmit(event){
	event.preventDefault();
	const lowerCase = /(?=.*[a-z])/;
	const upperCase = /(?=.*[A-Z])/;
	const digit = /(?=.*\d)/;
	const specialCharacter = /(?=.*[@$!%*?&])/;
	const minLength = /.{8,}/;
	const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
	const confirmpassword = document.getElementById("confirmpassword").value;
	const email = document.getElementById("email").value;
	if (password != confirmpassword) {
		alert("Passwords do not match!");
		return;
	}
	if (!lowerCase.test(password) || !upperCase.test(password) || !digit.test(password) || !specialCharacter.test(password) || !minLength.test(password)) {
		const results = {
			lowerCase: lowerCase.test(password) ? '✓' : '✗',
			upperCase: upperCase.test(password) ? '✓' : '✗',
			digit: digit.test(password) ? '✓' : '✗',
			specialCharacter: specialCharacter.test(password) ? '✓' : '✗',
			minLength: minLength.test(password) ? '✓' : '✗'
		};
		alert(`Password does not meet the requirement.
	One Lowercase Letter: ${results.lowerCase}
	One Uppercase Letter: ${results.upperCase}
	One Number: ${results.digit}
	One Special Character: ${results.specialCharacter}
	Minimum Length (8 characters): ${results.minLength}`);
		return;
	}
	console.log("Starting handshake");
    const aesKey = await startup();
    console.log("Completed handshake");
    const sessionID = sessionStorage.getItem("sessionID");
    const {ciphertext, iv} = await encrypt(aesKey, password);
    const payload = {
        sessionid: sessionID,
        username: username, // Send the username as a string
        ciphertext: ciphertext, // Convert ciphertext to base64
        iv: iv, // Convert IV to base64
		email: email
    };
    let response = await fetch('/registerProcess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }, // JSON content type
        body: JSON.stringify(payload) // Convert payload to JSON
    });
    if (response.ok) {
        const result = await response.json();
        if (result.success) {
            alert(result.message);
            window.location.href = '/login';
        } else {
            alert(result.message);
        }
    } else {
        const result = await response.json();
		alert(result.message);
    }
}