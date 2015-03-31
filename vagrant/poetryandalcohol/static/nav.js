/**
 * The nav stuff
 */
(function( window ){
	
	'use strict';

	var body = document.body,
		mask = document.createElement("div"),
		togglePushRight = document.querySelector( ".toggle-push-right" ),
		pushMenuRight = document.querySelector( ".push-menu-right" ),
		activeNav
	;
	mask.className = "mask";

	/* push menu right */
	togglePushRight.addEventListener( "click", function(){
		classie.add( body, "pmr-open" );
		document.body.appendChild(mask);
		activeNav = "pmr-open";
	} );

	/* hide active menu if mask is clicked */
	mask.addEventListener( "click", function(){
		classie.remove( body, activeNav );
		activeNav = "";
		document.body.removeChild(mask);
	} );

	/* hide active menu if close menu button is clicked */
	[].slice.call(document.querySelectorAll(".close-menu")).forEach(function(el,i){
		el.addEventListener( "click", function(){
			classie.remove( body, activeNav );
			activeNav = "";
			document.body.removeChild(mask);
		} );
	});


})( window );