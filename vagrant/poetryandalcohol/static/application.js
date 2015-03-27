$(function() {
  var submit_form = function(e) {
    $.getJSON($SCRIPT_ROOT + '/get_author_poems', {
      author_id: $(this).attr('id')
    }, update_list);
    return false;
  };

  var update_list = function(data) {
    console.log(data);
    clear_list();
    if(data !== null) {          
      $.each(data, function() {
        $.each(this, function(key, value){            
            $('#poem-list').append('<li id="' + value.id + '">' + value.name + '</li>');
        });            
      });          
    } else {
      console.log('fuckayou');
    }
  };

  var clear_list = function() {
    console.log("panis");
    $('#poem-list').empty();
  };

  $('a.author-link').bind('click', submit_form);    

  $('a.author-link').bind('keydown', function(e) {
    if (e.keyCode == 13) {
      submit_form(e);
    }
  });
});