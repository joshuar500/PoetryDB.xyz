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
    console.log("getting poems");
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
      console.log('whatdafuk');
    }
  };

  var get_one_poem = function(e) {   
    $.getJSON($SCRIPT_ROOT + '/get_poem', {
      poem_id: $(this).attr('id')
    }, update_poem);    
    return false;
  };
  var update_poem = function(data) {    
    if(data !== null) {          
      $.each(data, function(key, value) {
        console.log(value.id);
        $('#poem').append('<span class = "fix-lines">' + value.the_poem + '<span>');        
      });
      remove_classie_stuff();
    } else {
      console.log('fuckayou');
    }
  };

  /*CLEAR POEM LIST*/
  var clear_list = function() {    
    $('#poem-list').empty();
  };

  $('button.author-link').bind('click', get_poems);    

  $('button.author-link').bind('keydown', function(e) {
    if (e.keyCode == 13) {
      get_poems(e);
    }
  });

/*!
* classie v1.0.0
* class helper functions
* from bonzo https://github.com/ded/bonzo
* MIT license
* 
* classie.has( elem, 'my-class' ) -> true/false
* classie.add( elem, 'my-new-class' )
* classie.remove( elem, 'my-unwanted-class' )
* classie.toggle( elem, 'my-class' )
*/

/*jshint browser: true, strict: true, undef: true, unused: true */
/*global define: false */

  // class helper functions from bonzo https://github.com/ded/bonzo

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
      /**
     * The nav stuff
     */

    var body = document.body,
      mask = document.createElement("div"),
      mask_again = document.createElement("div"),
      activeNav
    ;
    mask.className = "mask";
    mask_again.className = "mask-again";

    var remove_classie_stuff = function() {      
      classie.remove(body, activeNav);
      activeNav = "";
      classie.add( body, "pmr-open-again" );
      document.body.appendChild(mask_again);
      activeNav = "pmr-open-again";  
    }

    /* push menu right */
    $('.toggle-push-right').bind( "click", function(){
      classie.add( body, "pmr-open" );
      document.body.appendChild(mask);
      activeNav = "pmr-open";
    } );    

    /* hide active menu if mask is clicked */
    $('div').bind( "click", function(){
      classie.remove( body, activeNav );
      activeNav = "";      
      $( "div" ).remove( ".mask" );
      $( "div" ).remove( ".mask-again" );
    } );

    /* hide active menu if close menu button is clicked */
    $('.close-menu').bind( "click", function(){        
        classie.remove( body, activeNav );
        activeNav = "";        
        $( "div" ).remove( ".mask" );
        $( "div" ).remove( ".mask-again" );
    });

}); 