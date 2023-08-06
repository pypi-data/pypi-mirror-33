(function($){
    'use strict';

$(function(){
    $('.aboutconfig-type-field').change(function() {
        var fieldset = $(this).closest('fieldset');
        var data_field = fieldset.find('[name="value"]');
        var that = this;

        if(this.value) {
            // disable field to prevent accidental editing while loading
            // also serves as "currently loading" feedback
            data_field.prop('disabled', 'disabled').attr('title', 'Loading...');

            $.getJSON(
                this.dataset.url,
                {
                    'id': data_field.attr('id'),
                    'value': data_field.val(),
                    'pk': this.value, // data type id
                    'config_pk': data_field.attr('instance-pk')
                },
                function(data) {
                    data_field.replaceWith(data.content);
                    $(that).data('current-value', that.value);
                }
            ).fail(function() {
                // reset dropdown and data fields' states on failure
                alert('Server request failed');
                data_field.prop('disabled', '').attr('title', '');
                that.value = $(that).data('current-value');
            });
        }
    }).each(function() {
        $(this).data('current-value', this.value);
    });
});})(django.jQuery);
