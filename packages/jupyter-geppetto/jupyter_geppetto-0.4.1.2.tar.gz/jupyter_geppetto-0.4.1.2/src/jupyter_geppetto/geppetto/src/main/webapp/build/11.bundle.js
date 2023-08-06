webpackJsonp([11],{

/***/ 2209:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {
    var React = __webpack_require__(1),
        GEPPETTO = __webpack_require__(71);

    __webpack_require__(3822);

    var Share = React.createClass({
        displayName: 'Share',


        visible: false,
        /**
         * Shares Geppetto on Facebook
         *
         * @param {URL} linkURL - URL to share
         * @param {String} title - Title of sharing post
         * @param {String} text - Test of sharing post
         */
        facebook: function facebook() {
            var url = 'http://www.facebook.com/sharer.php?';
            url += '&u=' + encodeURIComponent('http://geppetto.org');
            this.popup(url);
            return GEPPETTO.Resources.SHARE_ON_FACEBOOK;
        },
        /**
         * Shares Geppetto on Twitter
         *
         * @param {URL} linkURL - URL to share
         * @param {String} title - Title of sharing post
         */
        twitter: function twitter() {
            var url = 'http://twitter.com/share?';
            url += 'text=' + encodeURIComponent('Check out Geppetto, an opensource platform to explore and simulate digital biology!');
            url += '&url=' + encodeURIComponent('http://geppetto.org');
            url += '&counturl=' + encodeURIComponent('http://geppetto.org');
            this.popup(url);
            return GEPPETTO.Resources.SHARE_ON_TWITTER;
        },

        /**
         * General method to display popup window with either facebook or twitter share
         *
         * @param {URL} url - URL to share
         */
        popup: function popup(url) {
            window.open(url, '', 'toolbar=0,status=0,width=626, height=436');
        },

        setVisible: function setVisible(mode) {
            this.visible = mode;
        },

        isVisible: function isVisible() {
            return this.visible;
        },

        show: function show(mode) {
            var returnMessage;

            if (mode) {
                returnMessage = GEPPETTO.Resources.SHOW_SHAREBAR;

                //show share bar
                if (!this.isVisible()) {
                    $("#geppetto-share").toggleClass("clicked");
                    $("#geppetto-share").slideToggle();
                    this.setVisible(mode);
                }
                //share bar is already visible, nothing to see here
                else {
                        returnMessage = GEPPETTO.Resources.SHAREBAR_ALREADY_VISIBLE;
                    }
            } else {
                returnMessage = GEPPETTO.Resources.SHOW_SHAREBAR;
                //hide share bar
                if (this.isVisible()) {
                    $("#geppetto-share").toggleClass("clicked");
                    $("#geppetto-share").slideToggle();
                    this.setVisible(mode);
                }
                //share bar already hidden
                else {
                        returnMessage = GEPPETTO.Resources.SHAREBAR_ALREADY_HIDDEN;
                    }
            }

            return returnMessage;
        },

        componentDidMount: function componentDidMount() {
            GEPPETTO.Share = this;

            var share = $("#share");

            share.click(function () {

                //toggle button class
                share.toggleClass('clicked');

                //user has clicked the console button
                GEPPETTO.Share.show(share.hasClass('clicked'));
                return false;
            }.bind(this));
        },

        render: function render() {
            var that = this;
            return React.createElement(
                'div',
                null,
                React.createElement(
                    'div',
                    { id: 'shareTab' },
                    React.createElement(
                        'button',
                        { className: 'btn', id: 'share' },
                        React.createElement('i', { className: 'fa fa-share icon-xlarge' })
                    )
                ),
                React.createElement(
                    'div',
                    { id: 'geppetto-share', className: 'col-md-1 share-panel' },
                    React.createElement(
                        'p',
                        null,
                        React.createElement(
                            'a',
                            { className: 'btn', onClick: that.facebook },
                            React.createElement('i', { className: 'icon-xlarge fa fa-facebook' })
                        )
                    ),
                    React.createElement(
                        'p',
                        null,
                        React.createElement(
                            'a',
                            { className: 'btn', onClick: that.twitter },
                            React.createElement('i', { className: 'icon-xlarge fa fa-twitter' })
                        )
                    )
                )
            );
        }
    });

    return Share;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3822:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(3823);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./Share.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./Share.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 3823:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\n#geppetto-share {\n  background-color: rgba(255, 255, 255, 0.5);\n  position: absolute;\n  bottom: 0px;\n  right: 280px;\n  display: none;\n  border-radius: 0px;\n  height: auto;\n  opacity: .85;\n  padding-bottom: 30px;\n  width: 65px;\n  z-index: 10001;\n  text-align: center;\n}\n#geppetto-share p {\n  margin: 1em 0em;\n}\n#geppetto-share a {\n  width: 35px;\n}\n#shareTab {\n  bottom: 0px;\n  right: 280px;\n  position: fixed;\n  z-index: 10002;\n}\n#share-button {\n  z-index: 10001;\n}\n#share {\n  box-shadow: none;\n  text-shadow: none;\n  background-color: rgba(255, 255, 255, 0.8);\n  border-radius: 0px;\n  color: #f23d7a;\n  width: 65px;\n  height: 32px;\n  border: 0px;\n}\n", ""]);

// exports


/***/ })

});
//# sourceMappingURL=11.bundle.js.map