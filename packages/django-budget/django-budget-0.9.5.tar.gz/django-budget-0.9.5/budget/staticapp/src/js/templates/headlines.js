(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["headlines/root-view"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<nav class=\"navbar navbar-inverse\">\n    <div class=\"container-fluid\">\n      <div class=\"navbar-header\">\n        <a class=\"navbar-brand\" href=\"#\">\n          <img src=\"https://s3.amazonaws.com/datalab-assets/static/foiatracker/foia-tracker-logo.svg\" alt=\"FOIAtracker logo\">\n        </a>\n      </div>\n      <p class=\"navbar-text navbar-right\">\n         <i class=\"fa fa-lock\"></i>\n      </p>\n    </div>\n  </nav>\n  <div id=\"snackbar\">\n\n\n  </div>\n\n<div class=\"container\">\n  <div class=\"page-header\">\n    <h1>All records requests</h1>\n  </div>\n\n    <div class=\"panel-with-actions\">\n      <div class=\"panel panel-default\">\n        <div class=\"panel-body\">\n          <div class=\"row\">\n            <div class=\"col-xs-12 col-sm-8\">\n              <h2>FOIA request CBP-2016-030639 on credible fear for minors</h2>\n\n                <p><i class=\"fa fa-circle status-pending\"></i> Awaiting agency response</p>\n\n            </div>\n            <div class=\"col-xs-12 col-sm-4\">\n              <p class=\"text-label text-right\">From:</strong> Solis</p>\n              <p class=\"text-label text-right\">To:</strong> foia@postbox.dallasnews.com</p>\n            </div>\n          </div>\n        </div>\n        <div class=\"panel-footer\">\n          <i class=\"fa fa-calendar\"></i> April 22, 2016\n\n\n              <span class=\"pull-right hidden-xs\"><i class=\"fa fa-plus\"></i> 1 update</span>\n\n\n        </div>\n      </div>\n      <div class=\"panel-actions\">\n        <a class=\"btn btn-primary\" href=\"/foiatracker/request/5/\"><i class=\"fa fa-edit\"></i></a>\n        <a class=\"btn btn-primary\" href=\"/foiatracker/event/add/?foia=5\"><i class=\"fa fa-plus\"></i></a>\n      </div>\n    </div>\n\n</div>\n\n<div class=\"text-center\">\n\n\n    <ul class=\"pagination\">\n\n        <li class=\"prev disabled\">\n            <a href=\"#\">&laquo;</a>\n        </li>\n\n\n\n\n            <li class=\"active\">\n                <a href=\"#\">1</a>\n            </li>\n\n\n\n\n        <li class=\"last disabled\">\n            <a href=\"#\">&raquo;</a>\n        </li>\n\n    </ul>\n\n\n\n</div>";
if(parentTemplate) {
parentTemplate.rootRenderFunc(env, context, frame, runtime, cb);
} else {
cb(null, output);
}
;
} catch (e) {
  cb(runtime.handleError(e, lineno, colno));
}
}
return {
root: root
};

})();
})();
