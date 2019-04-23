
var uploadFileId = 0;
var matchRes = {};

$(function() {

    var bar = $('.bar');
    var percent = $('.percent');
    var status = $('#status');

    $('#fileInput').change(function(){
        $('#fileUploadForm').submit();
    });

    // File Upload function
	$('body').on('submit','#fileUploadForm',function(e){
        e.preventDefault();

        uploadFileId = 0;
        $('.btn-find-match').attr('disabled', 'disabled');
        $('.uploadError').hide();
        
        show_progressbar();

		var url = $(this).attr('action');
		var frm = $(this);
		
		var data = new FormData();
		if(frm.find('#fileInput[type="file"]').length === 1 ){
            data.append('file', frm.find('#fileInput')[0].files[0]);
            data.append('csrfmiddlewaretoken', $("input[name=csrfmiddlewaretoken]").val());
		}
		
		var ajax  = new XMLHttpRequest();
		ajax.upload.addEventListener('progress',function(evt){
			var percentage = (evt.loaded/evt.total)*100;
			upadte_progressbar(Math.round(percentage));
		},false);
		ajax.addEventListener('load',function(evt){

            var response = evt.target.responseText;
            try {
                res = JSON.parse(response);
                if(res['status']){
                    $('.btn-find-match').removeAttr('disabled');
                    uploadFileId = res['id'];
                    preview_image('.panel-source-file', res['fileUrl']);
                }else{
                    show_error(res['errMsg']);
                }

            } catch(e) {
                show_error('upload failed');
            }

            upadte_progressbar(0);
			
		},false);
		ajax.addEventListener('error',function(evt){
			show_error('upload failed');
			upadte_progressbar(0);
		},false);
		ajax.addEventListener('abort',function(evt){
			show_error('upload aborted');
			upadte_progressbar(0);
		},false);
		ajax.open('POST',url);
		ajax.send(data);
		return false;
	});
}); 

function findMatch (urlAddr) {
    $('.match-progress').css('display', 'block');
    $('.panel-match-file .file-preview').hide();
    $('.matchFindError').hide();

    $.ajax({
        xhr: function () {
            var xhr = new window.XMLHttpRequest();
            /*
            xhr.upload.addEventListener("progress", function (evt) {
                if (evt.lengthComputable) {
                    var percentComplete = evt.loaded / evt.total;
                    if (percentComplete === 1) {
                        $('.progress').addClass('hide');
                    }
                }
            }, false);*/
            xhr.addEventListener("progress", function (evt) {
                if (evt.lengthComputable) {
                    var percentComplete = evt.loaded / evt.total;
                    upadte_match_progressbar(percentComplete);
                }
            }, false);
            return xhr;
        },
        type: 'GET',
        url: urlAddr + "/" + uploadFileId,
        success: function (data) {
            upadte_match_progressbar(1);
            try {
                res = data;
                if(res['status']){
                    matchRes = res;
                    showMatchFiles(res);
                }else{
                    show_match_error(res['errMsg']);
                }

            } catch(e) {
                show_match_error('Server`s response is not correct');
            }
        }
    });
}

function show_progressbar(showOrHide = true){
    if(showOrHide){
        $('#fileUploadForm').hide();
        $('.upload-process-wrap').show();
    } 
    else{
        $('#fileUploadForm').show();
        $('.upload-process-wrap').hide();
    }
}

function upadte_progressbar(value){
	if(value==0){
        show_progressbar(false);
        $('#fileUploadForm').trigger("reset");
	}else{
        $('.upload-process-wrap .process-value').html(value + '%');
	}
}

function upadte_match_progressbar(percentComplete){
    $('.match-progress .match-progress-value').html(percentComplete * 100 + '%');
    $('.match-progress .progress-bar').css({
        width: percentComplete * 100 + '%'
    });
}

function show_error(error){
	$('.uploadError').show();
	$('.uploadError').html(error);
}

function show_match_error(error){
	$('.matchFindError').show();
	$('.matchFindError').html(error);
}

function preview_image(panelName, srcUrl){
    var ext = srcUrl.split('.').pop().toLowerCase();
    var html = "";
    if(ext == "pdf"){
        html = "<embed src=\"" + srcUrl + "\">";
    }else{
        html = "<img src=\"" + srcUrl + "\">";
    }
    $(panelName + ' .file-preview').html(html);
}

function preview_match(masterUrl, cropUrl, accuracy, match, ismatch, scoreStr) {
    html = "<div class=\"col-sm-6\"><img class=\"cropimg\" src=\"" + masterUrl + "\"></div>";
    html += "<div class=\"col-sm-6\"><img class=\"cropimg\" src=\"" + cropUrl + "\"></div>";

    matchStr = "Identical Person: " + ismatch + "  " + "Confidence: " + Math.round(match * 100) + '%';
    html += "<div class=\"col-sm-12 matchPercent\">" + matchStr + "</div>";
    html += "<div class=\"col-sm-12 matchPercent\"><table class=\"table\"><thead class=\"thead-dark\"><tr><th width=\"40%\">Fields</th><th width=\"25%\">Master File</th><th  width=\"25%\">File Values</th><th width=\"10%\">Match Score</th></tr></thead><tbody class=\"score_table\">";
    score = JSON.parse(scoreStr);
    for (var idx in score) {
        if (score[idx]["score"] === 1)
            matchScore = 'Y';
        else
            matchScore = 'N';
        html += "<tr><td>" + score[idx]["Def"] + "</td><td>" + score[idx]["values"] + "</td><td>" + score[idx]["file"] + "</td><td>" + matchScore + "</td></tr>";
    }
    html += "</tbody></table></div>";

    $('.panel-match-result .img-preview').html(html);

    accStr = Math.round(accuracy * 100) + '%';
    $('#accuracy').html(accStr);
}

var curViewMatchFileIndex = 0;
function showMatchFiles(res){
    // curViewMatchFileIndex = ind;
    $('.panel-match-file .match-progress').hide();
    if($('.panel-match-file .file-preview').css('display').toLowerCase() != 'block'){
        $('.panel-match-file .file-preview').show();
    }

    /* if(ind == 0) $('.panel-match-file .btn-matchfile-prev').attr('disabled', 'disabled');
    else $('.panel-match-file .btn-matchfile-prev').removeAttr('disabled');
    if(ind >= matchedFiles.length - 1) $('.panel-match-file .btn-matchfile-next').attr('disabled', 'disabled');
    else $('.panel-match-file .btn-matchfile-next').removeAttr('disabled'); */

    /* if(matchedFiles.length > 1) $('.view-control-matchfile').css('display', 'flex');
    else $('.view-control-matchfile').css('display', 'none'); */

    /* if(ind >= 0 && ind < matchedFiles.length){
        $('.div-matchfile-page').html((ind + 1) + " / " + matchedFiles.length);
        preview_image('.panel-match-file', matchedFiles[ind]['fileUrl']);
        preview_image('.panel-match-result', matchedFiles[ind]['fileUrl']);
    } */
    preview_image('.panel-match-file', res['masterPdfUrl']);
    preview_match(res['masterJpgUrl'], res['imageUrl'], res['accuracy'], res['match'], res['ismatch'], res['score']);
}

function viewNextMatchFile(step){
    curViewMatchFileIndex += step;
    curViewMatchFileIndex = curViewMatchFileIndex % matchedFiles.length;
    if(curViewMatchFileIndex < 0) curViewMatchFileIndex += matchedFiles.length;
    showMatchFiles(curViewMatchFileIndex);
}