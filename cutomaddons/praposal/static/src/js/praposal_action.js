odoo.define('praposal.proposal_actions', function (require) {
    'use strict';
    
    var ajax = require('web.ajax');
    console.log("test-javascript--file")
    $(document).ready(function () {
        function updateTotal() {
            var total = 0;
            $('tbody tr').each(function () {
                var qty_accepted = $(this).find('input[id^="qty_accepted_"]').val();
                var price_accepted = $(this).find('input[id^="price_accepted_"]').val();
                var lineTotal = parseFloat(qty_accepted) * parseFloat(price_accepted);
                total += lineTotal;
            });
            $('#subtotal').text(total.toFixed(2));
            $('#total').text(total.toFixed(2));
        }

        // Call updateTotal function when any input box changes
        $('input[id^="qty_accepted_"], input[id^="price_accepted_"]').on('input', function() {
            updateTotal();
        });

        $('#accept_proposal').on('click', function () {
            var proposal_id = $(this).data('id');
            var token = $(this).data('token');
            var lines = [];

            $('tbody tr').each(function () {
                var line_id = $(this).find('input[id^="qty_accepted_"]').attr('id').split('_')[2];
                var qty_accepted = $(this).find('input[id^="qty_accepted_"]').val();
                var price_accepted = $(this).find('input[id^="price_accepted_"]').val();

                lines.push({
                    id: line_id,
                    qty_accepted: qty_accepted,
                    price_accepted: price_accepted,
                });
            });

            ajax.jsonRpc('/proposal/accept', 'call', {
                proposal_id: proposal_id,
                token: token,
                lines: lines,
            }).then(function (result) {
                if (result.status === 'success') {
                    updateTotal(); // Update total after accepting proposal
                    alert(result.data)
                    window.location.reload();
                }
            });
        });

        $('#refuse_proposal').on('click', function () {
            var proposal_id = $(this).data('id');
            var token = $(this).data('token');

            ajax.jsonRpc('/proposal/refuse', 'call', {
                proposal_id: proposal_id,
                token: token,
            }).then(function (result) {
                if (result.status === 'success') {
                    window.location.reload();
                }
            });
        });

        // Call updateTotal function when the page is loaded
        updateTotal();
    });
});
