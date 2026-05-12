$(document).ready(function () {

    $('#login_form').on('submit', function (e) {
        e.preventDefault();
        $('.error').html('');
        let username = $('#username').val().trim();
        let password = $('#password').val().trim();

        let isusername = validateAuthField('username', username)
        let ispassword = validateAuthField('password', password, 'login')

        if (!isusername || !ispassword) return;

        $.ajax({
            url: '/login/',
            type: "POST",
            data: {
                username: username,
                password: password,
                next: $('#next').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (response) {
                console.log(response)
                $(".error").text("");
                if (response.code == 200) {
                    $('#login_form')[0].reset();
                    window.location.href = response.data.redirect_url;
                }
                else {
                    let errors = response.data || [];
                    errors.forEach(element => {
                        showError('#' + element.field, element.message)
                    })
                }
            }
        })
    })

    $('#register_form').on('submit', function (e) {
        e.preventDefault();
        $('.error').html('');
        let username = $('#username').val().trim();
        let email = $('#email').val().trim();
        let password = $('#password').val().trim();
        let confirmpassword = $('#confirmpassword').val().trim();

        let isusername = validateAuthField('username', username)
        let isemail = validateAuthField('email', email)
        let ispassword = validateAuthField('password', password, 'register')
        let isconfirmpassword = validateAuthField('confirmpassword', confirmpassword)

        if (!isusername || !isemail || !ispassword || !isconfirmpassword) return;

        $.ajax({
            url: '/register/',
            type: "POST",
            data: {
                username: username,
                email: email,
                password: password,
                confirmpassword: confirmpassword,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (response) {
                console.log(response)
                $(".error").text("");
                if (response.code == 200) {
                    $('#register_form')[0].reset();
                    $('#message').html(
                        '<div class="alert alert-success">' +
                        '<strong>' + response.message + '</strong>' +
                        '</div>');

                    $('#message').hide().fadeIn();
                    $('#message').show().delay(1000).fadeOut(400, function () {
                        window.location.href = '/login/';
                    });
                }
                else {
                    let errors = response.data || [];
                    errors.forEach(element => {
                        showError('#' + element.field, element.message)
                    })
                }
            }
        })
    })


    function validateAuthField(type, value, formType) {
        let isValid = true;

        if (type == 'username') {
            if (value === '') {
                showError($('#username'), 'Please enter username');
                isValid = false;
            }
        }

        if (type == 'email') {
            let emailptn = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
            if (value === '') {
                showError($('#email'), 'Please enter email');
                isValid = false;
            }
            else if (!emailptn.test(value)) {
                showError($('#email'), 'Enter valid email (Ex.john@gmail.com)');
                isValid = false;
            }
        }

        if (type == 'password') {
            if (value === '') {
                showError($('#password'), 'Please enter password');
                isValid = false;
            }
            else if (formType == 'register' && value.length < 8) {
                showError($('#password'), 'Password must be at least 8 characters long');
                isValid = false;
            }
        }

        if (type == 'confirmpassword') {
            if (value === '') {
                showError($('#confirmpassword'), 'Please enter confirmpassword');
                isValid = false;
            }
            else if (password.value !== value) {
                showError($('#confirmpassword'), 'Passwords do not match');
                isValid = false;
            }
        }
        return isValid;
    }

    function showError(div, message) {
        $(div).closest('.mb-3').find('.error').html(message).css('color', 'red')
    }
})