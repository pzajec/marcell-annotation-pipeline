$('#anonButton').on('click', function(event) {
    let text = $('#mainText').val();
    $.ajax({
        url: '/anonymizetext',
        type: 'POST',
        contentType: "text/plain; charset=utf-8",
        data: text,
        success: function (response) {
            $('#mainOut').html(response);
        }
    });
});