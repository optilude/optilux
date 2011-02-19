jQuery(function($) {
    
    // No overlays for IE6
    if (!jQuery.browser.msie || parseInt(jQuery.browser.version, 10) >= 7) {
        
        // Set up overlays
        $("#siteaction-enquiry > a").prepOverlay({
            subtype: 'ajax',
        
            // Which part of the page do we want to show in the overlay?
            filter: '#content>*',
        
            // Which form are we using?
            formselector: '#content-core > form',
        
            // What happens if there is no form, e.g. on successful
            // submisison?
            noform: 'close',
        
            // Button that closes the form
            closeselector: '[name=form.buttons.cancel]',
        });
        
    }
    
    // Update film ratings asynchronously
    $("#filmRatings input[type='submit']").click(function() {
        
        var action = $("#filmRatings").attr('data-ajax-target');
        var token = $("#filmRatings input[name='_authenticator']").val();
        var button = $(this).attr('name');
        var value = $(this).val();
        
        var data = {'_authenticator': token};
        data[button] = action;
        
        $.post(action, 
            data,
            function(data) {
                var newStatus = data['newStatus'];
                $("#ratingForm").hide();
                $("#ratingStatus").html(newStatus);
            },
            'json');
        
        return false;
    });
    
});
