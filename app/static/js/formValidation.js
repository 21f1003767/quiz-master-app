// Form Validation
document.addEventListener('DOMContentLoaded', function() {
    // Get all forms with the class 'needs-validation'
    const forms = document.querySelectorAll('.needs-validation');
    
    // Email validation regex pattern
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    
    // Password strength validation (at least 6 chars, with at least one number and one uppercase letter)
    const passwordStrengthPattern = /^(?=.*[A-Z])(?=.*\d).{6,}$/;
    
    // Custom validation messages
    const messages = {
        required: 'This field is required',
        email: 'Please enter a valid email address',
        passwordMatch: 'Passwords do not match',
        passwordStrength: 'Password must be at least 6 characters with at least one number and one uppercase letter',
        dateOfBirth: 'Please enter a valid date of birth (you must be at least 12 years old)',
        fullName: 'Please enter your full name (first and last name)'
    };
    
    // Loop over forms and add validation
    Array.from(forms).forEach(form => {
        // Add submit event listener
        form.addEventListener('submit', function(event) {
            let formIsValid = true;
            
            // Email validation
            const emailInput = form.querySelector('input[name="username"]');
            if (emailInput) {
                // Check if empty
                if (!emailInput.value.trim()) {
                    setInvalid(emailInput, messages.required);
                    formIsValid = false;
                }
                // Check email format
                else if (!emailPattern.test(emailInput.value.trim())) {
                    setInvalid(emailInput, messages.email);
                    formIsValid = false;
                } else {
                    setValid(emailInput);
                }
            }
            
            // Password validation
            const passwordInput = form.querySelector('input[name="password"]');
            if (passwordInput) {
                // Check if empty
                if (!passwordInput.value) {
                    setInvalid(passwordInput, messages.required);
                    formIsValid = false;
                }
                // Check password strength on registration form
                else if (form.id === 'registerForm' && !passwordStrengthPattern.test(passwordInput.value)) {
                    setInvalid(passwordInput, messages.passwordStrength);
                    formIsValid = false;
                } else {
                    setValid(passwordInput);
                }
                
                // Confirm password validation (only for registration)
                const confirmPasswordInput = form.querySelector('input[name="confirm_password"]');
                if (confirmPasswordInput) {
                    if (!confirmPasswordInput.value) {
                        setInvalid(confirmPasswordInput, messages.required);
                        formIsValid = false;
                    } else if (confirmPasswordInput.value !== passwordInput.value) {
                        setInvalid(confirmPasswordInput, messages.passwordMatch);
                        formIsValid = false;
                    } else {
                        setValid(confirmPasswordInput);
                    }
                }
            }
            
            // Full name validation
            const fullNameInput = form.querySelector('input[name="full_name"]');
            if (fullNameInput) {
                const fullName = fullNameInput.value.trim();
                if (!fullName) {
                    setInvalid(fullNameInput, messages.required);
                    formIsValid = false;
                } else if (fullName.split(' ').length < 2) {
                    setInvalid(fullNameInput, messages.fullName);
                    formIsValid = false;
                } else {
                    setValid(fullNameInput);
                }
            }
            
            // Qualification validation (just required)
            const qualificationInput = form.querySelector('input[name="qualification"]');
            if (qualificationInput) {
                if (!qualificationInput.value.trim()) {
                    setInvalid(qualificationInput, messages.required);
                    formIsValid = false;
                } else {
                    setValid(qualificationInput);
                }
            }
            
            // Date of birth validation
            const dobInput = form.querySelector('input[name="dob"]');
            if (dobInput) {
                if (!dobInput.value) {
                    setInvalid(dobInput, messages.required);
                    formIsValid = false;
                } else {
                    const dobDate = new Date(dobInput.value);
                    const today = new Date();
                    const minDate = new Date();
                    minDate.setFullYear(today.getFullYear() - 12); // Must be at least 12 years old
                    
                    if (isNaN(dobDate.getTime()) || dobDate > today || dobDate > minDate) {
                        setInvalid(dobInput, messages.dateOfBirth);
                        formIsValid = false;
                    } else {
                        setValid(dobInput);
                    }
                }
            }
            
            // If form is not valid, prevent submission
            if (!formIsValid) {
                event.preventDefault();
                event.stopPropagation();
            }
        }, false);
        
        // Add real-time validation feedback on input
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                // Clear validation state when user starts typing again
                input.classList.remove('is-invalid');
                input.classList.remove('is-valid');
                
                // Get the feedback element
                const feedback = input.nextElementSibling;
                if (feedback && feedback.classList.contains('invalid-feedback')) {
                    feedback.textContent = '';
                }
            });
        });
    });
    
    // Password strength meter (for registration form)
    const passwordInput = document.querySelector('#registerForm input[name="password"]');
    if (passwordInput) {
        const strengthMeter = document.createElement('div');
        strengthMeter.className = 'password-strength-meter mt-1';
        strengthMeter.innerHTML = `
            <div class="progress" style="height: 5px;">
                <div class="progress-bar" role="progressbar" style="width: 0%"></div>
            </div>
            <small class="text-muted mt-1 d-block">Password strength: <span class="strength-text">Not entered</span></small>
        `;
        
        // Insert after the password input
        passwordInput.parentNode.insertBefore(strengthMeter, passwordInput.nextSibling);
        
        // Update strength meter on input
        passwordInput.addEventListener('input', function() {
            updatePasswordStrength(passwordInput.value, strengthMeter);
        });
    }
    
    // Helper functions
    function setInvalid(input, message) {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        
        // Find or create the feedback element
        let feedback = input.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            input.parentNode.insertBefore(feedback, input.nextSibling);
        }
        
        feedback.textContent = message;
    }
    
    function setValid(input) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    }
    
    function updatePasswordStrength(password, meterElement) {
        let strength = 0;
        let feedback = 'Not entered';
        
        if (password.length > 0) {
            strength += 20;
            feedback = 'Very weak';
        }
        
        if (password.length >= 6) {
            strength += 20;
            feedback = 'Weak';
        }
        
        if (password.match(/[A-Z]/)) {
            strength += 20;
            feedback = 'Medium';
        }
        
        if (password.match(/[0-9]/)) {
            strength += 20;
            feedback = 'Strong';
        }
        
        if (password.match(/[^A-Za-z0-9]/)) {
            strength += 20;
            feedback = 'Very strong';
        }
        
        // Update the UI
        const progressBar = meterElement.querySelector('.progress-bar');
        const strengthText = meterElement.querySelector('.strength-text');
        
        progressBar.style.width = strength + '%';
        strengthText.textContent = feedback;
        
        // Change color based on strength
        progressBar.className = 'progress-bar';
        if (strength <= 40) {
            progressBar.classList.add('bg-danger');
        } else if (strength <= 60) {
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.add('bg-success');
        }
    }
}); 