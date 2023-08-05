var django = django || {};
django.jQuery = jQuery

var yl = yl || {};
yl.jQuery = django.jQuery

// this file also prevents django.jQuery.noConflict
// there's got to be a better way ...

// OVERRIDDEN BY DAVE - FIX FOR DJANGO AUTOCOMPLETE LIGHT