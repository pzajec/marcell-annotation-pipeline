$('#anonButton').on('click', function(event) {
    let text = $('#mainText').val();
    document.getElementById('anonButtonSpin').style.visibility = 'visible';

    $.ajax({
        url: '/anonymizetext',
        type: 'POST',
        contentType: "text/plain; charset=utf-8",
        data: text,
        success: function (response) {
            document.getElementById('anonButtonSpin').style.visibility = 'hidden';
            $('#mainOut').html(response);
        }
    });
});

$("form#data").submit(function(e) {
    e.preventDefault();    
    var formData = new FormData(this);
    document.getElementById('anonFileSpin').style.visibility = 'visible';

    $.ajax({
        url: '/submit',
        type: 'POST',
        data: formData,
        success: function (response) {
            document.getElementById('anonFileSpin').style.visibility = 'hidden';
            $('#mainOut').html(response);
        },
        cache: false,
        contentType: false,
        processData: false
    });
});