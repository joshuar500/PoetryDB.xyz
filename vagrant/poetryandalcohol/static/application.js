$(function() {
  var submit_form = function(e) {
    $.getJSON($SCRIPT_ROOT + '/get_author_poems', {
      author_id: $(this).attr('id')
    }, function(data) {
      console.log(data);
      if(data !== null) {          
        $.each(data, function() {
          $.each(this, function(key, value){
              console.log(value.name);
              $("#result").text(value.name);
          });            
        });          
      } else {
        console.log("fuckayou");
      }
    });
    return false;
  };

  $('a.author-link').bind('click', submit_form);    

  $('a.author-link').bind('keydown', function(e) {
    if (e.keyCode == 13) {
      submit_form(e);
    }
  });
});