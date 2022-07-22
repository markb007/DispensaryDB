        $(document).ready($(function() {
            $(".inline.{{ ingredient_form.prefix }}").formset({
                prefix: "{{ ingredient_form.prefix }}",
                addText: "Add another ingredient",
                deleteText: "Remove",
                formCssClass: 'dynamic-formset1',
                added: addIEvent,
                removed: removeIEvent,
            });
            $(".inline.{{ patient_form.prefix }}").formset({
                prefix: "{{ patient_form.prefix }}",
                addText: "Add another patient",
                deleteText: "Remove",
                formCssClass: 'dynamic-formset2',
            });
            
            /* we must add an event to each dynamically created input field */
            /* as once the dom is created, events are not added to dynamically created elements */
            /* Calculate the total value of the formula with this dynamically added element included */
            function addIEvent(row) {
                var formulatype = $("select[id*='formula_type']").val();
                var lastform = $("input[type='hidden'][id='id_formulaherbitem_set-TOTAL_FORMS']").val();
                lastform = lastform - 1;
                var idlast = 'id_formulaherbitem_set-'+ lastform + '-quantity';
                var getid = $('#' + idlast);
                
                /* change input number min max and step for required formula type */
                switch(formulatype) {
                    case "M":
                        getid.attr({max: 10.0, min: 0.25, step: 0.25});
                        /* if (getid.next().is('span')) {
                            getid.next().replaceWith("<span>mls</span>");
                        } else {
                                getid.after("<span>mls</span>");
                        } */
                        $("div[id*='change_qty_display']").text('Quantity (in mls)*');
                        break;
                    case "D":
                        getid.attr({max: 50, min: 1.0, step: 1.0});
                        /* if (getid.next().is('span')) {
                            getid.next().replaceWith("<span>drops</span>");
                        } else {
                                getid.after("<span>drops</span>");
                        } */
                        $("div[id*='change_qty_display']").text('Quantity (in drops)*');
                        break;
                    case "P":
                        getid.attr({max: 100, min: 5.0, step: 5.0});
                        /* if (getid.next().is('span')) {
                            getid.next().replaceWith("<span>%</span>");
                        } else {
                                getid.after("<span>%</span>");
                        } */
                        $("div[id*='change_qty_display']").text('Quantity (percentage)*');
                        break;
                    case "T":
                        getid.attr({max: 100, min: 5.0, step: 5.0});
                        /* if (getid.next().is('span')) {
                            getid.next().replaceWith("<span>mls</span>");
                        } else {
                                getid.after("<span>mls</span>");
                        } */
                        $("div[id*='change_qty_display']").text('Quantity (in total mls)*');
                        break;
                    default:
                        getid.attr({max: 10.0, min: 0.25, step: 0.25});
                        /* if (getid.next().is('span')) {
                            getid.next().replaceWith("<span>mls</span>");
                        } else {
                            getid.after("<span>mls</span>");
                        } */
                        $("div[id*='change_qty_display']").text('Quantity (in mls)*');
                        break;
                };

                /* attach event for input field change */
                /* so that formula totals are recalculated */ 
                row.on('input', function() {
                    total = (0.00).toFixed(2);
                    $("input[type='number'][id*='formulaherbitem']").each(function() {
                        if ($.isNumeric($(this).val())) {
                            total = (parseFloat(total) + parseFloat($(this).val())).toFixed(2);
                        };
                    });
                    var formulatype = $("select[id*='formula_type']").val();
                    switch (formulatype) {
                        case "M":
                            var extra = 'mls per dose';
                            break;
                        case "D":
                            var extra = 'drops per dose';
                            break;
                        case "P":
                            var extra = '%';
                            break; 
                        case "T":
                            var extra = 'total mls';
                            break; 
                        default:
                            var extra = 'mls per dose';
                            break;     
                    };
                    $("span[id*='displaytotal']").text(total + ' ' + extra);                
                }); 
                return;
            };

            /* we must recalculate totals when input line is removed */
            /* subtracting from the total displayed .. don't delete this event handler */
            function removeIEvent(row) {
                total = (0.00).toFixed(2);
                $("input[type='number'][id*='formulaherbitem']").each(function() {
                    if ($.isNumeric($(this).val())) {
                        total = (parseFloat(total) + parseFloat($(this).val())).toFixed(2);
                    };
                });
                var formulatype = $("select[id*='formula_type']").val();
                switch (formulatype) {
                    case "M":
                        var extra = 'mls per dose';
                        break;
                    case "D":
                        var extra = 'drops per dose';
                        break;
                    case "P":
                        var extra = '%';
                        break; 
                    case "T":
                        var extra = 'total mls';
                        break; 
                    default:
                        var extra = 'mls per dose';
                        break;     
                };
                $("span[id*='displaytotal']").text(total + ' ' + extra);    
                return;
            };

        }));
    
         $(document).ready($(function() {
            /* event for change to formula type field added */
            /* this is triggered on entry to the form after loading */
            $("select[id*='formula_type']").change(function() {
                /* check type of formula being prepared */
                var formulatype = $(this).val();
                /* set total back to zero */
                $("span[id*='displaytotal']").text('0.00');
                /* check input elements with id containing 'formulaherbitem' which is quantity input */
                $("input[type='number'][id*='formulaherbitem']").each(function() {
                    $(this).val("");
                    switch(formulatype) {
                        case "M":
                            $(this).attr({max: 10.0, min: 0.25, step: 0.25});
                            /* if ($(this).next().is('span')) {
                                $(this).next().replaceWith("<span>mls</span>");
                            } else {
                                    $(this).after("<span>mls</span>");
                            } */
                            $("div[id*='change_qty_display']").text('Quantity (in mls)*');
                            $("span[id*='displaytotal']").text('0.00 mls per dose');
                            break;
                        case "D":
                            $(this).attr({max: 50, min: 1.0, step: 1.0});
                            /* if ($(this).next().is('span')) {
                                $(this).next().replaceWith("<span>drops</span>");
                            } else {
                                    $(this).after("<span>drops</span>");
                            } */
                            $("div[id*='change_qty_display']").text('Quantity (in drops)*');
                            $("span[id*='displaytotal']").text('0 drops');
                            break;
                        case "P":
                            $(this).attr({max: 100, min: 5.0, step: 5.0});
                            /* if ($(this).next().is('span')) {
                                $(this).next().replaceWith("<span>%</span>");
                            } else {
                                    $(this).after("<span>%</span>");
                            } */
                            $("div[id*='change_qty_display']").text('Quantity (in percentages)*');
                            $("span[id*='displaytotal']").text('0.00 %');
                            break;
                        case "T":
                            $(this).attr({max: 100, min: 5.0, step: 5.0});
                            /* if ($(this).next().is('span')) {
                                $(this).next().replaceWith("<span>mls</span>");
                            } else {
                                    $(this).after("<span>mls</span>");
                            } */
                            $("div[id*='change_qty_display']").text('Quantity (in total mls)*');
                            $("span[id*='displaytotal']").text('0.00 total mls');
                            break;
                        default:
                            $(this).attr({max: 10.0, min: 0.25, step: 0.25});
                            /* if ($(this).next().is('span')) {
                                $(this).next().replaceWith("<span>mls</span>");
                            } else {
                                    $(this).after("<span>mls</span>");
                            } */
                            $("div[id*='change_qty_display']").text('Quantity (in mls)*');
                            $("span[id*='displaytotal']").text('0.00 mls per dose');
                            break;
                    };
                });
            });

            /* trigger formulatype change initially to add formula type detail to the form */
            $("select[id*='formula_type']").trigger('change');

            /* event for input change - change totals when input fields are changed */
            $("input[type='number'][id*='formulaherbitem']").on('input', function() {
                total = (0.00).toFixed(2);
                $("input[type='number'][id*='formulaherbitem']").each(function() {
                    if ($.isNumeric($(this).val())) {
                        total = (parseFloat(total) + parseFloat($(this).val())).toFixed(2);
                    };
                });
                var formulatype = $("select[id*='formula_type']").val();
                switch (formulatype) {
                    case "M":
                        var extra = 'mls per dose';
                        break;
                    case "D":
                        var extra = 'drops per dose';
                        break;
                    case "P":
                        var extra = '%';
                        break; 
                    case "T":
                        var extra = 'total mls';
                        break; 
                    default:
                        var extra = 'mls per dose';
                        break;     
                }
                $("span[id*='displaytotal']").text(total + ' ' + extra);
            }); 

         }));