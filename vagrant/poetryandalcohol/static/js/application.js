$(document).ready(function() {

    var initMagPopup = function() {
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
    };

  /*INITIALIZE MAGNIFIC POPUP*/
  initMagPopup();

  /*GET LIST OF POEMS BY AUTHOR THEN UPDATE THE PAGE*/
  var get_poems = function(e) {    
    $.getJSON($SCRIPT_ROOT + '/get_author_poems', {
      author_id: $(this).attr('id')
    }, update_poem_list);
    return false;
  };
  var update_poem_list = function(data) {    
    clear_list();
    if(data !== null) {          
      $.each(data, function() {
        $.each(this, function(key, value){            
            $('#poem-list').append('<button class="poem-link nav-toggler toggle-push-right-again" id="'+ value.id +'"><a href="#">' + value.name + '</a></button><br />');
        });            
      });
        $('button.poem-link').bind('click', get_one_poem);    

        $('button.poem-link').bind('keydown', function(e) {
          if (e.keyCode == 13) {
            get_one_poem(e);
          }        
        });        

    } else {
      return false;
    }
  };

  /*GET A SINGLE POEM THEN UPDATE THE PAGE*/
  var get_one_poem = function(e) {   
    $.getJSON($SCRIPT_ROOT + '/get_poem', {
      poem_id: $(this).attr('id')
    }, display_poem);    
    return false;
  };
  var display_poem = function(data) {
    clear_list();   
    if(data !== null) {          
      $.each(data, function(key, value) {        
        $('#poem').append('<span class = "fix-lines">' + value.the_poem + '<span>' +
                          '<a href="#update-poem-form" class="update-poem-link popup-with-form open-popup-link">' +
                          '<i class="fa fa-pencil-square-o"><span style="display:none;">' + value.author_id + '</span></i>' +
                          '</a>' +
                          '<a href="#delete-poem-form" class="update-poem-link popup-with-form open-popup-link">' +
                          '<i class="fa fa-times"></i>' +
                          '</a>');        
      });      
      initMagPopup();      
      remove_classie_stuff();

      $('a.update-poem-link').bind('click', update_poem_place);

    } else {
      return false;
    }
  };

  /*UPDATE THE AUTHORS NAME/ID FOR FORM*/
  /*FORM DOES ACTUAL LOGIC*/
  var update_author_place = function() {      
      clear_author_forms();
      /*now update everything*/      
      author_id = $(this).parent().attr('id');      
      $('#update-author-form #id').attr('value', author_id);      
      $('#delete-author-form #id').attr('value', author_id);
  };

  /*UPDATE THE POEM'S NAME/ID FOR FORM*/
  /*FORM DOES ACTUAL LOGIC*/
  var update_poem_place = function() {      
      clear_poem_forms();
      /*now update everything*/      
      poem_id = $('#poem').find('i').text();
      $('#update-poem-form #id').attr('value', poem_id);
      $('#delete-poem-form #id').attr('value', poem_id);      
  };

  /*CLEAR POEM LIST*/
  var clear_list = function() {    
    $('#poem-list').empty();
    $('#poem').empty();
  };

  var clear_author_forms = function() {
    $('#update-author-form #name').attr('value', '');
    $('#update-author-form #id').attr('value', '');

    $('#delete-author-form #name').attr('value', '');
    $('#delete-author-form #id').attr('value', '');
  };

  var clear_poem_forms = function() {
    $('#update-poem-form #name').attr('value', '');
    $('#update-poem-form #id').attr('value', '');

    $('#delete-poem-form #name').attr('value', '');
    $('#delete-poem-form #id').attr('value', '');
  };

  /* class helper functions from bonzo 
   * https://github.com/ded/bonzo 
   */
  function classReg( className ) {
    return new RegExp("(^|\\s+)" + className + "(\\s+|$)");
  }

  // classList support for class management
  // altho to be fair, the api sucks because it won't accept multiple classes at once
  var hasClass, addClass, removeClass;

  if ( 'classList' in $(document.documentElement) ) {
    hasClass = function( elem, c ) {
      return elem.classList.contains( c );
    };
    addClass = function( elem, c ) {
      elem.classList.add( c );
    };
    removeClass = function( elem, c ) {
      elem.classList.remove( c );
    };
  }
  else {
    hasClass = function( elem, c ) {
      return classReg( c ).test( elem.className );
    };
    addClass = function( elem, c ) {
      if ( !hasClass( elem, c ) ) {
        elem.className = elem.className + ' ' + c;
      }
    };
    removeClass = function( elem, c ) {
      elem.className = elem.className.replace( classReg( c ), ' ' );
    };
  }

  function toggleClass( elem, c ) {
    var fn = hasClass( elem, c ) ? removeClass : addClass;
    fn( elem, c );
  }

  var classie = {
    // full names
    hasClass: hasClass,
    addClass: addClass,
    removeClass: removeClass,
    toggleClass: toggleClass,
    // short names
    has: hasClass,
    add: addClass,
    remove: removeClass,
    toggle: toggleClass
  };
  
  /*
   * The nav stuff
   */
  var body = document.body,
    mask = document.createElement("div"),
    mask_again = document.createElement("div"),
    activeNav
  ;

  /* first mask is for poem list, 
   * second mask is for individual poem 
   */
  mask.className = "mask";
  mask_again.className = "mask-again";

  var remove_classie_stuff = function() {      
    classie.remove(body, activeNav);
    activeNav = "";
    classie.add( body, "pmr-open-again" );
    document.body.appendChild(mask_again);
    activeNav = "pmr-open-again";  
  };

    /* author links when clicked will call get_poems function */
  $('button.author-link').bind('click', get_poems);    

  $('button.author-link').bind('keydown', function(e) {
    if (e.keyCode == 13) {
      get_poems(e);
    }
  });

  $('a.update-author-link').bind('click', update_author_place);

  /* push menu right when element class is clicked */
  $('.toggle-push-right').bind( "click", function(){
    classie.add( body, "pmr-open" );
    document.body.appendChild(mask);
    activeNav = "pmr-open";
  } );    

  /* hide active menu if close menu button is clicked */
  $('.close-menu').bind( "click", function(){        
      classie.remove( body, activeNav );
      activeNav = "";        
      $( "div" ).remove( ".mask" );
      $( "div" ).remove( ".mask-again" );
  });

  /* hide active menu if close menu button is clicked */
  $('.close-menu-again').bind( "click", function(){        
      classie.remove( body, activeNav );
      activeNav = "";        
      $( "div" ).remove( ".mask" );
      $( "div" ).remove( ".mask-again" );
  });

}); 