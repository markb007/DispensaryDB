$(document).ready($(function() {

    // when anywhere is clicked in table row then activate the radio button
    //  and change 'a' link href to include correct record id's
    $('tr').click(function () {
        var delimiter = '/';
        $(this).find('td input:radio').prop('checked', true);
        var $checked = $("input[type='radio']").filter(':checked');
        var myvalue = $checked.val();

        //  change href
        var myaction = $("a[id='actionProductUpdate']").attr('href');
        //  get second occurence of '/' from href and extract up to that then add on value string
        var tokens2 = myaction.split(delimiter).slice(0, 3);
        var fronthref = tokens2.join(delimiter) + delimiter;
        // now replace to the end
        var result = fronthref + myvalue + delimiter;
        $("#actionProductUpdate").attr("href", result);

    });

}));