$(document).ready(function() {
    $('#post').hide();
    $('#post-toggle-on').on('click', function () {
        $('#post').show();
        $('#post-toggle-on').hide();
    });
    $('#post-toggle-off').on('click', function () {
        $('#post').hide();
        $('#post-toggle-on').show();
    });
});