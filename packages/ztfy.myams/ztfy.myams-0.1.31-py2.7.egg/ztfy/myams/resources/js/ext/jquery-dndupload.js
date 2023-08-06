/* globals MyAMS */

(function($, globals) {

	'use strict';

	$.dndupload = {
		defaults: {
			action: 'upload-files',
			fieldname: 'files',
			autosubmit: true
		}
	};

	var ams = MyAMS;

	var isAdvancedUpload = function() {
		var div = document.createElement('div');
		return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) && ('FormData' in window) && ('FileReader' in window);
	} ();

	// Initialize upload form
	function init(input, settings) {
		$(input).each(function() {
			var widget = $(this);
			if (widget.data('ams-dndupload-initialiazed')) {
				return;
			}
			settings = $.extend(true, {}, $.dndupload.defaults, settings);

			var uploader = widget.get(0);
			if (uploader.tagName !== 'FORM') {
				widget.removeClass('dndupload')
					  .html('<form action="{action}" method="POST" enctype="multipart/form-data" class="dndupload"></form>'.replace(/{action}/, settings.action));
				widget = $('form', widget);
			}
			var template = '<div class="box__input">\n' +
				'	<svg class="box__icon" xmlns="http://www.w3.org/2000/svg" width="50" height="43" viewBox="0 0 50 43">\n' +
				'		<path d="M48.4 26.5c-.9 0-1.7.7-1.7 1.7v11.6h-43.3v-11.6c0-.9-.7-1.7-1.7-1.7s-1.7.7-1.7 1.7v13.2c0 .9.7 1.7 1.7 1.7h46.7c.9 0 1.7-.7 1.7-1.7v-13.2c0-1-.7-1.7-1.7-1.7zm-24.5 6.1c.3.3.8.5 1.2.5.4 0 .9-.2 1.2-.5l10-11.6c.7-.7.7-1.7 0-2.4s-1.7-.7-2.4 0l-7.1 8.3v-25.3c0-.9-.7-1.7-1.7-1.7s-1.7.7-1.7 1.7v25.3l-7.1-8.3c-.7-.7-1.7-.7-2.4 0s-.7 1.7 0 2.4l10 11.6z" />\n' +
				'	</svg>\n' +
				'	<input type="file" name="{label}" id="file" class="box__file" multiple="multiple"\n'.replace(/{label}/, settings.fieldname) +
				'		   data-multiple-caption="{label}" />\n'.replace(/{label}/, ams.plugins.i18n.dndupload.FILES_SELECTED) +
				'	<label for="file">\n' +
				'		<strong>{label}</strong> {add}<br />\n'.replace(/{label}/, ams.plugins.i18n.dndupload.CHOOSE_FILE).replace(/{add}/, ams.plugins.i18n.dndupload.ADD_INFO) +
				'		<span class="box__dragndrop">{label}</span></label>\n'.replace(/{label}/, ams.plugins.i18n.dndupload.DRAG_FILE) +
				'	<button type="submit" class="box__button">{label}</button>\n'.replace(/{label}/, ams.plugins.i18n.dndupload.UPLOAD) +
				'</div>\n' +
				'<div class="box__uploading">{label}</div>\n'.replace(/{label}/, ams.plugins.i18n.dndupload.UPLOADING) +
				'<div class="box__success">{label}\n'.replace(/{label}/, ams.plugins.i18n.dndupload.DONE) +
				'	<a href=".?" class="box__restart" role="button">{label}</a>\n'.replace(/{label}/, ams.plugins.i18n.dndupload.UPLOAD_MORE) +
				'</div>\n' +
				'<div class="box__error">{label}<span></span>. \n'.replace(/{label}/, ams.plugins.i18n.dndupload.ERROR) +
				'	<a href=".?" class="box__restart" role="button">{label}</a>\n'.replace(/{label}/, ams.plugins.i18n.dndupload.TRY_AGAIN) +
				'</div>';
			widget.html(template);

			var form = widget,
				input = form.find('input[type="file"]'),
				label = form.find('label'),
				error = form.find('.box__error span'),
				restart = form.find('.box__restart'),
				droppedFiles = false;

			var showFiles = function(files) {
				label.text(files.length > 1 ? (input.attr('data-multiple-caption') || '').replace(/{count}/, files.length) : files[0].name);
			};

			input.on('change', function(ev) {
				showFiles(ev.target.files);
				if (settings.autosubmit) {
					form.trigger('submit');
				}
			});

			if (isAdvancedUpload) {
				form.addClass('has-advanced-upload')
					.on('drag dragstart dragend dragover dragenter dragleave drop', function(ev) {
						ev.preventDefault();
						ev.stopPropagation();
					})
					.on('dragover dragenter', function() {
						form.addClass('is-dragover');
					})
					.on('dragleave dragend drop', function() {
						form.removeClass('is-dragover');
					})
					.on('drop', function(ev) {
						droppedFiles = ev.originalEvent.dataTransfer.files;
						showFiles(droppedFiles);
						if (settings.autosubmit) {
							form.trigger('submit');
						}
					});
			}

			form.on('submit', function(ev) {
				if (form.hasClass('is-uploading')) {
					return false;
				}
				form.addClass('is-uploading')
					.removeClass('is-error');
				if (isAdvancedUpload) {
					ev.preventDefault();
					var ajaxData = new FormData(form.get(0));
					if (droppedFiles) {
						$.each(droppedFiles, function(i, file) {
							ajaxData.append(input.attr('name'), file);
						});
					}
					$.ajax({
						url: form.attr('action'),
						type: form.attr('method'),
						data: ajaxData,
						dataType: 'json',
						cache: false,
						contentType: false,
						processData: false,
						success: function(data) {
							if (typeof(data) === 'string') {
								data = JSON.parse(data);
							}
							ams.ajax.handleJSON(data);
						},
						complete: function() {
							form.removeClass('is-uploading');
						}
					});
				} else {
					var iframeName = 'uploadiframe_' + new Date().getTime(),
						iframe = $('<iframe>').attr('name', iframeName)
											  .attr('style', 'display: none')
											  .appendTo($('body'));
					form.attr('target', iframeName);
					iframe.one('load', function() {
						var data = JSON.parse(iframe.contents().find('body').text());
						form.removeClass('is-uploading')
							.addClass(data.success === true ? 'is-success' : 'is-error')
							.removeAttr('target');
						if (!data.success) {
							error.text(data.error);
						}
						iframe.remove();
					});
				}
			});

			restart.on('click', function(ev) {
				ev.preventDefault();
				form.removeClass('is-error is-success');
				input.trigger('click');
			});

			input.on('focus', function() {
					input.addClass('has-focus');
				}).on('blur', function() {
					input.removeClass('has-focus');
				});

			$(uploader).removeClass('hidden');
			widget.data('ams-dndupload-initialized', true);
		});

		return input;
	}

	function destroy(input) {

	}

	$.extend($.fn, {

		dndupload: function(method, data) {

			var input = $(this);

			switch(method) {

				case 'settings':
					if (data === undefined) {
						return input.data('dndupload-settings');
					} else {
						input.each(function() {
							var settings = input.data('dndupload-settings') || {};
							destroy($(this));
							input.dndupload($.extend(true, settings, data));
						});
					}
					return input;

				case 'destroy':
					input.each(function() {
						destroy($(this));
					});
					return input;

				default:
					if (method !== 'create') {
						data = method;
					}
					input.each(function() {
						init($(this), data);
					});
					return input;
			}
		}

	});

})(jQuery, this);
