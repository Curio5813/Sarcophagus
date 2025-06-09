/* =================================
------------------------------------
	Game Warrior Template
	Version: 1.0
 ------------------------------------ 
 ====================================*/


'use strict';


$(window).on('load', function() {
	/*------------------
		Preloder
	--------------------*/
	$(".loader").fadeOut(); 
	$("#preloder").delay(400).fadeOut("slow");

});

(function($) {

	/*------------------
		Navigation
	--------------------*/
	$('.nav-switch').on('click', function(event) {
		$('.main-menu').slideToggle(400);
		event.preventDefault();
	});


	/*------------------
		Background Set
	--------------------*/
	$('.set-bg').each(function() {
		var bg = $(this).data('setbg');
		$(this).css('background-image', 'url(' + bg + ')');
	});


	/*------------------
		Hero Slider
	--------------------*/
	try {
	    Object.defineProperty(document, 'hidden', {value: false, writable: false});
    } catch (e) {
	    console.warn("Não foi possível aplicar autoplay contínuo fora da aba:", e);
    }
	$(".hero-slider").owlCarousel({
	items: 1,
	loop: true,                 // Loop infinito
	autoplay: true,             // Autoplay ligado
	autoplayTimeout: 5000,      // Tempo entre slides (5 segundos)
	autoplayHoverPause: false, // Não pausa quando passa o mouse
	smartSpeed: 800,            // Velocidade da transição
	animateOut: 'fadeOut',      // Animação de saída
	nav: false,
	dots: true
    });
	var dot = $('.hero-slider .owl-dot');
	dot.each(function() {
		var index = $(this).index() + 1;
		if(index < 10){
			$(this).html('0').append(index);
			$(this).append('<span>.</span>');
		}else{
			$(this).html(index);
			$(this).append('<span>.</span>');
		}
	});


	/*------------------
		News Ticker
	--------------------*/
	$('.news-ticker').marquee({
	    duration: 10000,
	    //gap in pixels between the tickers
	    //gap: 200,
	    delayBeforeStart: 0,
	    direction: 'left',
	    duplicated: true
	});

})(jQuery);

