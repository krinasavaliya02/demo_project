$(document).ready(function () {

    $('#edit_profile_form').on('submit', function (e) {
        e.preventDefault();

        $('.error').html('');
        let username = $('#username').val().trim();
        let email = $('#email').val().trim();

        let isUsername = validateField('username', username)
        let isEmail = validateField('email', email)

        if (!isUsername || !isEmail) return;

        $.ajax({
            url: '/companies/edit-profile/',
            type: "PUT",
            headers: {
                "X-CSRFToken": $('input[name=csrfmiddlewaretoken]').val()
            },
            data: {
                username: username,
                email: email,
            },
            success: function (response) {
                if (response.code == 200) {
                    $('#edit_profile_form')[0].reset();
                    $('#message').html(
                        '<div class="alert alert-success">' +
                        '<strong>' + response.message + '</strong>' +
                        '</div>');

                    $('#message').hide().fadeIn();
                    $('#editProfileModel').modal('hide');

                    setTimeout(function () {
                        window.location.href = '/login/';
                    }, 500);
                }
                else {
                    let errors = response.data || [];
                    $('.error').html('');
                    errors.forEach(element => {
                        showError('#' + element.field, element.message)
                    })
                }
            }
        })
    })

    $('.btn-close').on('click', function () {
        $('.error').html('');
    })

    function validateField(type, value) {
        let isValid = true;
        if (value === '') {
            showError('#' + type, 'Please enter ' + type);
            isValid = false;
        }
        return isValid;
    }

    function showError(div, message) {
        $(div).closest('.mb-3').find('.error').html(message).css('color', 'red')
    }
})