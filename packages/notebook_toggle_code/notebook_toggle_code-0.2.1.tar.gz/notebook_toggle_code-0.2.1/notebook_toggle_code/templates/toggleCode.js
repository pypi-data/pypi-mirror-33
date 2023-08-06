
'use strict';

console.log('start main');

var initShow = ('__$data.init_show$__' == 'True');
var delayToggle = __$data.delay_toggle$__;
window.codeVisible = initShow;

console.log('initShow=' + initShow);
console.log('delayToggle=' + delayToggle);


window.hideCodeCells = function () {
	$('div.input').hide(delayToggle);

	// hide input prompts
	$('div.prompt.input_prompt').delay(delayToggle).css('visibility', 'hidden');

	// hide output prompts
	$('div.prompt.output_prompt').delay(delayToggle).css('visibility', 'hidden');
	$('div.out_prompt_overlay.prompt').delay(delayToggle).css('visibility', 'hidden');

	// reduce left margin as prompts hidden
	$('.prompt').css('min-width', '3%');
	$('.prompt').css('width', '3%');

	// hide toolbars
	$('#maintoolbar-container').delay(delayToggle).css('display', 'none');
	$('#header-container').delay(delayToggle).css('display', 'none');

	// hide header
	// $('div#header').delay(delayToggle).css('display', 'none');

	// hide selected outline
	$('.cell.code_cell.rendered.selected').toggleClass('selected');
};

window.showCodeCells = function () {
	$('div.input').show(delayToggle);

	// show input prompts
	$('div.prompt.input_prompt').delay(delayToggle).css('visibility', 'visible');

	// show output prompts
	$('div.prompt.output_prompt').delay(delayToggle).css('visibility', 'visible');
	$('div.out_prompt_overlay.prompt').delay(delayToggle).css('visibility', 'visible');

	// left margin back to normal
	$('.prompt').css('min-width', '14ex');

	// show toolbars
	$('#maintoolbar-container').delay(delayToggle).css('display', '');
	$('#header-container').delay(delayToggle).css('display', '');

	// show header
	// $('div#header').delay(delayToggle).css('display', '');
};


window.setButtonToShow = function () {
	$('#toggleButton').val('Show Code');
	$('#toggleButton').removeClass('btn-primary');
};

window.setButtonToHide = function () {
	$('#toggleButton').val('Hide Code');
	$('#toggleButton').addClass('btn-primary');
}

window.toggleCodeCellsNotebook = function () {
	if (window.codeVisible) {
		window.hideCodeCells();
		window.setButtonToShow();
	} else {
		window.showCodeCells();
		window.setButtonToHide();
	}
	window.codeVisible = !window.codeVisible;
};


window.toggleCodeCellsNbviewer = function () {
	if (window.codeVisible) {
		window.hideCodeCells();
	} else {
		window.showCodeCells();
	}
	window.codeVisible = !window.codeVisible;
};



var htmlNotebook = `
<form action="javascript:toggleCodeCellsNotebook()">
	<input type="submit" id="toggleButton" value="Hide Code" class="bbtn">
</form>
`;


var htmlNbviewer = `
<li>
  <a href="javascript:window.toggleCodeCellsNbviewer()" title="Show/Hide Code">
	<span class="fa fa-cog fa-2x menu-icon"></span>
	<span class="menu-text">Show/Hide Code</span>
  </a>
</li>
`;



require([
	'jquery',
	'base/js/events',
	'base/js/namespace',
	'base/js/promises'
], function (
	$,
	events,
	Jupyter,
	promises
) {
	promises.app_initialized.then(function (appname) {
		if (appname === 'NotebookApp') {
			console.log('code cell toggle: notebook mode');
			$(htmlNotebook).appendTo('#anchor-div');
			if (window.codeVisible) {
				window.showCodeCells();
				window.setButtonToHide();
			}
			else {
				window.hideCodeCells();
				window.setButtonToShow();

			}
		}
	});
});


$(document).ready(function () {
	if ($('body.nbviewer').length) {
		console.log('code cell toggle: nbviewer mode');
		$(htmlNbviewer).appendTo('.navbar-right');
		if (window.codeVisible) {
			window.showCodeCells();
		}
		else {
			window.hideCodeCells();
		}
	}

});

console.log('end main');
