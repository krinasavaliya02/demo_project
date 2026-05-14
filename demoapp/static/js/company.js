$(document).ready(function () {

    function disableDeleteButton() {
        let count = $('.project-block').length;
        $('.remove-project-btn').prop('disabled', count == 1);
    }

    $(document).on('click', '.add-project-btn', function () {

        let row = `
        <div class="project-block border border-2 rounded p-3 shadow-sm mb-3">

            <div class="text-end">
                <button type="button" class="btn btn-outline-danger btn-sm remove-project-btn">
                    <i class="fa-regular fa-trash-can"></i> Delete
                </button>
            </div>

            <div class="row mt-3">
                <div class="col-sm-3">
                    <label>Project Name:</label>
                </div>
                <div class="col-sm-9">
                    <input type="text" name="project_name" class="project_name form-control" placeholder="Enter project name">
                    <p class="error"></p>
                </div>
            </div>

            <div class="row mt-1">
                <div class="col-sm-3">
                    <label>Technology:</label>
                </div>
                <div class="col-sm-9">
                    <input type="text" name="technology" class="technology form-control"
                        placeholder="Enter technology">
                    <p class="error"></p>
                </div>
            </div>

            <div class="row mt-1">
                <div class="col-sm-3">
                    <label>Status:</label>
                </div>
                <div class="col-sm-9">
                    <select name="status" class="status form-select">
                        <option value="">Select Option</option>
                        <option value="PENDING">Pending</option>
                        <option value="ONGOING">Ongoing</option>
                        <option value="COMPLETED">Completed</option>
                        <option value="CLOSED">Closed</option>
                        <option value="CANCELLED">Cancelled</option>
                    </select>
                    <p class="error"></p>
                </div>
            </div>

        </div>
        `;
        $('#project_container').append(row);
        disableDeleteButton();
    });

    $(document).on('click', '.remove-project-btn', function () {

        if ($('.project-block').length > 1) {
            $(this).closest('.project-block').remove();
        }
        disableDeleteButton();
    });

    $('#form').on('submit', function (e) {
        e.preventDefault();
        let company_id = $('#company_id').val();
        let company_name = $('#company_name').val().trim();
        let email = $('#email').val().trim();
        let phone = $('#phone').val().trim();
        let address = $('#address').val().trim();
        let is_active = $('#statusSwitch').is(':checked');

        let projects = []

        let project_name = $('.project_name').val().trim();
        let technology = $('.technology').val().trim();
        let status = $('.status').val();

        $('.project-block').each(function () {

            let project_name = $(this).find('.project_name').val().trim();
            let technology = $(this).find('.technology').val().trim();
            let status = $(this).find('.status').val();

            let project = {
                project_name: project_name,
                technology: technology,
                status: status
            };

            projects.push(project);
        });

        if (!formValidation(company_name, email, phone, address, project_name, technology, status)) {
            return;
        }

        let url = '';
        let method = '';

        if (company_id) {
            url = `/companies/${company_id}/edit/`;
            method = "PUT";
        }
        else {
            url = "/companies/new/";
            method = "POST";
        }

        $.ajax({
            url: url,
            type: method,
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            data: {
                name: company_name,
                email: email,
                phone: phone,
                address: address,
                is_active: is_active,
                projects: JSON.stringify(projects),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (response) {
                $(".error").text("");
                if (response.code == 200) {
                    $('#form')[0].reset();
                    $('#message').html(
                        '<div class="alert alert-success">' +
                        '<strong>' + response.message + '</strong>' +
                        '</div>');

                    $('#message').hide().fadeIn();
                    $('#message').show().delay(1000).fadeOut(400, function () {
                        window.location.href = '/companies/';
                    });
                }
                else {
                    let errors = response.data || {};
                    $(".error").text("");
                    if (errors.company) {
                        errors.company.forEach(element => {
                            showError('#' + element.field, element.message)
                        });
                    }
                    if (errors.project) {
                        errors.project.forEach((element, i) => {
                            let key = Object.keys(element)
                            key.forEach(k => {
                                let value = element[k]
                                value.forEach(err => {
                                    let block = $('.project-block').eq(k)
                                    let input = block.find('.' + err.field);
                                    showProjectError(input, err.message);
                                })
                            })
                        })
                    }
                }
            }
        });
    });

    function formValidation(company_name, email, phone, address, project_name, technology, status) {
        let isValid = true;

        $('.error').html('');

        if (company_name == '') {
            showError($('#company_name'), 'Please enter company name');
            isValid = false;
        }

        let emailptn = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        if (email.trim() == "") {
            showError($('#email'), 'Please enter email');
            isValid = false;
        }
        else if (!emailptn.test(email)) {
            showError($('#email'), 'Enter valid email (Ex.john@gmail.com)');
            isValid = false;
        }

        let phoneptn = /^\d{10}$/;
        if (phone == '') {
            showError($('#phone'), 'Please enter phone number');
            isValid = false;
        }
        else if (!phoneptn.test(phone)) {
            showError($('#phone'), 'Enter 10 digits number without spaces.');
            isValid = false;
        }

        if (address == '') {
            showError($('#address'), 'Please enter address');
            isValid = false;
        }

        if (project_name == '') {
            showProjectError($('.project_name').first(), 'Please enter project name')
            isValid = false;
        }

        if (technology == '') {
            showProjectError($('.technology').first(), 'Please enter technology');
            isValid = false;
        }

        if (status == '') {
            showProjectError($('.status').first(), 'Please select status');
            isValid = false;
        }
        return isValid;
    }

    function showError(div, message) {
        $(div).closest('.mb-3, .col-sm-6').find('.error').html(message).css('color', 'red')
    }

    function showProjectError(div, message) {
        $(div).closest('.col-sm-9').find('.error').html(message).css('color', 'red')
    }


    $('#searchBox, #statusDropdown, #projectDropdown, #technologyDropdown').on('keyup change', function () {
        table.ajax.reload();
    });

    // Pegination

    var table = $('#companyTable').DataTable({
        "processing": true,
        "serverSide": true,
        "pageLength": 4,
        "searching": false,
        "lengthChange": false,
        "ajax": {
            url: '/companies/',
            dataSrc: function (json) {
                $('#totalCompanies').text(json.recordsTotal)
                return json.data
            },
            data: function (d) {
                d.search = $('#searchBox').val()
                d.status = $('#statusDropdown').val()
                d.project = $('#projectDropdown').val()
                d.technology = $('#technologyDropdown').val()
            }
        },
        "columns": [
            { data: 'name' },
            { data: 'email' },
            { data: 'phone' },
            { data: 'address' },
            { data: 'is_active' },
            {
                data: 'projects',
                render: function (data) {
                    let projects = ''
                    data.forEach(function (project, index) {
                        projects += `
                        <div class="mb-2">
                            <strong> ${project.name}</strong><br>
                            <span class="text-muted">
                                (${project.technology})
                            </span>
                        </div>
                        `
                        if (index != data.length - 1) {
                            projects += `<hr>`
                        }
                    })
                    return projects;
                }
            },
            { data: 'action', orderable: false },
        ],
    })
});