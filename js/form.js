async function handleFormSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch(form.action, {
            method: form.method,
            body: formData
        });

        if (response.ok) {
            alert('Form submitted successfully.');
            window.location.href = '/';
        } else {
            alert('Form submission failed. Please try again.');
        }
    } catch (error) {
        console.error('Error submitting the form:', error);
        alert('An unexpected error occurred. Please try again later.');
    }
}