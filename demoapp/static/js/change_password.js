$(document).ready(function () {

    $('#update_password').on('submit', function (e) {
        e.preventDefault();
        $('.error').html('');

        let current_password = $('#current_password').val().trim();
        let new_password = $('#new_password').val().trim();
        let confirm_password = $('#confirm_password').val().trim();

        let isCurrentPassword = validateField('current_password', current_password)
        let isNewPassword = validateField('new_password', new_password)
        let isConfirmPassword = validateField('confirm_password', confirm_password)

        if (!isCurrentPassword || !isNewPassword || !isConfirmPassword) return;

        $.ajax({
            url: '/companies/change-password/',
            type: "POST",
            headers: {
                "X-CSRFToken": $('input[name=csrfmiddlewaretoken]').val()
            },
            data: {
                current_password: current_password,
                new_password: new_password,
                confirm_password: confirm_password,
            },
            success: function (response) {
                console.log(response)
                if (response.code === 200) {
                    $('#message').html(
                        '<div class="alert alert-success">' +
                        '<strong>' + response.message + '</strong>' +
                        '</div>');

                    $('#message').hide().fadeIn();
                    $('#passwordModel').modal('hide');

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
        console.log("----------", type, ">>>>>>>>>>>", value)
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