$(document).ready(function(){

    function countCompany() {

        if($('#countCompany').length == 0) return;
        $.ajax({
            url: '/dashboard/',
            type: 'GET',
            success: function (response) {
                $('#countCompany').text(response.data.total)
            }
        })
    }
    countCompany()
})