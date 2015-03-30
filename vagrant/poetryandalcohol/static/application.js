$(document).ready(function() {

    $('.popup-with-form').magnificPopup({
        type: 'inline',
        preloader: false,
        focus: '#name',

        // When elemened is focused, some mobile browsers in some cases zoom in
        // It looks not nice, so we disable it:
        callbacks: {
          beforeOpen: function() {
            if($(window).width() < 700) {
              this.st.focus = false;
            } else {
              this.st.focus = '#name';
            }
          }
        }
      });

  /*GET LIST OF POEMS BY AUTHOR*/
  var get_poems = function(e) {
    $.getJSON($SCRIPT_ROOT + '/get_author_poems', {
      author_id: $(this).attr('id')
    }, update_poem_list);
    return false;
  };
  var update_poem_list = function(data) {
    console.log(data);
    clear_list();
    if(data !== null) {          
      $.each(data, function() {
        $.each(this, function(key, value){            
            $('#poem-list').append('<li><a href="#" id="' + value.id +'" class="poem-link">' + value.name + '</a></li>');
        });            
      });
        $('a.poem-link').bind('click', get_one_poem);    

        $('a.poem-link').bind('keydown', function(e) {
          if (e.keyCode == 13) {
            get_one_poem(e);
          }
  });
    } else {
      console.log('fuckayou');
    }
  };

  var get_one_poem = function(e) {    
    $.getJSON($SCRIPT_ROOT + '/get_poem', {
      poem_id: $(this).attr('id')
    }, update_poem);
    return false;
  };
  var update_poem = function(data) {
    console.log(data);
    clear_list();
    if(data !== null) {          
      $.each(data, function(key, value) {
        console.log(value.id);
        $('#poem-list').append('<span class = "fix-lines">' + value.the_poem + '<span>');
      });          
    } else {
      console.log('fuckayou');
    }
  };

  /*CLEAR POEM LIST*/
  var clear_list = function() {    
    $('#poem-list').empty();
  };

  $('a.author-link').bind('click', get_poems);    

  $('a.author-link').bind('keydown', function(e) {
    if (e.keyCode == 13) {
      get_poems(e);
    }
  });

});