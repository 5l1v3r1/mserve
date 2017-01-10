$(document).ready(function() {

    console.log('hi');
    function format(release) {
        return [ '<tr>'
               ,    '<td>' + release.artist + '</td>'
               ,    '<td>'
               ,        '<a href="/download/' + release.id + '">'
               ,            '<span class="glyphicon glyphicon-download-alt"></span>'
               ,        '</a>'
               ,        '&nbsp'
               ,        '<a href="https://musicbrainz.org/release/' + release.id + '" target="_blank">'
               ,            release.title
               ,        '</a>'
               ,    '</td>'
               ,    '<td>' + release.year + '</td>'
               ,    '<td>' + release.genre + '</td>'
               , '</tr>'
               ].join('');
    }

    function get_params() {
        return {
            artist: $('#artist').val(),
            title: $('#title').val(),
            genre: $('#genre').val(),
            year_from: $('#year_from').val(),
            year_to: $('#year_to').val(),
        };
    }

    $('#search-form').submit(function (evt) {
        evt.preventDefault();
        $.get('/search', get_params(), function(data) {
            $('#results').html(data.results.map(format));
            $('#results-area').css('visibility', 'visible');
        });
    });

});
