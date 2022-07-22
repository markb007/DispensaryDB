$(document).ready($(function() {

    $("a[id*='action'").click(function( event ) {
        //  check if a radio button has been selected on a row - if not then show message
        if (!$("input[name='checkRadio']:checked").val()) {
          $('#radioNotSelected').show();
          event.preventDefault();
        } else {
          $('#radioNotSelected').hide();
        }
      });

    }));