$(document).ready(function(){
	function updatePosts() {
		$.ajax({url: "/posts",
				cache: false, 
				success: function(frag){
	            	$('#posts_list').html(frag);
	        	}
	    });
	}
	updatePosts();
	setInterval(updatePosts, 2000);

	$("#backToTop").hide();
	$(function () {
		$(window).scroll(function () {
			if ($(this).scrollTop() > 400) {
				$('#backToTop').fadeIn();
			} else {
				$('#backToTop').fadeOut();
			}
		});

		$('#backToTop a').click(function () {
			$('body,html').animate({
				scrollTop: 0
			}, 800);
			return false;
		});
	});
});