//----------------------------------------------------------------------------
//  DYMO Label Framework JavaScript Library Samples: Print label
//  Copyright (c), 2010, Sanford, L.P. All Rights Reserved.
//----------------------------------------------------------------------------
 
(function()
{
    // called when the document completly loaded
    function onload()
    {
        var label, label2, labelXml, labelXml2, printerName = "";
        var formulaid, formulacode, formulatype, patient, expiry, doseage, measure, quantity, units, frequency, directions = "";
        var business, practitioner, address1, address2, city, state, postcode, provider, providerno = "";
        var herb = [];
        var quantityherb = [];
        var setToPrint = false;
        var setToPrintIngredients = false;
        var dispensaryLabel = "/static/labels/Dispensary.label";
        var ingredientsLabel = "/static/labels/FormulaIngredients-1.label";
        var printPreview = document.getElementById('printPreview');
 
        function setLabelFields() {
            //  reset any previous errors
            $('.js-error-field').remove();
            $('#labelFormula').show();
            $('#labelIngredients').show();
            $('#js-modal-error-p').remove();  
            
            formulaid = $("select[id='id_formula']").val();
            formulacode = $("select[id='id_formula'] option:selected").text();
            if (formulacode == "")
                $("label[for='id_formula']").append("<strong class='js-error-field' style='color: red'>This field is required</strong>");
            patient = $("select[id='id_patient'] option:selected").text();
            if (patient == "")
                $("label[for='id_patient']").append("<strong class='js-error-field' style='color: red'>This field is required</strong>");
            quantity = $("select[id='id_quantity'] option:selected").val();
            units = $("select[id='id_qtytype'] option:selected").val();
            measure = $("select[id='id_measure'] option:selected").val();
            doseage = $("input[id='id_doseage']").val();
            if (doseage == "") {
                // $('#id_doseage').css({ "border": '#FF0000 1px solid'});
                $("label[for='id_doseage']").append("<strong class='js-error-field' style='color: red'>Required</strong>");
            } else {
                if(isNaN(doseage)){
                    $("label[for='id_doseage']").append("<strong class='js-error-field' style='color: red'>Not numeric</strong>");
                }
            }
            frequency = $("input[id='id_frequency']").val();
            if (frequency == "") {
                // $('#id_frequency').css({ "border": '#FF0000 1px solid'});
                $("label[for='id_frequency']").append("<strong class='js-error-field' style='color: red'>Required</strong>");
            }
            administer = $("input[id='id_administerin']").val();
            if (administer == "") {
                // $('#id_administerin').css({ "border": '#FF0000 1px solid'});
                $("label[for='id_administerin']").append("<strong class='js-error-field' style='color: red'>Required</strong>");
            }
            directions = $("input[id='id_directions']").val();
            if (directions == "") {
                // $('#id_directions').css({ "border": '#FF0000 1px solid'});
                $("label[for='id_directions']").append("<strong class='js-error-field' style='color: red'>Required</strong>");
            }
            if ($("strong").hasClass("js-error-field"))
                return false;

            return true;
        }

        // print preview the label
        printPreview.onclick = function()
        {
            // Preview labels only
            setToPrint = false;
            checkIngredientsPrint();
            printTheLabels();

        }

        // print the label(s)
        printLabel.onclick = function()
        {
            setToPrint = true;
            checkIngredientsPrint();
            printTheLabels();
        }

        function checkIngredientsPrint() 
        {
            if ($('#checkIngredients').prop("checked")) {
                // insert img html into the form inside div
                $("div[id='labelIngredients-div']").append("<img id='labelIngredients' src='' style='padding: 1px; border:1px solid #021a40; background-color: lightgray; '/>");
                setToPrintIngredients = true;
            }
            else {
                // remove img from form if it exists
                $("img[id='labelIngredients']").remove();
                setToPrintIngredients = false;
            }
        }

        function printTheLabels() {
            try
            {
                // ajax call to get formula ingredients
                var form_id = '#formula-form';
                // setup label fields
                validData = setLabelFields();
                // if invalid do not print or preview
                if (!validData) {
                    $('#labelFormula').hide();
                    $('#labelIngredients').hide();
                    $('#js-modal-label-error-msg').append("<p id='js-modal-error-p'>Please correct input errors to view the labels.</p>")
                    return;
                }
                
                //  obtain the formula ingredients if we are to print ingredients label as well
                $.ajax({
                    async: false,
                    url: $(form_id).attr("data-validate-ingredients-url"),
                    data: {'formula': formulaid},
                    dataType: 'json',
                    success: function (data) {
                        var i;
                        var inputdata = data;
                        for (i = 1; i < 11; i++) {
                            keyval = "herb_" + i;
                            if (inputdata[keyval]) {
                                herb[i] = inputdata[keyval];
                                keyval2 = "quantity_" + i;
                                quantityherb[i] = inputdata[keyval2]
                            } else {
                                herb[i] = "";
                                quantityherb[i] = "";
                            }
                        }
                        expiry = inputdata.expiry;
                        address1 = inputdata.address1;
                        address2 = inputdata.address2;
                        city = inputdata.city;
                        state = inputdata.state;
                        postcode = inputdata.postcode;
                        provider = inputdata.provider_name;
                        providerno = inputdata.provider_number;
                        practitioner = inputdata.practitioner;
                        business = inputdata.business_name;
                        formulatype = inputdata.formulatype;
                    },
                    error: function(xhr, status, error) {
                        alert("An Ajax error occurred - " + xhr.responseText);
                        return;
                    }
         
                });

                //  access label printer
                printerName = "";
                if (setToPrint) {
                    printerName = getPrinters();
                }
                // open details label
                $.get(dispensaryLabel, function(labelXml){
                    setFormulaLabel(labelXml); 

                    if ((setToPrint) && (printerName != ""))
                        label.print(printerName);
                    else
                        if (!setToPrint)
                            updatePreview();
                });

                if (setToPrintIngredients) {
                    // open ingredients label
                    $.get(ingredientsLabel, function(labelXml2){
                        setIngredientsLabel(labelXml2);
                        if ((setToPrint) && (printerName != ""))
                            label2.print(printerName);
                        else
                            if (!setToPrint)
                                updatePreview2();
                    });
                }
            }
                catch(e)
            {
                alert(e.message || e);
            }
        }

        function setFormulaLabel(labelXml) {
            label = dymo.label.framework.openLabelXml(labelXml);
            label.setObjectText("BUSINESS", business);
            label.setObjectText("NAME", patient);
            label.setObjectText("DOSEL1", doseage + measure + " " + frequency + " " + administer);
            label.setObjectText("DOSEL2", directions);
            label.setObjectText("QUANTITY", quantity + units);
            label.setObjectText("CODE", formulacode);
            label.setObjectText("EXPIRY", expiry); 
            label.setObjectText("ADDRESS1", address1);
            if (address2 == null)
                label.setObjectText("ADDRESS2", city + " " + state + " " + postcode); 
            else
                label.setObjectText("ADDRESS2", address2 + " " + city + " " + state + " " + postcode); 
            
            var today = new Date();
            var dd = today.getDate(); 
            var mm = today.getMonth() + 1; 
        
            var yyyy = today.getFullYear(); 
            var today = dd + '/' + mm + '/' + yyyy;

            label.setObjectText("DISPENSEDBY", "Dispensed By: "  + practitioner + " - Provider " + provider + " " + providerno + " on " + today); 
        }

        function setIngredientsLabel(labelXml2) {
            label2 = dymo.label.framework.openLabelXml(labelXml2);
            label2.setObjectText("BUSINESS", business);
            for (i = 1; i < 11; i++) {
                keyval = "HERB_" + i;
                label2.setObjectText(keyval, herb[i]);
            } 
            for (i = 1; i < 11; i++) {
                keyval = "DOSE_" + i;
                if (quantityherb[i] != "")
                    label2.setObjectText(keyval, quantityherb[i] + " " + formulatype);
                else
                    label2.setObjectText(keyval, quantityherb[i])
            } 
        }

        function updatePreview() {
            if (!label)
                return;
            var pngData = label.render();
            var labelImage = document.getElementById('labelFormula');
            labelImage.src = "data:image/png;base64," + pngData;
        }
              
        function updatePreview2() {
            if (!label2)
                return;
            var pngData2 = label2.render();
            var labelImage2 = document.getElementById('labelIngredients');
            labelImage2.src = "data:image/png;base64," + pngData2;
        }

        //  find labelprinter installed and online
        function getPrinters() {
            printerName = "";
            var printers = dymo.label.framework.getPrinters();
            if (printers.length == 0) {
                alert("No DYMO printers are installed. Install DYMO printers.");
                return printerName;
            }

            for (var i = 0; i < printers.length; ++i)
            {
                var printer = printers[i];
                if (printer.printerType == "LabelWriterPrinter")
                {
                    printerName = printer.name;
                    if (printer.isConnected) {
                        break;
                    }
                    else {
                        alert("DYMO printer '" + printerName + "' is installed, but is offline");
                        return printerName;
                    }
                }
            }

            if (printerName == "")
                alert("No LabelWriter printers found. Install LabelWriter printer");
            
            return printerName
        }
    };
 
    // register onload event
    if (window.addEventListener)
        window.addEventListener("load", onload, false);
    else if (window.attachEvent)
        window.attachEvent("onload", onload);
    else
        window.onload = onload;
 
} ());