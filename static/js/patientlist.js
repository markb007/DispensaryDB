$(document).ready($(function() {

    // when anywhere is clicked in table row then activate the radio button
    //  and change 'a' link href to include correct record id's
    $('tr').click(function () {
        var delimiter = '/';
        $(this).find('td input:radio').prop('checked', true);
        var $checked = $("input[type='radio']").filter(':checked');
        var myvalue = $checked.val();
        
        //  change href for each 'a' link - all the same number of parms
        $("a[id^='action']").each(function() {
            var myaction = $(this).attr('href');
            var tokens2 = myaction.split(delimiter).slice(0, 4);
            var fronthref = tokens2.join(delimiter) + delimiter;
            // now replace to the end
            var result = fronthref + myvalue;
            $(this).attr("href", result);
        });

    });

}));