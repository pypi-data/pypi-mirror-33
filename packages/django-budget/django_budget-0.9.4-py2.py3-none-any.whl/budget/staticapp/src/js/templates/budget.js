(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/additional-content-form"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div class=\"content-header\"><span class=\"package-title\">New additional content</span><i class=\"fa fa-times delete-additional\" data-confirm=\"\"></i></div>\n\n<div class=\"row\">\n    <div class=\"medium-4 columns form-group\">\n        <input id=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_type\" class=\"field-type to-selectize\" name=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_type\" type=\"text\" placeholder=\"Choose an option\" value=\"\" required=\"\" />\n        <label for=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_type\" class=\"control-label\">Type<span class=\"required-marker\">*</span></label>\n        <i class=\"bar\"></i>\n        <div class=\"form-help\"></div>\n    </div>\n    <div class=\"medium-3 columns form-group variable-attribute-group\">\n        <div class=\"length-group variable-attribute\">\n            <input id=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_length\" class=\"field-length form-select-word-count\" name=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_length\" data-form=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "\" type=\"number\" value=\"\" required=\"\" />\n            <label for=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_length\" class=\"control-label\">Word count</label>\n            <i class=\"bar\"></i>\n            <div class=\"form-help\"></div>\n        </div>\n\n        ";
if(runtime.contextOrFrameLookup(context, frame, "visualsRequestURL")) {
output += "\n        <div class=\"request-link-group variable-attribute\">\n            <div class=\"request-button-holder\">\n                <div class=\"request-link material-button flat-button\"><a href=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "visualsRequestURL"), env.opts.autoescape);
output += "\" target=\"_blank\"><span>Request visuals</span></a></div>\n            </div>\n        </div>\n        ";
;
}
output += "\n    </div>\n    <div class=\"medium-6 columns\"></div>\n</div>\n\n<div class=\"row\">\n    <div class=\"medium-12 columns form-group\">\n        <div class=\"slug-group-holder\">\n            <div class=\"primary-content-slug\"></div>\n            <div class=\"keyword-group\">\n                <div class=\"keyword-value\">keyword</div>\n                <input id=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_slugkey\" class=\"field-slugkey\" name=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_slugkey\" data-form=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "\" type=\"text\" placeholder=\"keyword\" autocomplete=\"off\" required=\"\" maxlength=\"20\">\n            </div>\n            <div class=\"slug-suffix\"></div>\n            <div class=\"clearer\"></div>\n        </div>\n        <label for=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_slugkey\" class=\"control-label\">Slug<span class=\"required-marker\">*</span></label>\n        <i class=\"bar\"></i>\n        <div class=\"form-help\"></div>\n\n    </div>\n    <div class=\"medium-6 columns\"></div>\n</div>\n\n<div class=\"row\">\n    <!--  -->\n    <div class=\"medium-12 columns form-group\">\n        <div class=\"expanding-holder\">\n            <textarea id=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_budgetline\" class=\"field-budgetline\" name=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_budgetline\" data-form=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "\" rows=\"1\" required=\"\"></textarea>\n            <pre class=\"budget-spacer\"><span></span><br></pre>\n        </div>\n        <label for=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_budgetline\" class=\"control-label\">Budget line<span class=\"required-marker\">*</span></label>\n        <i class=\"bar\"></i>\n        <div class=\"form-help\"></div>\n    </div>\n</div>\n\n<div class=\"row\">\n    <div class=\"medium-6 columns form-group set-authors\">\n        <input id=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_authors\" class=\"field-authors to-selectize staff-select reporter\" name=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_authors\" data-form=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "\" type=\"text\" value=\"\" />\n        <label for=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_authors\" class=\"control-label\">Author(s)<span class=\"required-marker\">*</span></label>\n        <i class=\"bar\"></i>\n        <div class=\"form-help\"></div>\n    </div>\n    <div class=\"medium-6 columns form-group set-editors\">\n        <input id=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_editors\" class=\"field-editors to-selectize staff-select editor\" name=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_editors\" data-form=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "\" type=\"text\" value=\"\" />\n        <label for=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "formID"), env.opts.autoescape);
output += "_editors\" class=\"control-label\">Editor(s)</label>\n        <i class=\"bar\"></i>\n        <div class=\"form-help\"></div>\n    </div>\n</div>\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/list-components-print-daily-title"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div class=\"accent-line-holder\">\n    <div class=\"double-line\"></div>\n</div>\n<img class=\"the-daily\" src=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "printLogoURL"), env.opts.autoescape);
output += "\" alt=\"The Daily\" />\n<div class=\"accent-line-holder\">\n    <div class=\"double-line\"></div>\n</div>\n<div class=\"clearer\"></div>\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/list-components-print-placement-toggle"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div class=\"icon-holder column small-1 medium-1 large-1\">\n    <i class=\"fa fa-newspaper-o\"></i>\n</div>\n\n<div class=\"toggle-holder column small-11 medium-11 large-11\">\n    <div class=\"\">\n        <input id=\"publication-search-box\" name=\"publication-search-box\" type=\"text\" placeholder=\"Choose a publication...\" />\n    </div>\n</div>\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/main-content"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<h1>Rendered.</h1>";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/modal-base"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div class=\"modal-inner\">\n    <h1>";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "modalTitle"), env.opts.autoescape);
output += "</h1>\n    ";
if(runtime.contextOrFrameLookup(context, frame, "formConfig")) {
output += "<form id=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "innerID"), env.opts.autoescape);
output += "\" action=\".\" method=\"POST\" data-abide=\"ajax\">";
;
}
else {
output += "<div id=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "innerID"), env.opts.autoescape);
output += "\" class=\"form-replacement\">";
;
}
output += "\n        ";
frame = frame.push();
var t_3 = runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "formConfig")),"rows");
if(t_3) {var t_2 = t_3.length;
for(var t_1=0; t_1 < t_3.length; t_1++) {
var t_4 = t_3[t_1];
frame.set("row", t_4);
frame.set("loop.index", t_1 + 1);
frame.set("loop.index0", t_1);
frame.set("loop.revindex", t_2 - t_1);
frame.set("loop.revindex0", t_2 - t_1 - 1);
frame.set("loop.first", t_1 === 0);
frame.set("loop.last", t_1 === t_2 - 1);
frame.set("loop.length", t_2);
output += "\n\n        ";
if(runtime.memberLookup((t_4),"rowHeader")) {
output += "\n        <div class=\"section-header";
if(runtime.memberLookup((t_4),"rowHeaderExtraClasses")) {
output += " ";
output += runtime.suppressValue(runtime.memberLookup((t_4),"rowHeaderExtraClasses"), env.opts.autoescape);
;
}
output += "\">\n            <h4>";
output += runtime.suppressValue(runtime.memberLookup((t_4),"rowHeader"), env.opts.autoescape);
output += "</h4>\n        </div>\n        ";
;
}
output += "\n\n        <div ";
if(runtime.memberLookup((t_4),"id")) {
output += "id=\"";
output += runtime.suppressValue(runtime.memberLookup((t_4),"id"), env.opts.autoescape);
output += "\" ";
;
}
output += "class=\"row";
if(runtime.memberLookup((t_4),"extraClasses")) {
output += " ";
output += runtime.suppressValue(runtime.memberLookup((t_4),"extraClasses"), env.opts.autoescape);
;
}
output += "\">\n            ";
if(runtime.memberLookup((t_4),"rowType") == "radio-buttons") {
output += "\n                <div class=\"medium-12 columns form-radio\">\n            ";
;
}
output += "\n\n            ";
frame = frame.push();
var t_7 = runtime.memberLookup((t_4),"fields");
if(t_7) {var t_6 = t_7.length;
for(var t_5=0; t_5 < t_7.length; t_5++) {
var t_8 = t_7[t_5];
frame.set("field", t_8);
frame.set("loop.index", t_5 + 1);
frame.set("loop.index0", t_5);
frame.set("loop.revindex", t_6 - t_5);
frame.set("loop.revindex0", t_6 - t_5 - 1);
frame.set("loop.first", t_5 === 0);
frame.set("loop.last", t_5 === t_6 - 1);
frame.set("loop.length", t_6);
output += "\n                ";
if(runtime.memberLookup((t_8),"type") == "input") {
output += "\n                <div class=\"form-element form-group column ";
output += runtime.suppressValue(runtime.memberLookup((t_8),"widthClasses"), env.opts.autoescape);
output += " ";
output += runtime.suppressValue(runtime.memberLookup((t_8),"extraClasses"), env.opts.autoescape);
output += "\">\n                    <input name=\"";
output += runtime.suppressValue(runtime.memberLookup((t_8),"inputName"), env.opts.autoescape);
output += "\" type=\"";
output += runtime.suppressValue(runtime.memberLookup((t_8),"inputType"), env.opts.autoescape);
output += "\" id=\"";
output += runtime.suppressValue(runtime.memberLookup((t_8),"inputID"), env.opts.autoescape);
output += "\">\n                    <label for=\"";
output += runtime.suppressValue(runtime.memberLookup((t_8),"inputID"), env.opts.autoescape);
output += "\" class=\"control-label\">";
output += runtime.suppressValue(runtime.memberLookup((t_8),"labelText"), env.opts.autoescape);
output += "</label>\n                    <i class=\"bar\"></i>\n                    <div class=\"form-help\"></div>\n                </div>\n                ";
;
}
else {
if(runtime.memberLookup((t_8),"type") == "radio") {
output += "\n                    <div class=\"form-element form-radio\">\n                        <label>\n                            <input id=\"";
output += runtime.suppressValue(runtime.memberLookup((t_8),"inputID"), env.opts.autoescape);
output += "\" name=\"";
output += runtime.suppressValue(runtime.memberLookup((t_8),"groupName"), env.opts.autoescape);
output += "\" type=\"radio\" value=\"";
if(runtime.memberLookup((t_8),"inputValue")) {
output += runtime.suppressValue(runtime.memberLookup((t_8),"inputValue"), env.opts.autoescape);
;
}
output += "\"";
if(runtime.memberLookup((t_8),"isChecked")) {
output += " checked";
;
}
if(runtime.memberLookup((t_8),"isDisabled")) {
output += " disabled";
;
}
output += " /><i class=\"helper\"></i><span class=\"radio-label\">";
output += runtime.suppressValue(env.getFilter("safe").call(context, runtime.memberLookup((t_8),"labelText")), env.opts.autoescape);
output += "</span>\n                        </label>\n                    </div>\n                ";
;
}
else {
if(runtime.memberLookup((t_8),"type") == "checkbox") {
output += "\n                    <div class=\"form-element column ";
output += runtime.suppressValue(runtime.memberLookup((t_8),"widthClasses"), env.opts.autoescape);
output += " checkbox ";
output += runtime.suppressValue(runtime.memberLookup((t_8),"extraClasses"), env.opts.autoescape);
output += "\">\n                        <label>\n                            <input id=\"";
output += runtime.suppressValue(runtime.memberLookup((t_8),"inputID"), env.opts.autoescape);
output += "\" name=\"";
output += runtime.suppressValue(runtime.memberLookup((t_8),"groupName"), env.opts.autoescape);
output += "\" type=\"checkbox\" value=\"";
output += runtime.suppressValue(runtime.memberLookup((t_8),"inputValue"), env.opts.autoescape);
output += "\"";
if(runtime.memberLookup((t_8),"isChecked")) {
output += " checked";
;
}
output += " /><i class=\"helper\"></i>";
output += runtime.suppressValue(env.getFilter("safe").call(context, runtime.memberLookup((t_8),"labelText")), env.opts.autoescape);
output += "\n                        </label>\n                    </div>\n                ";
;
}
else {
if(runtime.memberLookup((t_8),"type") == "div") {
output += "\n                    <div id=\"";
output += runtime.suppressValue(runtime.memberLookup((t_8),"inputID"), env.opts.autoescape);
output += "\" class=\"form-element column ";
output += runtime.suppressValue(runtime.memberLookup((t_8),"extraClasses"), env.opts.autoescape);
output += " ";
output += runtime.suppressValue(runtime.memberLookup((t_8),"widthClasses"), env.opts.autoescape);
output += "\"></div>\n                ";
;
}
;
}
;
}
;
}
output += "\n            ";
;
}
}
frame = frame.pop();
output += "\n\n            ";
if(runtime.memberLookup((t_4),"rowType") == "radio-buttons") {
output += "\n                </div>\n            ";
;
}
output += "\n\n            ";
if(runtime.memberLookup((t_4),"extraHTML")) {
output += "\n            ";
output += runtime.suppressValue(env.getFilter("safe").call(context, runtime.memberLookup((t_4),"extraHTML")), env.opts.autoescape);
output += "\n            ";
;
}
output += "\n            <div class=\"clearer\"></div>\n        </div>\n        ";
;
}
}
frame = frame.pop();
output += "\n\n        ";
if(runtime.contextOrFrameLookup(context, frame, "extraHTML")) {
output += "\n            ";
output += runtime.suppressValue(env.getFilter("safe").call(context, runtime.contextOrFrameLookup(context, frame, "extraHTML")), env.opts.autoescape);
output += "\n        ";
;
}
output += "\n\n        <div class=\"button-holder\">\n            ";
frame = frame.push();
var t_11 = runtime.contextOrFrameLookup(context, frame, "buttons");
if(t_11) {var t_10 = t_11.length;
for(var t_9=0; t_9 < t_11.length; t_9++) {
var t_12 = t_11[t_9];
frame.set("button", t_12);
frame.set("loop.index", t_9 + 1);
frame.set("loop.index0", t_9);
frame.set("loop.revindex", t_10 - t_9);
frame.set("loop.revindex0", t_10 - t_9 - 1);
frame.set("loop.first", t_9 === 0);
frame.set("loop.last", t_9 === t_10 - 1);
frame.set("loop.length", t_10);
output += "\n            ";
if(!runtime.memberLookup((t_12),"hidden")) {
output += "\n            <div id=\"";
output += runtime.suppressValue(runtime.memberLookup((t_12),"buttonID"), env.opts.autoescape);
output += "\" class=\"material-button ";
output += runtime.suppressValue(runtime.memberLookup((t_12),"buttonClass"), env.opts.autoescape);
output += " click-init\"><span>";
output += runtime.suppressValue(runtime.memberLookup((t_12),"innerLabel"), env.opts.autoescape);
output += "</span></div>\n            ";
;
}
output += "\n            ";
;
}
}
frame = frame.pop();
output += "\n            <div class=\"clearer\"></div>\n        </div>\n    ";
if(runtime.contextOrFrameLookup(context, frame, "formConfig")) {
output += "</form>";
;
}
else {
output += "</div>";
;
}
output += "\n</div>\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/navigation-logo"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<a href=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "homeViewLink"), env.opts.autoescape);
output += "\" class=\"\">\n    <img class=\"masthead\" src=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "mastheadLogoURL"), env.opts.autoescape);
output += "\" alt=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "mastheadLogoAltText"), env.opts.autoescape);
output += "\" />\n    <img class=\"budget-wordmark\" src=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "siteLogoURL"), env.opts.autoescape);
output += "\" alt=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "siteLogoAltText"), env.opts.autoescape);
output += "\" />\n</a>\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/navigation-user-info"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<tag class=\"white\">";
frame = frame.push();
var t_3 = runtime.contextOrFrameLookup(context, frame, "links");
if(t_3) {var t_2 = t_3.length;
for(var t_1=0; t_1 < t_3.length; t_1++) {
var t_4 = t_3[t_1];
frame.set("link", t_4);
frame.set("loop.index", t_1 + 1);
frame.set("loop.index0", t_1);
frame.set("loop.revindex", t_2 - t_1);
frame.set("loop.revindex0", t_2 - t_1 - 1);
frame.set("loop.first", t_1 === 0);
frame.set("loop.last", t_1 === t_2 - 1);
frame.set("loop.length", t_2);
output += "<a href=\"";
output += runtime.suppressValue(runtime.memberLookup((t_4),"destination"), env.opts.autoescape);
output += "\">";
output += runtime.suppressValue(runtime.memberLookup((t_4),"name"), env.opts.autoescape);
output += "</a>&nbsp;&thinsp;|&thinsp;&nbsp";
;
}
}
frame = frame.pop();
if(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "currentUser")),"email")) {
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "currentUser")),"email"), env.opts.autoescape);
;
}
else {
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "currentUser")),"username"), env.opts.autoescape);
;
}
output += " <i class=\"fa fa-lock neon\"></i></tag>\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/navigation"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div id=\"logo-holder\" class=\"top-bar-left\"></div>\n<div id=\"user-info-holder\" class=\"top-bar-right\"></div>\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/package-empty"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<h3>No content matched your search.</h3>\n<p>Remove some filters to see more matches.</p>";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/package-item-print-additionalcontent"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "        <li class=\"content-item\" ready=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"isReady"), env.opts.autoescape);
output += "\" content-id=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"id"), env.opts.autoescape);
output += "\">\n            <div class=\"row\">\n                <div class=\"visible-area column small-11 medium-11 large-11\">\n                    <div class=\"slug-bar row\">\n                        <div class=\"date-slug column small-6 medium-7 large-7\">\n                            <h3 class=\"might-overflow\">";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"slug"), env.opts.autoescape);
output += "</h3>\n                        </div>\n                        <div class=\"author-info column small-6 medium-5 large-5\">\n                            ";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors")) > 0) {
output += "\n                            <h4 class=\"might-overflow\">";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors")) == 1) {
output += "Author";
;
}
else {
output += "Authors";
;
}
output += ": ";
frame = frame.push();
var t_3 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors");
if(t_3) {var t_2 = t_3.length;
for(var t_1=0; t_1 < t_3.length; t_1++) {
var t_4 = t_3[t_1];
frame.set("author", t_4);
frame.set("loop.index", t_1 + 1);
frame.set("loop.index0", t_1);
frame.set("loop.revindex", t_2 - t_1);
frame.set("loop.revindex0", t_2 - t_1 - 1);
frame.set("loop.first", t_1 === 0);
frame.set("loop.last", t_1 === t_2 - 1);
frame.set("loop.length", t_2);
output += runtime.suppressValue(runtime.memberLookup((t_4),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
output += "</h4>\n                            ";
;
}
output += "\n\n                            ";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors")) > 0) {
output += "\n                            <h4 class=\"might-overflow\">";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors")) == 1) {
output += "Editor";
;
}
else {
output += "Editors";
;
}
output += ": ";
frame = frame.push();
var t_7 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors");
if(t_7) {var t_6 = t_7.length;
for(var t_5=0; t_5 < t_7.length; t_5++) {
var t_8 = t_7[t_5];
frame.set("editor", t_8);
frame.set("loop.index", t_5 + 1);
frame.set("loop.index0", t_5);
frame.set("loop.revindex", t_6 - t_5);
frame.set("loop.revindex0", t_6 - t_5 - 1);
frame.set("loop.first", t_5 === 0);
frame.set("loop.last", t_5 === t_6 - 1);
frame.set("loop.length", t_6);
output += runtime.suppressValue(runtime.memberLookup((t_8),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
output += "</h4>\n                            ";
;
}
output += "\n                        </div>\n                    </div>\n\n                    <div class=\"contents-bar row\">\n                        <div class=\"column small-6 medium-8 large-8 text-left\">\n                            <div class=\"additional-info-line\"><i class=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"typeMeta")),"icon"), env.opts.autoescape);
output += "\"></i>&thinsp;&nbsp;";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"typeMeta")),"verboseName"), env.opts.autoescape);
if(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"length")) {
output += " (";
output += runtime.suppressValue(env.getFilter("numberWithCommas").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"length")), env.opts.autoescape);
output += " words)";
;
}
output += "</div>\n                        </div>\n                        <div class=\"column small-6 medium-4 large-4 text-center\">\n                        </div>\n                    </div>\n\n                    <div class=\"related-description row\">\n                        <div class=\"budget-line column small-12 medium-12 large-12\">\n                            <div class=\"mobile-author-info\">\n                                <p>";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors")) > 0) {
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors")) == 1) {
output += "Author";
;
}
else {
output += "Authors";
;
}
output += ": ";
frame = frame.push();
var t_11 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors");
if(t_11) {var t_10 = t_11.length;
for(var t_9=0; t_9 < t_11.length; t_9++) {
var t_12 = t_11[t_9];
frame.set("author", t_12);
frame.set("loop.index", t_9 + 1);
frame.set("loop.index0", t_9);
frame.set("loop.revindex", t_10 - t_9);
frame.set("loop.revindex0", t_10 - t_9 - 1);
frame.set("loop.first", t_9 === 0);
frame.set("loop.last", t_9 === t_10 - 1);
frame.set("loop.length", t_10);
output += runtime.suppressValue(runtime.memberLookup((t_12),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors")) > 0) {
output += "&nbsp;/&nbsp;";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors")) == 1) {
output += "Editor";
;
}
else {
output += "Editors";
;
}
output += ": ";
frame = frame.push();
var t_15 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors");
if(t_15) {var t_14 = t_15.length;
for(var t_13=0; t_13 < t_15.length; t_13++) {
var t_16 = t_15[t_13];
frame.set("editor", t_16);
frame.set("loop.index", t_13 + 1);
frame.set("loop.index0", t_13);
frame.set("loop.revindex", t_14 - t_13);
frame.set("loop.revindex0", t_14 - t_13 - 1);
frame.set("loop.first", t_13 === 0);
frame.set("loop.last", t_13 === t_14 - 1);
frame.set("loop.length", t_14);
output += runtime.suppressValue(runtime.memberLookup((t_16),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
output += "</p>\n                            </div>\n\n                            ";
if(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"budgetLine")) {
output += "\n                            <p>";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"budgetLine"), env.opts.autoescape);
output += "</p>\n                            ";
;
}
else {
output += "\n                            <p>(None specified)</p>\n                            ";
;
}
output += "\n                        </div>\n                    </div>\n\n                </div>\n                <div class=\"knockout column small-1 medium-1 large-1\"></div>\n            </div>\n        </li>";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/package-item-print"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div class=\"package-sheet";
if(runtime.contextOrFrameLookup(context, frame, "primaryIsExpanded")) {
output += " is-expanded";
;
}
output += " row";
if(runtime.contextOrFrameLookup(context, frame, "hasPrimary")) {
output += " has-primary";
;
}
output += "\" content-id=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"id"), env.opts.autoescape);
output += "\" content-primary-id=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"id"), env.opts.autoescape);
output += "\" data-hub=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"hub"), env.opts.autoescape);
output += "\" data-vertical=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "verticalSlug"), env.opts.autoescape);
output += "\" data-all-people=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "allPeople"), env.opts.autoescape);
output += "\" data-full-text=\"\" has-url=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "packageHasURL"), env.opts.autoescape);
output += "\">\n\n    <div class=\"minimal-card column small-11 medium-11 large-11\">\n        ";
if(runtime.contextOrFrameLookup(context, frame, "packageObj")) {
if(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"publishedUrl")) {
output += "<a href=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"publishedUrl"), env.opts.autoescape);
output += "\" target=\"_blank\">";
;
}
;
}
output += "\n        <div class=\"readiness-indicator\">\n            <div class=\"indicator-inner\">\n                <i class=\"fa fa-check\"></i>\n            </div>\n        </div>\n        ";
if(runtime.contextOrFrameLookup(context, frame, "packageObj")) {
if(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"publishedUrl")) {
output += "</a>";
;
}
;
}
output += "\n\n        <div class=\"slug-bar row\">\n            <div class=\"date-slug-budget-line column small-7 medium-9 large-9\">\n                <div class=\"color-dot\" style=\"background-color: ";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "hubDotColor"), env.opts.autoescape);
output += ";\"></div>\n                <h2 class=\"date-header\">";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "verticalName"), env.opts.autoescape);
output += "&nbsp;/&nbsp;";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "hubName"), env.opts.autoescape);
output += "&nbsp;&nbsp;&bull;&nbsp;&nbsp;";
if(env.getFilter("length").call(context, runtime.contextOrFrameLookup(context, frame, "placementTypes")) > 0) {
frame = frame.push();
var t_3 = runtime.contextOrFrameLookup(context, frame, "placementTypes");
if(t_3) {var t_2 = t_3.length;
for(var t_1=0; t_1 < t_3.length; t_1++) {
var t_4 = t_3[t_1];
frame.set("placement", t_4);
frame.set("loop.index", t_1 + 1);
frame.set("loop.index0", t_1);
frame.set("loop.revindex", t_2 - t_1);
frame.set("loop.revindex0", t_2 - t_1 - 1);
frame.set("loop.first", t_1 === 0);
frame.set("loop.last", t_1 === t_2 - 1);
frame.set("loop.length", t_2);
output += runtime.suppressValue(t_4, env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
else {
output += "No placements";
;
}
if(runtime.contextOrFrameLookup(context, frame, "placementPageNumber")) {
output += " (Page&nbsp;";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "placementPageNumber"), env.opts.autoescape);
output += ")";
;
}
output += "</h2>\n                <h1 class=\"primary-slug might-overflow\">";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"budgetLine"), env.opts.autoescape);
output += "</h1>\n                <h4 class=\"budget-line-truncated might-overflow\"><i class=\"fa fa-fw fa-newspaper-o\"></i>";
if(runtime.contextOrFrameLookup(context, frame, "packageObj")) {
if(!runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"printPlacement")),"isFinalized")) {
output += "Planned for ";
;
}
else {
output += "Set for ";
;
}
output += runtime.suppressValue(env.getFilter("safe").call(context, runtime.contextOrFrameLookup(context, frame, "formattedRunDateRange")), env.opts.autoescape);
;
}
output += "</h4>\n            </div>\n            <div class=\"author-info column small-5 medium-3 large-3\">\n                <h3 class=\"additional-info-line package-slug\"><span>";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"slugKey"), env.opts.autoescape);
output += ".";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"slugDate"), env.opts.autoescape);
output += "</span></h3>\n\n                <div class=\"staff-info\">\n                    <h3 class=\"might-overflow\">";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors")) > 0) {
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors")) == 1) {
output += "Author";
;
}
else {
output += "Authors";
;
}
output += ": ";
frame = frame.push();
var t_7 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors");
if(t_7) {var t_6 = t_7.length;
for(var t_5=0; t_5 < t_7.length; t_5++) {
var t_8 = t_7[t_5];
frame.set("author", t_8);
frame.set("loop.index", t_5 + 1);
frame.set("loop.index0", t_5);
frame.set("loop.revindex", t_6 - t_5);
frame.set("loop.revindex0", t_6 - t_5 - 1);
frame.set("loop.first", t_5 === 0);
frame.set("loop.last", t_5 === t_6 - 1);
frame.set("loop.length", t_6);
output += runtime.suppressValue(runtime.memberLookup((t_8),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
output += "</h3>\n\n                    <h3 class=\"additional-info-line might-overflow\">";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors")) > 0) {
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors")) == 1) {
output += "Editor";
;
}
else {
output += "Editors";
;
}
output += ": ";
frame = frame.push();
var t_11 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors");
if(t_11) {var t_10 = t_11.length;
for(var t_9=0; t_9 < t_11.length; t_9++) {
var t_12 = t_11[t_9];
frame.set("editor", t_12);
frame.set("loop.index", t_9 + 1);
frame.set("loop.index0", t_9);
frame.set("loop.revindex", t_10 - t_9);
frame.set("loop.revindex0", t_10 - t_9 - 1);
frame.set("loop.first", t_9 === 0);
frame.set("loop.last", t_9 === t_10 - 1);
frame.set("loop.length", t_10);
output += runtime.suppressValue(runtime.memberLookup((t_12),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
output += "</h3>\n                </div>\n            </div>\n        </div>\n        <div class=\"contents-bar row\">\n            <div class=\"primary-type column small-6 medium-6 large-6 text-left\">\n                <div class=\"additional-info-line\"><i class=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "primaryTypeMeta")),"icon"), env.opts.autoescape);
output += "\"></i>&thinsp;&nbsp;";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "primaryTypeMeta")),"verboseName"), env.opts.autoescape);
if(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"length")) {
output += " (";
output += runtime.suppressValue(env.getFilter("numberWithCommas").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"length")), env.opts.autoescape);
output += " words)";
;
}
output += "</div>\n            </div>\n            <div class=\"related-types column small-6 medium-6 large-6 text-right\"><div class=\"additional-info-line\">";
if(env.getFilter("length").call(context, runtime.contextOrFrameLookup(context, frame, "additionalItemTypes")) > 0) {
output += "Includes ";
frame = frame.push();
var t_15 = runtime.contextOrFrameLookup(context, frame, "additionalItemTypes");
if(t_15) {var t_14 = t_15.length;
for(var t_13=0; t_13 < t_15.length; t_13++) {
var t_16 = t_15[t_13];
frame.set("type", t_16);
frame.set("loop.index", t_13 + 1);
frame.set("loop.index0", t_13);
frame.set("loop.revindex", t_14 - t_13);
frame.set("loop.revindex0", t_14 - t_13 - 1);
frame.set("loop.first", t_13 === 0);
frame.set("loop.last", t_13 === t_14 - 1);
frame.set("loop.length", t_14);
output += "<i class=\"";
output += runtime.suppressValue(runtime.memberLookup((t_16),"icon"), env.opts.autoescape);
output += "\"></i>";
;
}
}
frame = frame.pop();
;
}
output += "</div>\n            </div>\n        </div>\n\n        <div class=\"primary-description row";
if(runtime.contextOrFrameLookup(context, frame, "primaryIsExpanded")) {
output += " overflow-visible";
;
}
output += "\">\n            <div class=\"budget-line collapsed column small-12 medium-12 large-12\">\n                <div class=\"item-options\">\n                    <div class=\"option-list\">\n                        <div class=\"web-info option\">\n                            <i class=\"fa fa-fw fa-desktop\"></i>\n                            <span class=\"hover-info\">Web publishing</span>\n                        </div>\n                        <div class=\"print-info option\">\n                            <i class=\"fa fa-fw fa-newspaper-o\"></i>\n                            <span class=\"hover-info\">Print publishing</span>\n                        </div>\n                    </div>\n                </div>\n\n                <div class=\"mobile-author-info\">\n                    <p>";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors")) > 0) {
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors")) == 1) {
output += "Author";
;
}
else {
output += "Authors";
;
}
output += ": ";
frame = frame.push();
var t_19 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors");
if(t_19) {var t_18 = t_19.length;
for(var t_17=0; t_17 < t_19.length; t_17++) {
var t_20 = t_19[t_17];
frame.set("author", t_20);
frame.set("loop.index", t_17 + 1);
frame.set("loop.index0", t_17);
frame.set("loop.revindex", t_18 - t_17);
frame.set("loop.revindex0", t_18 - t_17 - 1);
frame.set("loop.first", t_17 === 0);
frame.set("loop.last", t_17 === t_18 - 1);
frame.set("loop.length", t_18);
output += runtime.suppressValue(runtime.memberLookup((t_20),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors")) > 0) {
output += "&nbsp;/&nbsp;";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors")) == 1) {
output += "Editor";
;
}
else {
output += "Editors";
;
}
output += ": ";
frame = frame.push();
var t_23 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors");
if(t_23) {var t_22 = t_23.length;
for(var t_21=0; t_21 < t_23.length; t_21++) {
var t_24 = t_23[t_21];
frame.set("editor", t_24);
frame.set("loop.index", t_21 + 1);
frame.set("loop.index0", t_21);
frame.set("loop.revindex", t_22 - t_21);
frame.set("loop.revindex0", t_22 - t_21 - 1);
frame.set("loop.first", t_21 === 0);
frame.set("loop.last", t_21 === t_22 - 1);
frame.set("loop.length", t_22);
output += runtime.suppressValue(runtime.memberLookup((t_24),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
output += "</p>\n                </div>\n\n                <p>";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"budgetLine"), env.opts.autoescape);
output += "</p>\n\n                <div class=\"mobile-action-buttons\">\n                    <div class=\"action-button material-button edit-package\">\n                        <a href=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "homeViewLink"), env.opts.autoescape);
output += "edit/";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"id"), env.opts.autoescape);
output += "/\">\n                            <div class=\"button-contents\">\n                                <div class=\"button-innermost\">\n                                    <i class=\"fa fa-fw fa-pencil-square-o\"></i>\n                                    <div class=\"action-text\">Edit</div>\n                                    <div class=\"clearer\"></div>\n                                </div>\n                            </div>\n                        </a>\n                    </div>\n                    <div class=\"action-button material-button view-notes\">\n                        <div class=\"button-contents\">\n                            <div class=\"button-innermost\">\n                                <i class=\"fa fa-fw fa-paragraph\"></i>\n                                <div class=\"action-text\">Notes</div>\n                                <div class=\"clearer\"></div>\n                            </div>\n                        </div>\n                    </div>\n                    <div class=\"action-button material-button subscribe\">\n                        <div class=\"button-contents\">\n                            <div class=\"button-innermost\">\n                                <i class=\"fa fa-fw fa-slack\"></i>\n                                <div class=\"action-text\">Subscribe</div>\n                                <div class=\"clearer\"></div>\n                            </div>\n                        </div>\n                    </div>\n                    <div class=\"clearer\"></div>\n                </div>\n\n                <div class=\"clearer\"></div>\n            </div>\n        </div>\n    </div>\n    <div class=\"action-buttons column small-1 medium-1 large-1 text-center\">\n        <div class=\"edit-package action-button\">\n            <a href=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "homeViewLink"), env.opts.autoescape);
output += "edit/";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"id"), env.opts.autoescape);
output += "/\">\n                <i class=\"fa fa-pencil-square-o\"></i>\n                <span class=\"hover-info\">Edit</span>\n            </a>\n        </div>\n        <div class=\"view-notes action-button\">\n            <i class=\"fa fa-paragraph\"></i>\n            <span class=\"hover-info\">Notes</span>\n        </div>\n        <div class=\"subscribe action-button\">\n            <i class=\"fa fa-slack\"></i>\n            <span class=\"hover-info\">Subscribe</span>\n        </div>\n        <div class=\"expand-package action-button\">\n            <i class=\"fa fa-plus\"></i>\n            <i class=\"fa fa-minus\"></i>\n            <span class=\"hover-info\">More info</span>\n        </div>\n    </div>\n    <div class=\"clearer\"></div>\n</div>\n";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"additionalContent")) > 0) {
output += "\n<div class=\"extra-sheet\">\n    <ul class=\"related-content\">\n        ";
frame = frame.push();
var t_27 = runtime.contextOrFrameLookup(context, frame, "additionalWithTypeMetas");
if(t_27) {var t_26 = t_27.length;
for(var t_25=0; t_25 < t_27.length; t_25++) {
var t_28 = t_27[t_25];
frame.set("item", t_28);
frame.set("loop.index", t_25 + 1);
frame.set("loop.index0", t_25);
frame.set("loop.revindex", t_26 - t_25);
frame.set("loop.revindex0", t_26 - t_25 - 1);
frame.set("loop.first", t_25 === 0);
frame.set("loop.last", t_25 === t_26 - 1);
frame.set("loop.length", t_26);
output += "\n            ";
env.getTemplate("budget/package-item-print-additionalcontent", false, "budget/package-item-print", null, function(t_31,t_29) {
if(t_31) { cb(t_31); return; }
t_29.render(context.getVariables(), frame, function(t_32,t_30) {
if(t_32) { cb(t_32); return; }
output += t_30
output += "\n        ";
})});
}
}
frame = frame.pop();
output += "\n    </ul>\n</div>\n";
;
}
output += "\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/package-item-web-additionalcontent"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "        <li class=\"content-item\" ready=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"isReady"), env.opts.autoescape);
output += "\" content-id=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"id"), env.opts.autoescape);
output += "\">\n            <div class=\"row\">\n                <div class=\"visible-area column small-11 medium-11 large-11\">\n                    <div class=\"slug-bar row\">\n                        <div class=\"date-slug column small-6 medium-7 large-7\">\n                            <h3 class=\"might-overflow\">";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"slug"), env.opts.autoescape);
output += "</h3>\n                        </div>\n                        <div class=\"author-info column small-6 medium-5 large-5\">\n                            ";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors")) > 0) {
output += "\n                            <h4 class=\"might-overflow\">";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors")) == 1) {
output += "Author";
;
}
else {
output += "Authors";
;
}
output += ": ";
frame = frame.push();
var t_3 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors");
if(t_3) {var t_2 = t_3.length;
for(var t_1=0; t_1 < t_3.length; t_1++) {
var t_4 = t_3[t_1];
frame.set("author", t_4);
frame.set("loop.index", t_1 + 1);
frame.set("loop.index0", t_1);
frame.set("loop.revindex", t_2 - t_1);
frame.set("loop.revindex0", t_2 - t_1 - 1);
frame.set("loop.first", t_1 === 0);
frame.set("loop.last", t_1 === t_2 - 1);
frame.set("loop.length", t_2);
output += runtime.suppressValue(runtime.memberLookup((t_4),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
output += "</h4>\n                            ";
;
}
output += "\n\n                            ";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors")) > 0) {
output += "\n                            <h4 class=\"might-overflow\">";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors")) == 1) {
output += "Editor";
;
}
else {
output += "Editors";
;
}
output += ": ";
frame = frame.push();
var t_7 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors");
if(t_7) {var t_6 = t_7.length;
for(var t_5=0; t_5 < t_7.length; t_5++) {
var t_8 = t_7[t_5];
frame.set("editor", t_8);
frame.set("loop.index", t_5 + 1);
frame.set("loop.index0", t_5);
frame.set("loop.revindex", t_6 - t_5);
frame.set("loop.revindex0", t_6 - t_5 - 1);
frame.set("loop.first", t_5 === 0);
frame.set("loop.last", t_5 === t_6 - 1);
frame.set("loop.length", t_6);
output += runtime.suppressValue(runtime.memberLookup((t_8),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
output += "</h4>\n                            ";
;
}
output += "\n                        </div>\n                    </div>\n\n                    <div class=\"contents-bar row\">\n                        <div class=\"column small-6 medium-8 large-8 text-left\">\n                            <div class=\"additional-info-line\"><i class=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"typeMeta")),"icon"), env.opts.autoescape);
output += "\"></i>&thinsp;&nbsp;";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"typeMeta")),"verboseName"), env.opts.autoescape);
if(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"length")) {
output += " (";
output += runtime.suppressValue(env.getFilter("numberWithCommas").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"length")), env.opts.autoescape);
output += " words)";
;
}
output += "</div>\n                        </div>\n                        <div class=\"column small-6 medium-4 large-4 text-center\">\n                        </div>\n                    </div>\n\n                    <div class=\"related-description row\">\n                        <div class=\"budget-line column small-12 medium-12 large-12\">\n                            <div class=\"mobile-author-info\">\n                                <p>";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors")) > 0) {
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors")) == 1) {
output += "Author";
;
}
else {
output += "Authors";
;
}
output += ": ";
frame = frame.push();
var t_11 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"authors");
if(t_11) {var t_10 = t_11.length;
for(var t_9=0; t_9 < t_11.length; t_9++) {
var t_12 = t_11[t_9];
frame.set("author", t_12);
frame.set("loop.index", t_9 + 1);
frame.set("loop.index0", t_9);
frame.set("loop.revindex", t_10 - t_9);
frame.set("loop.revindex0", t_10 - t_9 - 1);
frame.set("loop.first", t_9 === 0);
frame.set("loop.last", t_9 === t_10 - 1);
frame.set("loop.length", t_10);
output += runtime.suppressValue(runtime.memberLookup((t_12),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors")) > 0) {
output += "&nbsp;/&nbsp;";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors")) == 1) {
output += "Editor";
;
}
else {
output += "Editors";
;
}
output += ": ";
frame = frame.push();
var t_15 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"editors");
if(t_15) {var t_14 = t_15.length;
for(var t_13=0; t_13 < t_15.length; t_13++) {
var t_16 = t_15[t_13];
frame.set("editor", t_16);
frame.set("loop.index", t_13 + 1);
frame.set("loop.index0", t_13);
frame.set("loop.revindex", t_14 - t_13);
frame.set("loop.revindex0", t_14 - t_13 - 1);
frame.set("loop.first", t_13 === 0);
frame.set("loop.last", t_13 === t_14 - 1);
frame.set("loop.length", t_14);
output += runtime.suppressValue(runtime.memberLookup((t_16),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
output += "</p>\n                            </div>\n\n                            ";
if(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"budgetLine")) {
output += "\n                            <p>";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "item")),"model")),"budgetLine"), env.opts.autoescape);
output += "</p>\n                            ";
;
}
else {
output += "\n                            <p>(None specified)</p>\n                            ";
;
}
output += "\n                        </div>\n                    </div>\n\n                </div>\n                <div class=\"knockout column small-1 medium-1 large-1\"></div>\n            </div>\n        </li>";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/package-item-web"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div class=\"package-sheet";
if(runtime.contextOrFrameLookup(context, frame, "primaryIsExpanded")) {
output += " is-expanded";
;
}
output += " row";
if(runtime.contextOrFrameLookup(context, frame, "hasPrimary")) {
output += " has-primary";
;
}
output += "\" content-id=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"id"), env.opts.autoescape);
output += "\" content-primary-id=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"id"), env.opts.autoescape);
output += "\" data-hub=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"hub"), env.opts.autoescape);
output += "\" data-vertical=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "verticalSlug"), env.opts.autoescape);
output += "\" data-all-people=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "allPeople"), env.opts.autoescape);
output += "\" data-full-text=\"\" has-url=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "packageHasURL"), env.opts.autoescape);
output += "\">\n\n    <div class=\"minimal-card column small-11 medium-11 large-11\">\n        ";
if(runtime.contextOrFrameLookup(context, frame, "packageObj")) {
if(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"publishedUrl")) {
output += "<a href=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"publishedUrl"), env.opts.autoescape);
output += "\" target=\"_blank\">";
;
}
;
}
output += "\n        <div class=\"readiness-indicator\">\n            <div class=\"indicator-inner\">\n                <i class=\"fa fa-check\"></i>\n            </div>\n        </div>\n        ";
if(runtime.contextOrFrameLookup(context, frame, "packageObj")) {
if(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"publishedUrl")) {
output += "</a>";
;
}
;
}
output += "\n\n        <div class=\"slug-bar row\">\n            <div class=\"date-slug-budget-line column small-7 medium-9 large-9\">\n                <div class=\"color-dot\" style=\"background-color: ";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "hubDotColor"), env.opts.autoescape);
output += ";\"></div>\n                <h2 class=\"date-header\">";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "verticalName"), env.opts.autoescape);
output += "&nbsp;/&nbsp;";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "hubName"), env.opts.autoescape);
output += "</h2>\n                <h1 class=\"primary-slug might-overflow\">";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"budgetLine"), env.opts.autoescape);
output += "</h1>\n                <h4 class=\"budget-line-truncated might-overflow\"><i class=\"fa fa-fw fa-desktop\"></i>";
if(runtime.contextOrFrameLookup(context, frame, "packageObj")) {
if(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"publishedUrl")) {
output += "Published";
;
}
else {
output += "Expected";
;
}
;
}
else {
output += "Expected";
;
}
output += " ";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "publishDate"), env.opts.autoescape);
output += "</h4>\n            </div>\n            <div class=\"author-info column small-5 medium-3 large-3\">\n                <h3 class=\"additional-info-line package-slug\"><span>";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"slugKey"), env.opts.autoescape);
output += ".";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"slugDate"), env.opts.autoescape);
output += "</span></h3>\n\n                <div class=\"staff-info\">\n                    <h3 class=\"might-overflow\">";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors")) > 0) {
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors")) == 1) {
output += "Author";
;
}
else {
output += "Authors";
;
}
output += ": ";
frame = frame.push();
var t_3 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors");
if(t_3) {var t_2 = t_3.length;
for(var t_1=0; t_1 < t_3.length; t_1++) {
var t_4 = t_3[t_1];
frame.set("author", t_4);
frame.set("loop.index", t_1 + 1);
frame.set("loop.index0", t_1);
frame.set("loop.revindex", t_2 - t_1);
frame.set("loop.revindex0", t_2 - t_1 - 1);
frame.set("loop.first", t_1 === 0);
frame.set("loop.last", t_1 === t_2 - 1);
frame.set("loop.length", t_2);
output += runtime.suppressValue(runtime.memberLookup((t_4),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
output += "</h3>\n\n                    <h3 class=\"additional-info-line might-overflow\">";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors")) > 0) {
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors")) == 1) {
output += "Editor";
;
}
else {
output += "Editors";
;
}
output += ": ";
frame = frame.push();
var t_7 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors");
if(t_7) {var t_6 = t_7.length;
for(var t_5=0; t_5 < t_7.length; t_5++) {
var t_8 = t_7[t_5];
frame.set("editor", t_8);
frame.set("loop.index", t_5 + 1);
frame.set("loop.index0", t_5);
frame.set("loop.revindex", t_6 - t_5);
frame.set("loop.revindex0", t_6 - t_5 - 1);
frame.set("loop.first", t_5 === 0);
frame.set("loop.last", t_5 === t_6 - 1);
frame.set("loop.length", t_6);
output += runtime.suppressValue(runtime.memberLookup((t_8),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
output += "</h3>\n                </div>\n            </div>\n        </div>\n        <div class=\"contents-bar row\">\n            <div class=\"primary-type column small-6 medium-6 large-6 text-left\">\n                <div class=\"additional-info-line\"><i class=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "primaryTypeMeta")),"icon"), env.opts.autoescape);
output += "\"></i>&thinsp;&nbsp;";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "primaryTypeMeta")),"verboseName"), env.opts.autoescape);
if(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"length")) {
output += " (";
output += runtime.suppressValue(env.getFilter("numberWithCommas").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"length")), env.opts.autoescape);
output += " words)";
;
}
output += "</div>\n            </div>\n            <div class=\"related-types column small-6 medium-6 large-6 text-right\"><div class=\"additional-info-line\">";
if(env.getFilter("length").call(context, runtime.contextOrFrameLookup(context, frame, "additionalItemTypes")) > 0) {
output += "Includes ";
frame = frame.push();
var t_11 = runtime.contextOrFrameLookup(context, frame, "additionalItemTypes");
if(t_11) {var t_10 = t_11.length;
for(var t_9=0; t_9 < t_11.length; t_9++) {
var t_12 = t_11[t_9];
frame.set("type", t_12);
frame.set("loop.index", t_9 + 1);
frame.set("loop.index0", t_9);
frame.set("loop.revindex", t_10 - t_9);
frame.set("loop.revindex0", t_10 - t_9 - 1);
frame.set("loop.first", t_9 === 0);
frame.set("loop.last", t_9 === t_10 - 1);
frame.set("loop.length", t_10);
output += "<i class=\"";
output += runtime.suppressValue(runtime.memberLookup((t_12),"icon"), env.opts.autoescape);
output += "\"></i>";
;
}
}
frame = frame.pop();
;
}
output += "</div>\n            </div>\n        </div>\n\n        <div class=\"primary-description row";
if(runtime.contextOrFrameLookup(context, frame, "primaryIsExpanded")) {
output += " overflow-visible";
;
}
output += "\">\n            <div class=\"budget-line collapsed column small-12 medium-12 large-12\">\n                <div class=\"item-options\">\n                    <div class=\"option-list\">\n                        <div class=\"web-info option\">\n                            <i class=\"fa fa-fw fa-desktop\"></i>\n                            <span class=\"hover-info\">Web publishing</span>\n                        </div>\n                        <div class=\"print-info option\">\n                            <i class=\"fa fa-fw fa-newspaper-o\"></i>\n                            <span class=\"hover-info\">Print publishing</span>\n                        </div>\n                    </div>\n                </div>\n\n                <div class=\"mobile-author-info\">\n                    <p>";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors")) > 0) {
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors")) == 1) {
output += "Author";
;
}
else {
output += "Authors";
;
}
output += ": ";
frame = frame.push();
var t_15 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"authors");
if(t_15) {var t_14 = t_15.length;
for(var t_13=0; t_13 < t_15.length; t_13++) {
var t_16 = t_15[t_13];
frame.set("author", t_16);
frame.set("loop.index", t_13 + 1);
frame.set("loop.index0", t_13);
frame.set("loop.revindex", t_14 - t_13);
frame.set("loop.revindex0", t_14 - t_13 - 1);
frame.set("loop.first", t_13 === 0);
frame.set("loop.last", t_13 === t_14 - 1);
frame.set("loop.length", t_14);
output += runtime.suppressValue(runtime.memberLookup((t_16),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors")) > 0) {
output += "&nbsp;/&nbsp;";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors")) == 1) {
output += "Editor";
;
}
else {
output += "Editors";
;
}
output += ": ";
frame = frame.push();
var t_19 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"editors");
if(t_19) {var t_18 = t_19.length;
for(var t_17=0; t_17 < t_19.length; t_17++) {
var t_20 = t_19[t_17];
frame.set("editor", t_20);
frame.set("loop.index", t_17 + 1);
frame.set("loop.index0", t_17);
frame.set("loop.revindex", t_18 - t_17);
frame.set("loop.revindex0", t_18 - t_17 - 1);
frame.set("loop.first", t_17 === 0);
frame.set("loop.last", t_17 === t_18 - 1);
frame.set("loop.length", t_18);
output += runtime.suppressValue(runtime.memberLookup((t_20),"formattedName"), env.opts.autoescape);
if(!runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last")) {
output += ", ";
;
}
;
}
}
frame = frame.pop();
;
}
output += "</p>\n                </div>\n\n                <p>";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"primaryContent")),"budgetLine"), env.opts.autoescape);
output += "</p>\n\n                <div class=\"mobile-action-buttons\">\n                    <div class=\"action-button material-button edit-package\">\n                        <a href=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "homeViewLink"), env.opts.autoescape);
output += "edit/";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"id"), env.opts.autoescape);
output += "/\">\n                            <div class=\"button-contents\">\n                                <div class=\"button-innermost\">\n                                    <i class=\"fa fa-fw fa-pencil-square-o\"></i>\n                                    <div class=\"action-text\">Edit</div>\n                                    <div class=\"clearer\"></div>\n                                </div>\n                            </div>\n                        </a>\n                    </div>\n                    <div class=\"action-button material-button view-notes\">\n                        <div class=\"button-contents\">\n                            <div class=\"button-innermost\">\n                                <i class=\"fa fa-fw fa-paragraph\"></i>\n                                <div class=\"action-text\">Notes</div>\n                                <div class=\"clearer\"></div>\n                            </div>\n                        </div>\n                    </div>\n                    <div class=\"action-button material-button subscribe\">\n                        <div class=\"button-contents\">\n                            <div class=\"button-innermost\">\n                                <i class=\"fa fa-fw fa-slack\"></i>\n                                <div class=\"action-text\">Subscribe</div>\n                                <div class=\"clearer\"></div>\n                            </div>\n                        </div>\n                    </div>\n                    <div class=\"clearer\"></div>\n                </div>\n\n                <div class=\"clearer\"></div>\n            </div>\n        </div>\n    </div>\n    <div class=\"action-buttons column small-1 medium-1 large-1 text-center\">\n        <div class=\"edit-package action-button\">\n            <a href=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "homeViewLink"), env.opts.autoescape);
output += "edit/";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"id"), env.opts.autoescape);
output += "/\">\n                <i class=\"fa fa-pencil-square-o\"></i>\n                <span class=\"hover-info\">Edit</span>\n            </a>\n        </div>\n        <div class=\"view-notes action-button\">\n            <i class=\"fa fa-paragraph\"></i>\n            <span class=\"hover-info\">Notes</span>\n        </div>\n        <div class=\"subscribe action-button\">\n            <i class=\"fa fa-slack\"></i>\n            <span class=\"hover-info\">Subscribe</span>\n        </div>\n        <div class=\"expand-package action-button\">\n            <i class=\"fa fa-plus\"></i>\n            <i class=\"fa fa-minus\"></i>\n            <span class=\"hover-info\">More info</span>\n        </div>\n    </div>\n    <div class=\"clearer\"></div>\n</div>\n";
if(env.getFilter("length").call(context, runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "packageObj")),"additionalContent")) > 0) {
output += "\n<div class=\"extra-sheet\">\n    <ul class=\"related-content\">\n        ";
frame = frame.push();
var t_23 = runtime.contextOrFrameLookup(context, frame, "additionalWithTypeMetas");
if(t_23) {var t_22 = t_23.length;
for(var t_21=0; t_21 < t_23.length; t_21++) {
var t_24 = t_23[t_21];
frame.set("item", t_24);
frame.set("loop.index", t_21 + 1);
frame.set("loop.index0", t_21);
frame.set("loop.revindex", t_22 - t_21);
frame.set("loop.revindex0", t_22 - t_21 - 1);
frame.set("loop.first", t_21 === 0);
frame.set("loop.last", t_21 === t_22 - 1);
frame.set("loop.length", t_22);
output += "\n            ";
env.getTemplate("budget/package-item-web-additionalcontent", false, "budget/package-item-web", null, function(t_27,t_25) {
if(t_27) { cb(t_27); return; }
t_25.render(context.getVariables(), frame, function(t_28,t_26) {
if(t_28) { cb(t_28); return; }
output += t_26
output += "\n        ";
})});
}
}
frame = frame.pop();
output += "\n    </ul>\n</div>\n";
;
}
output += "\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/package-search-list-print"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div id=\"filter-holder\" class=\"center-content row\"></div>\n\n<div id=\"faceted-packages\" class=\"center-content\"></div>\n\n<div id=\"package-list\" class=\"center-content\">\n      <div class=\"packages\"></div>\n</div>\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/package-search-list-web"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div id=\"filter-holder\" class=\"center-content row\"></div>\n\n<div id=\"package-list\" class=\"center-content\">\n      <div class=\"packages\"></div>\n</div>";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/packages-edit"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div class=\"center-content\">\n    <div class=\"edit-bar\">\n        <div id=\"presence-indicator\">\n            <div class=\"presence-notice-holder\">\n                <div class=\"presence-heading\">\n                    <div class=\"fa fa-exclamation-triangle neon\"></div>\n                    <h2>Caution</h2>\n                </div>\n                <div class=\"other-active-users\"></div>\n            </div>\n        </div>\n        <div class=\"button-holder\">\n            <div class=\"delete-trigger material-button flat-button\"><span>Delete</span></div>\n            <div class=\"primary-action save-trigger material-button flat-button\"><span>Save</span></div>\n            <div class=\"save-and-continue-editing-trigger material-button flat-button show-for-medium\"><span>Save &amp; continue editing</span></div>\n            <div class=\"clearer\"></div>\n        </div>\n    </div>\n    <div class=\"single-page\">\n        <div class=\"package-header\">\n            <div class=\"color-dot\"></div>\n            <h1>Add content</h1>\n        </div>\n        <form id=\"package-form\">\n            <div class=\"error-message\"></div>\n\n            <div class=\"row\">\n                <div class=\"medium-6 columns form-group\">\n                    <input id=\"hub\" name=\"hub\" class=\"to-selectize\" type=\"text\" placeholder=\"Choose an option\" autocomplete=\"off\" autocorrect=\"off\" data-form=\"package\" required=\"\" isRequired=\"true\" value=\"\" />\n                    <label for=\"hub\" class=\"control-label\">Hub<span class=\"required-marker\">*</span></label>\n                    <i class=\"bar\"></i>\n                    <div class=\"form-help\"></div>\n                </div>\n                <div class=\"medium-3 columns form-group\">\n                    <input id=\"type\" name=\"type\" class=\"to-selectize\" type=\"text\" placeholder=\"Choose an option\" autocomplete=\"off\" autocorrect=\"off\" data-form=\"primary\" value=\"\" required=\"\" isRequired=\"true\" />\n                    <label for=\"type\" class=\"control-label\">Type<span class=\"required-marker\">*</span></label>\n                    <i class=\"bar\"></i>\n                    <div class=\"form-help\"></div>\n                </div>\n                <div class=\"medium-3 columns form-group variable-attribute-group\">\n                    <div class=\"length-group variable-attribute\">\n                        <input id=\"length\" name=\"length\" data-form=\"primary\" class=\"form-select-word-count\" type=\"number\" autocomplete=\"off\" autocorrect=\"off\" value=\"\" required=\"\" />\n                        <label for=\"length\" class=\"control-label\">Word count</label>\n                        <i class=\"bar\"></i>\n                    </div>\n\n                    ";
if(runtime.contextOrFrameLookup(context, frame, "visualsRequestURL")) {
output += "\n                    <div class=\"request-link-group variable-attribute\">\n                        <div class=\"request-button-holder\">\n                            <div class=\"request-link material-button flat-button\"><a href=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "visualsRequestURL"), env.opts.autoescape);
output += "\" target=\"_blank\"><span>Request visuals</span></a></div>\n                        </div>\n                    </div>\n                    ";
;
}
output += "\n                </div>\n            </div>\n\n            <div class=\"row\">\n                <div class=\"medium-3 columns form-group\">\n                    <input id=\"pub_date_resolution\" name=\"pub_date_resolution\" class=\"to-selectize\" type=\"text\" placeholder=\"Choose an option\" autocomplete=\"off\" autocorrect=\"off\" data-form=\"package\" required=\"\" isRequired=\"true\" />\n                    <label for=\"pub_date_resolution\" class=\"control-label\">Time format<span class=\"required-marker\">*</span></label>\n                    <i class=\"bar\"></i>\n                    <div class=\"form-help\"></div>\n                </div>\n                <div class=\"medium-5 columns form-group pub-date-group\">\n                    <input id=\"pub_date\" name=\"pub_date\" data-form=\"package\" type=\"text\" autocomplete=\"off\" autocorrect=\"off\" required=\"\" isRequired=\"true\" value=\"\" />\n                    <label for=\"pub_date\" class=\"control-label\">Published date<span class=\"required-marker\">*</span></label>\n                    <span class=\"datepicker-trigger rich-widget-trigger\" tabindex=\"0\"><i class=\"material-icons md-24\">today</i></span>\n                    <i class=\"bar\"></i>\n                    <div class=\"form-help\"></div>\n                </div>\n                <div class=\"medium-4 columns form-group pub-time-group\">\n                    <input id=\"pub_time\" name=\"pub_time\" data-form=\"package\" type=\"text\" autocomplete=\"off\" autocorrect=\"off\" value=\"\" />\n                    <label for=\"pub_time\" class=\"control-label\">Published time&thinsp;*</label>\n                    <span class=\"timepicker-trigger rich-widget-trigger\" tabindex=\"0\"><i class=\"material-icons md-24\">access_time</i></span>\n                    <i class=\"bar\"></i>\n                </div>\n            </div>\n\n            <div class=\"row\">\n                <div class=\"medium-12 columns form-group\">\n                    <div class=\"slug-group-holder\">\n                        <div class=\"hub-slug-value\">hub.</div>\n                        <div class=\"keyword-group\">\n                            <div class=\"keyword-value\">keyword</div>\n                            <input id=\"slug_key\" name=\"slug_key\" data-form=\"primary\" type=\"text\" placeholder=\"keyword\" autocomplete=\"off\" value=\"\" required=\"\" isRequired=\"true\" maxlength=\"20\" />\n                        </div>\n                        <div class=\"formatted-date-value\">.date</div>\n                        <div class=\"clearer\"></div>\n                    </div>\n                    <label for=\"slug_key\" class=\"control-label\">Slug<span class=\"required-marker\">*</span></label>\n                    <i class=\"bar\"></i>\n                    <div class=\"form-help\"></div>\n                </div>\n                <div class=\"medium-6 columns\"></div>\n            </div>\n\n            <div class=\"row\">\n                <!--  -->\n                <div class=\"medium-12 columns form-group\">\n                    <div id=\"budget_line_holder\" class=\"expanding-holder\">\n                        <textarea id=\"budget_line\" name=\"budget_line\" data-form=\"primary\" rows=\"1\" required=\"\" isRequired=\"true\" ></textarea>\n                        <pre class=\"budget-spacer\"><span></span><br></pre>\n                    </div>\n                    <label for=\"budget_line\" class=\"control-label\">Budget line<span class=\"required-marker\">*</span></label>\n                    <i class=\"bar\"></i>\n                    <div class=\"form-help\"></div>\n                </div>\n            </div>\n\n            <div class=\"row\">\n                <div class=\"medium-6 columns form-group set-authors\">\n                    <input id=\"authors\" name=\"authors\" class=\"to-selectize staff-select reporter\" data-form=\"primary\" type=\"text\" isRequired=\"true\" value=\"\" />\n                    <label for=\"authors\" class=\"control-label\">Author(s)<span class=\"required-marker\">*</span></label>\n                    <i class=\"bar\"></i>\n                    <div class=\"form-help\"></div>\n                </div>\n                <div class=\"medium-6 columns form-group set-editors\">\n                    <input id=\"editors\" name=\"editors\" class=\"to-selectize staff-select editor\" data-form=\"primary\" type=\"text\" value=\"\" />\n                    <label for=\"editors\" class=\"control-label\">Editor(s)</label>\n                    <i class=\"bar\"></i>\n                </div>\n            </div>\n\n            ";
if(runtime.contextOrFrameLookup(context, frame, "showHeadlines")) {
output += "\n            <div class=\"row collapsible-row-header\" data-expand-target=\"headlines\">\n                <h4>Headlines</h4>\n            </div>\n            ";
;
}
output += "\n\n            <div class=\"row can-collapse\" data-expand-receiver=\"headlines\">\n                <div id=\"headline-fields\" class=\"collapsable-inner\">\n                    <div class=\"extra-spacing\"></div>\n\n                    <div class=\"hl-variable-group\" data-mode=\"other\">\n                        <div class=\"medium-6 columns form-group\">\n                            <input id=\"headline1\" name=\"headline1\" data-form=\"package\" type=\"text\" value=\"\" required=\"\" />\n                            <label for=\"headline1\" class=\"control-label\">Headline #1</label>\n                            <i class=\"bar\"></i>\n                        </div>\n\n                        <div class=\"medium-6 columns form-group\">\n                            <input id=\"headline2\" name=\"headline2\" data-form=\"package\" type=\"text\" value=\"\" required=\"\">\n                            <label for=\"headline2\" class=\"control-label\">Headline #2</label>\n                            <i class=\"bar\"></i>\n                        </div>\n\n                        <div class=\"medium-6 columns form-group\">\n                            <input id=\"headline3\" name=\"headline3\" data-form=\"package\" type=\"text\" value=\"\" required=\"\" />\n                            <label for=\"headline3\" class=\"control-label\">Headline #3</label>\n                            <i class=\"bar\"></i>\n                        </div>\n\n                        <div class=\"medium-6 columns form-group\">\n                            <input id=\"headline4\" name=\"headline4\" data-form=\"package\" type=\"text\" value=\"\" required=\"\" />\n                            <label for=\"headline4\" class=\"control-label\">Headline #4</label>\n                            <i class=\"bar\"></i>\n                        </div>\n\n                        <div class=\"clearer\"></div>\n                    </div>\n\n                    <div class=\"hl-variable-group medium-12 columns form-radio\" data-mode=\"voting\">\n                        <div class=\"radio\">\n                            <label>\n                                <input id=\"headlineRadio1\" name=\"headlineChoices\" data-form=\"package\" type=\"radio\" value=\"\" /><i class=\"helper\"></i><span class=\"radio-label\"> <span class=\"vote-count\">(<span class=\"vote-total\">0</span><span class=\"percent-sign\">%</span>)</span></span>\n                            </label>\n                        </div>\n\n                        <div class=\"radio\">\n                            <label>\n                                <input id=\"headlineRadio2\" name=\"headlineChoices\" data-form=\"package\" type=\"radio\" value=\"\" /><i class=\"helper\"></i><span class=\"radio-label\"> <span class=\"vote-count\">(<span class=\"vote-total\">0</span><span class=\"percent-sign\">%</span>)</span>\n                            </label>\n                        </div>\n\n                        <div class=\"radio\">\n                            <label>\n                                <input id=\"headlineRadio3\" name=\"headlineChoices\" data-form=\"package\" type=\"radio\" value=\"\" /><i class=\"helper\"></i><span class=\"radio-label\"> <span class=\"vote-count\">(<span class=\"vote-total\">0</span><span class=\"percent-sign\">%</span>)</span>\n                            </label>\n                        </div>\n\n                        <div class=\"radio\">\n                            <label>\n                                <input id=\"headlineRadio4\" name=\"headlineChoices\" data-form=\"package\" type=\"radio\" value=\"\" /><i class=\"helper\"></i><span class=\"radio-label\"> <span class=\"vote-count\">(<span class=\"vote-total\">0</span><span class=\"percent-sign\">%</span>)</span>\n                            </label>\n                        </div>\n\n                        <div class=\"clearer\"></div>\n                    </div>\n\n                    <div id=\"vote-submission-toggle\" class=\"medium-12 columns checkbox\">\n                        <label>\n                            <input id=\"headlinesReady\" name=\"headlinesReady\" data-form=\"package\" type=\"checkbox\" value=\"ready\" /><i class=\"helper\"></i>Submit headlines to a vote\n                            <!-- <input type=\"checkbox\" checked=\"\" /><i class=\"helper\"></i>Submit headlines to a vote -->\n                        </label>\n                    </div>\n\n                    <div class=\"clearer\"></div>\n                </div>\n            </div>\n\n            <div class=\"clearer\"></div>\n\n            <div class=\"row collapsible-row-header\" data-expand-target=\"production-notes\">\n                <h4>Production notes</h4>\n            </div>\n\n            <div class=\"row can-collapse\" data-expand-receiver=\"production-notes\">\n                <div class=\"collapsable-inner\">\n                    <div class=\"medium-12 columns notes-reveal form-group\">\n                        <div id=\"notes-quill\" class=\"quill-holder\">\n                        </div>\n                    </div>\n                    <div class=\"clearer\"></div>\n                </div>\n            </div>\n\n            <div class=\"clearer\"></div>\n\n            <div class=\"row collapsible-row-header\" data-expand-target=\"publishing-details\">\n                <h4>Publishing details</h4>\n            </div>\n\n            <div class=\"row can-collapse\" data-expand-receiver=\"publishing-details\">\n                <div id=\"publishing-fields\" class=\"collapsable-inner\">\n                    <div class=\"extra-spacing\"></div>\n\n                    <div class=\"medium-12 columns form-group\">\n                        <input id=\"url\" name=\"url\" data-form=\"package\" type=\"text\" value=\"\" />\n                        <label for=\"url\" class=\"control-label\">URL</label>\n                        <i class=\"bar\"></i>\n                    </div>\n\n                    <div class=\"clearer\"></div>\n                </div>\n            </div>\n\n            <div class=\"clearer\"></div>\n        </form>\n    </div>\n\n    <div class=\"single-page\">\n        <div id=\"additional-forms\">\n            <div class=\"section-header\">\n                <h4 class=\"final-header\">Additional content <span class=\"add-additional-content-trigger material-button\"><i class=\"fa fa-plus\"></i><span>&thinsp;Add<span class=\"show-for-medium\">&nbsp;content</span></span></span></h4>\n            </div>\n        </div>\n\n        <div id=\"additional-content-children\" class=\"additional-content\">\n        </div>\n\n        <div class=\"bottom-button-holder\">\n            <div class=\"add-additional-content-trigger material-button\"><i class=\"fa fa-plus\"></i><span>&thinsp;Add content</span></div>\n        </div>\n    </div>\n\n    <div id=\"content-placements-table\" class=\"single-page table-card\">\n        <div class=\"list-header\">\n            <h4>Print placements <span class=\"hint\">(Click to edit)</span></h4>\n            <div class=\"create-placement material-button flat-button\"><span>Create new</span></div>\n        </div>\n        <div id=\"content-placements-loading\">\n            <div class=\"spinner\"></div>\n            <div class=\"loading-text\">Loading...</div>\n        </div>\n        <div class=\"table-holder\">\n            <table class=\"full-results\">\n                <thead>\n                    <tr>\n                        <th class=\"destination\">Destination</th>\n                        <th class=\"run-date\">Run date(s)</th>\n                        <th class=\"external-slug\">Slug</th>\n                        <th class=\"placement-types\">Type(s)</th>\n                        <th class=\"page-and-details\">Page / Details</th>\n                        <th class=\"delete-action-holder\">Delete</th>\n                    </tr>\n                </thead>\n                <tbody>\n                </tbody>\n            </table>\n\n            <div class=\"table-pagination\">\n                <div class=\"current-range\">\n                    <span class=\"this-page-range\"><span class=\"range-start\">0</span>&thinsp;&mdash;&thinsp;<span class=\"range-end\">0</span></span> of <span class=\"total-records\">0</span></div>\n                    <a class=\"btn disabled btn-default btn-primary-flat prev-trigger\" href=\"#\" type=\"link\">\n                        <i class=\"material-icons md-24\">keyboard_arrow_left</i>\n                    </a>\n                    <a class=\"btn disabled btn-default btn-primary-flat next-trigger\" href=\"#\" type=\"link\">\n                        <i class=\"material-icons md-24\">keyboard_arrow_right</i>\n                    </a>\n            </div>\n        </div>\n    </div>\n</div>\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/packages-list-datefilter"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div class=\"icon-holder column small-1 medium-1 large-1\">\n    <i class=\"fa fa-calendar\"></i>\n</div>\n<div class=\"date-chooser-holder column small-5 medium-5 large-5\">\n    <div class=\"\"></div>\n    <div id=\"date-chooser\">\n        <div id=\"ugly-date-picker\" data-uglydate-large-screen-width=\"585\">\n            <div id=\"search-dates-start-holder\">\n                <input type=\"date\" name=\"start-date\" placeholder=\"Select A Date\" />\n            </div>\n\n            <div id=\"search-dates-end-holder\">\n                <input type=\"date\" name=\"end-date\" placeholder=\"Select A Date\" />\n            </div>\n        </div>\n\n        <input id=\"budget-dates-start\" placeholder=\"Start date\" size=\"20\" value=\"\">\n        <span class=\"start-date-holder\"></span>\n        <span class=\"to-label\"> to </span>\n        <input id=\"budget-dates-end\" placeholder=\"End date\" size=\"20\" value=\"\">\n        <span class=\"end-date-holder\"></span>\n        <div class=\"clearer\"></div>\n    </div>\n    <div class=\"\"></div>\n</div>\n<div class=\"spacer-column column small-3 medium-3 large-3\">&nbsp;</div>\n<div class=\"create-button column small-3 medium-3 large-3\">\n    <div class=\"material-button\"><a href=\"";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "homeViewLink"), env.opts.autoescape);
output += "edit/\" tabindex=\"-1\"><span>Create new</span></a></div>\n</div>\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/packages-list-searchbox"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div class=\"icon-holder column small-1 medium-1 large-1\">\n    <i class=\"fa fa-search\"></i>\n</div>\n<div class=\"search-box-holder column small-11 medium-11 large-11\">\n    <div class=\"\">\n        <input id=\"package-search-box\" name=\"package-search-box\" type=\"text\" placeholder=\"Search people, hubs, verticals and story descriptions...\" />\n    </div>\n</div>";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/placement-type-faceted-packages-list"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div>\n  <h4 class=\"facet-label\">";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "placementType")),"name"), env.opts.autoescape);
output += "</h4>\n  <div class=\"packages ";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "placementType")),"slug"), env.opts.autoescape);
output += "\"></div>\n</div>\n";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/root-view"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div id=\"navigation\" class=\"top-bar sans\"></div>\n<div id=\"main-content\"></div>\n<div id=\"modal-holder\"></div>\n<div id=\"snackbar-holder\"></div>";
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

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["budget/snackbar-base"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<div class=\"contents\">";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "text"), env.opts.autoescape);
if(runtime.contextOrFrameLookup(context, frame, "action")) {
if(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "action")),"promptText")) {
output += "<div class=\"action-trigger\">";
output += runtime.suppressValue(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "action")),"promptText"), env.opts.autoescape);
output += "</div>";
;
}
;
}
output += "</div>";
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
