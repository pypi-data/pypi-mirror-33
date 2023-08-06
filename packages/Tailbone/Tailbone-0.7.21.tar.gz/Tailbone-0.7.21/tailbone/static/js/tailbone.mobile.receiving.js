
/************************************************************
 *
 * tailbone.mobile.receiving.js
 *
 * Global logic for mobile receiving feature
 *
 ************************************************************/


// TODO: this is really just for receiving; should change form name?
$(document).on('autocompleteitemselected', 'form[name="new-purchasing-batch"] .vendor', function(event, uuid) {
    $('#new-receiving-types').show();
});


// TODO: this is really just for receiving; should change form name?
$(document).on('autocompleteitemcleared', 'form[name="new-purchasing-batch"] .vendor', function(event) {
    $('#new-receiving-types').hide();
});


$(document).on('click', 'form[name="new-purchasing-batch"] #receive-truck-dump', function() {
    var form = $(this).parents('form');
    form.find('input[name="workflow"]').val('truck_dump');
    form.submit();
});


$(document).on('click', 'form.receiving-update #delete-receiving-row', function() {
    var form = $(this).parents('form');
    form.find('input[name="delete_row"]').val('true');
    form.submit();
});


// handle receiving action buttons
$(document).on('click', 'form.receiving-update .receiving-actions button', function() {
    var action = $(this).data('action');
    var form = $(this).parents('form:first');
    var uom = form.find('[name="keypad-uom"]:checked').val();
    var mode = form.find('[name="mode"]:checked').val();
    var qty = form.find('.keypad-quantity').text();
    if (action == 'add' || action == 'subtract') {
        if (qty != '0') {
            if (action == 'subtract') {
                qty = '-' + qty;
            }

            if (uom == 'CS') {
                form.find('[name="cases"]').val(qty);
            } else { // units
                form.find('[name="units"]').val(qty);
            }

            if (action == 'add' && mode == 'expired') {
                var expiry = form.find('input[name="expiration_date"]');
                if (! /^\d{4}-\d{2}-\d{2}$/.test(expiry.val())) {
                    alert("Please enter a valid expiration date.");
                    expiry.focus();
                    return;
                }
            }

            form.submit();
        }
    }
});


$(document).on('click', 'form.receiving-update .receive-one-case', function() {
    var form = $(this).parents('form:first');
    form.find('[name="mode"]').val('received');
    form.find('[name="cases"]').val('1');
    form.submit();
});
