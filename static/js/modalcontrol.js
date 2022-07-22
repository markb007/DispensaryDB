//  Javascript for modal control for add indication or action on the herbalmedicine add or update page
//  adjust header in the modal to the request type
//  send request to view - 
//  get response and display
var dbTable = "Indication";

$('#addRecordModal').on('show.bs.modal', function (event) {
    $('#msgSelected').hide();
    $('#msg_return').text("");
    $('#indication-name').val('');
    $('#id_error-msg').remove();
    var button = $(event.relatedTarget);     // Button that triggered the modal - for Action or Indication
    dbTable = button.data('recordtype'); // Extract info from data-* attributes
    $('.indication-type').text(dbTable + ':'); // Extract info from data-* attributes
    var modal = $(this);
    modal.find('.modal-title').text('Add ' + dbTable + ' to Database');
});

$('#ajaxsubmit').click(function(event) {
    $('#id_error_msg').remove();
    var dataentry = $('#indication-name').val();
    if (dataentry == "") {
        $("label[for='indication-name']").append("<strong id='id_error_msg' class='text-danger'>  This field is required</strong>");
        return;
    }
        
    $.ajax({
        async: false,
        url: $('#modal_indication_form').attr("data-validate-indication-url"),
        data: {'addToTable': dbTable,
               'dataentry': dataentry},
        dataType: 'json',
        success: function (data) {
            $('#msgSelected').show();
            $('#msg_return').text(data['outcome']);
        },
        error: function(xhr, status, error) {
            alert("An Ajax error occurred - " + xhr.responseText);
            return;
        }

    });
    event.preventDefault();     // stay on the modal till closed by user
})