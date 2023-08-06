webpackJsonp([37],{

/***/ 1416:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(1417);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./CameraControls.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./CameraControls.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 1417:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, "#mainContainer .position-toolbar {\n  top: 50px;\n}\n.position-toolbar {\n  position: relative;\n}\n.position-toolbar .rotate90 {\n  -webkit-transform: rotate(90deg);\n  -moz-transform: rotate(90deg);\n  -ms-transform: rotate(90deg);\n  -o-transform: rotate(90deg);\n}\n.position-toolbar .rotate180 {\n  -webkit-transform: rotate(180deg);\n  -moz-transform: rotate(180deg);\n  -ms-transform: rotate(180deg);\n  -o-transform: rotate(180deg);\n}\n.position-toolbar .dg {\n  font-family: \"Helvetica Neue\", Helvetica, Arial, sans-serif;\n  font-weight: 200;\n}\n.position-toolbar .squareB {\n  width: 24px;\n  height: 24px;\n  position: absolute;\n  padding: 1px;\n}\n.position-toolbar .pan-left {\n  left: 10px;\n  top: 37px;\n}\n.position-toolbar .pan-top {\n  left: 37px;\n  top: 10px;\n}\n.position-toolbar .pan-home {\n  left: 37px;\n  top: 37px;\n}\n.position-toolbar .pan-right {\n  left: 64px;\n  top: 37px;\n}\n.position-toolbar .pan-bottom {\n  left: 37px;\n  top: 64px;\n}\n.position-toolbar .rotate-left {\n  left: 10px;\n  top: 132px;\n}\n.position-toolbar .rotate-top {\n  left: 37px;\n  top: 105px;\n}\n.position-toolbar .rotate-home {\n  left: 37px;\n  top: 132px;\n}\n.position-toolbar .rotate-right {\n  left: 64px;\n  top: 132px;\n}\n.position-toolbar .rotate-bottom {\n  left: 37px;\n  top: 159px;\n}\n.position-toolbar .rotate-z {\n  left: 10px;\n  top: 159px;\n}\n.position-toolbar .rotate-mz {\n  left: 64px;\n  top: 159px;\n}\n.position-toolbar .zoom-out {\n  left: 37px;\n  top: 228px;\n}\n.position-toolbar .zoom-in {\n  left: 37px;\n  top: 200px;\n}\n", ""]);

// exports


/***/ }),

/***/ 656:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1);
    var GEPPETTO = __webpack_require__(71);

    __webpack_require__(1416);

    var CameraControls = React.createClass({
        displayName: 'CameraControls',


        panLeft: function panLeft() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraPan(-0.01, 0)', true);
        },

        panRight: function panRight() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraPan(0.01, 0)', true);
        },

        panUp: function panUp() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraPan(0, -0.01)', true);
        },

        panDown: function panDown() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraPan(0, 0.01)', true);
        },

        rotateUp: function rotateUp() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraRotate(0, 0.01)', true);
        },

        rotateDown: function rotateDown() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraRotate(0, -0.01)', true);
        },

        rotateLeft: function rotateLeft() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraRotate(-0.01, 0)', true);
        },

        rotateRight: function rotateRight() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraRotate(0.01, 0)', true);
        },

        rotateZ: function rotateZ() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraRotate(0, 0, 0.01)', true);
        },

        rotateMZ: function rotateMZ(increment) {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraRotate(0, 0, -0.01)', true);
        },

        rotate: function rotate() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.autoRotate()', true);
        },

        cameraHome: function cameraHome() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.resetCamera()', true);
        },

        zoomIn: function zoomIn() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraZoom(-0.1)', true);
        },

        zoomOut: function zoomOut() {
            GEPPETTO.CommandController.execute(this.props.viewer + '.incrementCameraZoom(+0.1)', true);
        },

        componentDidMount: function componentDidMount() {},

        render: function render() {
            return React.createElement(
                'div',
                { className: 'position-toolbar' },
                React.createElement('button', { id: 'panLeftBtn', className: 'btn squareB fa fa-chevron-left pan-left', onClick: this.panLeft }),
                React.createElement('button', { id: 'panUpBtn', className: 'btn squareB fa fa-chevron-up pan-top', onClick: this.panUp }),
                React.createElement('button', { id: 'panRightBtn', className: 'btn squareB fa fa-chevron-right pan-right', onClick: this.panRight }),
                React.createElement('button', { id: 'panDownBtn', className: 'btn squareB fa fa-chevron-down pan-bottom', onClick: this.panDown }),
                React.createElement('button', { id: 'panHomeBtn', className: 'btn squareB fa fa-home pan-home', onClick: this.cameraHome }),
                React.createElement('button', { id: 'rotateLeftBtn', className: 'btn squareB fa fa-undo rotate-left', onClick: this.rotateLeft }),
                React.createElement('button', { id: 'rotateUpBtn', className: 'btn squareB fa fa-repeat rotate90 rotate-top', onClick: this.rotateUp }),
                React.createElement('button', { id: 'rotateRightBtn', className: 'btn squareB fa fa-repeat rotate-right', onClick: this.rotateRight }),
                React.createElement('button', { id: 'rotateDownBtn', className: 'btn squareB fa fa-undo rotate90 rotate-bottom', onClick: this.rotateDown }),
                React.createElement('button', { id: 'rotateZBtn', className: 'btn squareB fa fa-undo rotate-z', onClick: this.rotateZ }),
                React.createElement('button', { id: 'rotateMZBtn', className: 'btn squareB fa fa-repeat rotate-mz', onClick: this.rotateMZ }),
                React.createElement('button', { id: 'rotateBtn', className: 'btn squareB fa fa-video-camera rotate-home', onClick: this.rotate }),
                React.createElement('button', { id: 'zoomInBtn', className: 'btn squareB fa fa-search-plus zoom-in', onClick: this.zoomIn }),
                React.createElement('button', { id: 'zoomOutBtn', className: 'btn squareB fa fa-search-minus zoom-out', onClick: this.zoomOut })
            );
        }

    });

    return CameraControls;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ })

});
//# sourceMappingURL=37.bundle.js.map