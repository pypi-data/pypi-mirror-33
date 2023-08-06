webpackJsonp([24],{

/***/ 2272:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

/**
 *
 * Base Widget Class, all widgets extend this class.
 * @module Widgets/Widget
 * @author  Jesus R. Martinez (jesus@metacell.us)
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {
    var _Backbone$View$extend;

    var Backbone = __webpack_require__(94);
    var $ = __webpack_require__(16);
    __webpack_require__(803);

    var zIndex = {
        min: 1,
        max: 9999,
        restore: 10
    };

    return {

        /**
         * Not yet implemented, used for local storage and history.
         */
        Model: Backbone.Model.extend({}),

        /**
         * Creates base view for widget
         */
        View: Backbone.View.extend((_Backbone$View$extend = {

            id: null,
            dialog: null,
            visible: true,
            destroyed: false,
            size: {},
            position: {},
            registeredEvents: null,
            executedAction: 0,
            lastExecutedAction: 0,
            title: null,
            previousMaxTransparency: false,
            previousMaxSize: {},
            maximize: false,
            collapsed: false,
            widgetType: null,
            stateless: false,
            showTitleBar: true,
            transparentBackground: false,
            dirtyView: false,
            updateHistoryPosition: true,
            helpInfo: '### Inline help not yet available for this widget! \n\n' + 'Try the <a href="http://docs.geppetto.org/en/latest/usingwidgets.html"' + 'target="_blank">online documentation</a> instead.',

            defaultSize: function defaultSize() {
                return { height: 300, width: 350 };
            },
            defaultPosition: function defaultPosition() {
                return { left: "50%", top: "50%" };
            },
            /**
             * Initializes the widget
             *
             * @param {String} id - id of widget
             * @param {String} name - name of widget
             * @param {String} visibility - visibility of widget window
             */
            initialize: function initialize(options) {
                this.id = options.id;
                this.name = options.name;
                this.visible = options.visible;
                this.size = this.defaultSize();
                this.position = this.defaultPosition();
                this.contextMenu = new GEPPETTO.ContextMenuView();
                this.historyMenu = new GEPPETTO.ContextMenuView();
                this.widgetType = options.widgetType;
                this.stateless = options.stateless != undefined ? options.stateless : false;
                this.registeredEvents = [];
                this.dirtyView = false;

                var self = this;
                $(self.historyMenu.el).on('click', function (event) {
                    var itemId = $(event.target).attr('id');
                    var registeredItem = self.historyMenu.getClickedItem(itemId);
                    if (registeredItem != null || registeredItem != undefined) {
                        var label = registeredItem["label"];
                        self.title = label;
                        $("#" + self.id).parent().find(".ui-dialog-title").html(self.title);
                    }
                });
                window.addEventListener('resize', function (event) {
                    if (self.maximize) {
                        self.maximize = false;
                        self.setSize(window.innerHeight, window.innerWidth);
                        self.$el.trigger('resizeEnd', ["maximize"]);
                        self.maximize = true;
                    }
                });

                //this.setSize(this.defaultSize.height, this.defaultSize.width);
            },

            /**
             * Destroy the widget, remove it from DOM
             *
             * @command destroy()
             * @returns {String} - Action Message
             */
            destroy: function destroy() {
                this.$el.remove();
                this.destroyed = true;
                return this.name + " destroyed";
            },

            /**
             * Hides the widget
             *
             * @command hide()
             * @returns {String} - Action Message
             */
            hide: function hide() {
                this.$el.dialog('close').dialogExtend();

                this.visible = false;

                return "Hiding " + this.name + " widget";
            },

            /**
             *  Opens widget dialog
             *
             * @command show()
             * @returns {Object} - Action Message
             */
            show: function show() {
                this.$el.dialog('open').dialogExtend();
                this.visible = true;

                //Unfocused close button
                $(".ui-dialog-titlebar-close").blur();

                return this;
            },

            /**
             * Returns widget type as defined in GEPPETTO.Widgets
             *
             * @returns {int}
             */
            getComponentType: function getComponentType() {
                return this.widgetType;
            },

            /**
             * Gets the name of the widget
             *
             * @command getName()
             * @returns {String} - Name of widget
             */
            getName: function getName() {
                return this.name;
            },

            /**
             * Sets the name of the widget
             * @command setName(name)
             * @param {String} name - Name of widget
             */
            setName: function setName(name) {
                this.name = name;

                // set name to widget window
                this.$el.dialog("option", "title", this.name).dialogExtend();

                // set flag to indicate something changed
                this.dirtyView = true;

                return this;
            },

            /**
             * @command setPosition(left,top)
             * @param {Integer} left -Left position of the widget
             * @param {Integer} top - Top position of the widget
             */
            setPosition: function setPosition(left, top) {
                if (left != null && left != undefined) {
                    this.position.left = left;
                }
                if (top != null && top != undefined) {
                    this.position.top = top;
                }

                this.$el.dialog('option', 'position', {
                    my: "left+" + this.position.left + " top+" + this.position.top,
                    at: "left top",
                    of: $(window)
                }).dialogExtend();

                // set flag to indicate something changed
                this.dirtyView = true;

                return this;
            },

            /**
             * Sets the size of the widget
             * @command setSize(h,w)
             * @param {Integer} h - Height of the widget
             * @param {Integer} w - Width of the widget
             */
            setSize: function setSize(h, w) {
                if (h != null && h != undefined && h != -1) {
                    this.size.height = h;
                }
                if (w != null && w != undefined && w != -1) {
                    this.size.width = w;
                }
                this.$el.dialog({ height: this.size.height, width: this.size.width }).dialogExtend();

                this.$el.trigger('resizeEnd');

                // set flag to indicate something changed
                this.dirtyView = true;

                return this;
            },

            /**
             * @command setMinHeight(h)
             * @param {Integer} h - Minimum Height of the widget
             */
            setMinHeight: function setMinHeight(h) {
                this.$el.dialog('option', 'minHeight', h).dialogExtend();
                return this;
            },

            /**
             * @command setMinWidth(w)
             * @param {Integer} w - Minimum Width of the widget
             */
            setMinWidth: function setMinWidth(w) {
                this.$el.dialog('option', 'minWidth', w).dialogExtend();
                return this;
            },

            /**
             * @command setMinSize(h,w)
             * @param {Integer} h - Minimum Height of the widget
             * @param {Integer} w - Minimum Width of the widget
             */
            setMinSize: function setMinSize(h, w) {
                this.setMinHeight(h);
                this.setMinWidth(w);
                return this;
            },

            /**
             * @command setResizable(true|false)
             * @param {Boolean} true|false - enables / disables resizability
             */
            setResizable: function setResizable(resize) {
                this.$el.dialog('option', 'resizable', resize).dialogExtend();
                return this;
            },

            /**
             * @command setAutoWidth()
             */
            setAutoWidth: function setAutoWidth() {
                this.$el.dialog('option', 'width', 'auto').dialogExtend();
                return this;
            },

            /**
             * @command setAutoHeigth()
             */
            setAutoHeight: function setAutoHeight() {
                this.$el.dialog('option', 'height', 'auto').dialogExtend();
                return this;
            },

            /**
             * Returns the position of the widget
             * @command getPosition()
             * @returns {Object} - Position of the widget
             */
            getPosition: function getPosition() {
                return this.position;
            },

            /**
             * Returns the size of the widget
             * @command getSize()
             * @returns {Object} - Size of the widget
             */
            getSize: function getSize() {
                return this.size;
            },

            /**
             * Gets the ID of the widget
             *
             * @command getId()
             * @returns {String} - ID of widget
             */
            getId: function getId() {
                return this.id;
            },

            /**
             * Did something change in the state of the widget?
             *
             * @command isDirty()
             * @returns {boolean} - ID of widget
             */
            isDirty: function isDirty() {
                return this.dirtyView;
            },

            /**
             * Explicitly sets status of view
             * NOTE: we need to be able to control this from outside the component
             *
             * @command setDirty()
             * @param {boolean} dirty
             */
            setDirty: function setDirty(dirty) {
                this.dirtyView = dirty;
            },

            /**
             * Returns whether widget is visible or not
             *
             * @command isVisible()
             * @returns {Boolean} - Widget visibility state
             */
            isVisible: function isVisible() {
                return this.visible;
            },

            /**
             * Search obj for the value of node within using path.
             * E.g. If obj = {"tree":{"v":1}} and path is "tree.v", it will
             * search within the obj to find the value of "tree.v", returning object
             * containing {value : val, unit : unit, scale : scale}.
             */
            getState: function getState(tree, state) {
                var paths = state.split('.'),
                    current = tree,
                    i;

                for (i = 0; i < paths.length; ++i) {
                    //get index from node if it's array
                    var index = paths[i].match(/[^[\]]+(?=])/g);

                    if (index == null) {
                        if (current[paths[i]] == undefined) {
                            return undefined;
                        } else {
                            current = current[paths[i]];
                        }
                    } else {
                        var iNumber = index[0].replace(/[\[\]']+/g, "");

                        //take index and brackets out of the equation for now
                        var node = paths[i].replace(/ *\[[^]]*\] */g, "");

                        if (current[node][parseInt(iNumber)] == undefined) {
                            return undefined;
                        } else {
                            current = current[node][parseInt(iNumber)];
                        }
                    }
                }
                return current;
            },

            getItems: function getItems(history, name) {
                var data = [];
                for (var i = 0; i < history.length; i++) {
                    var action = this.getId() + "[" + this.getId() + "." + name + "[" + i + "].method].apply(" + this.getId() + ", " + this.getId() + "." + name + "[" + i + "].arguments)";
                    data.push({
                        "label": history[i].label,
                        "action": [action],
                        "icon": null,
                        "position": i
                    });
                }
                return data;
            },

            showHistoryMenu: function showHistoryMenu(event) {
                var that = this;
                if (this.controller.history.length > 0) {
                    that.updateHistoryPosition = true;
                    this.historyMenu.show({
                        top: event.pageY,
                        left: event.pageX + 1,
                        groups: that.getItems(that.controller.history, "controller.history"),
                        data: that
                    });
                }

                if (event != null) {
                    event.preventDefault();
                }
                return false;
            },

            showContextMenu: function showContextMenu(event, data) {
                var handlers = GEPPETTO.MenuManager.getCommandsProvidersFor(data.getMetaType());

                if (handlers.length > 0) {
                    var groups = [];
                    for (var handlerIndex = 0; handlerIndex < handlers.length; handlerIndex++) {
                        groups = groups.concat(handlers[handlerIndex](data));
                    }

                    this.contextMenu.show({
                        top: event.pageY,
                        left: event.pageX + 1,
                        groups: groups,
                        //registeredItems: registeredItems,
                        data: data
                    });
                }

                if (event != null) {
                    event.preventDefault();
                }

                return false;
            }

        }, _defineProperty(_Backbone$View$extend, 'showTitleBar', function showTitleBar(show) {
            this.hasTitleBar = show;

            if (show) {
                this.$el.parent().find(".ui-dialog-titlebar").show();
            } else {
                this.$el.parent().find(".ui-dialog-titlebar").hide();
            }

            // set flag to indicate something changed
            this.dirtyView = true;

            return this;
        }), _defineProperty(_Backbone$View$extend, 'updateNavigationHistoryBar', function updateNavigationHistoryBar() {
            var disabled = "arrow-disabled";
            if (this.getItems(this.controller.staticHistoryMenu, "controller.staticHistoryMenu").length <= 1) {
                if (!$("#" + this.id + "-left-nav").hasClass(disabled)) {
                    $("#" + this.id + "-left-nav").addClass(disabled);
                    $("#" + this.id + "-right-nav").addClass(disabled);
                }
            } else {
                if ($("#" + this.id + "-left-nav").hasClass(disabled)) {
                    $("#" + this.id + "-left-nav").removeClass(disabled);
                    $("#" + this.id + "-right-nav").removeClass(disabled);
                }
            }
        }), _defineProperty(_Backbone$View$extend, 'showHistoryNavigationBar', function showHistoryNavigationBar(show) {
            this.hasHistoryNavigationBar = show;
            var leftNav = $("#" + this.id + "-left-nav");
            var rightNav = $("#" + this.id + "-right-nav");

            if (show) {
                if (leftNav.length == 0 && rightNav.length == 0) {

                    var disabled = "";
                    if (this.getItems(this.controller.staticHistoryMenu, "controller.staticHistoryMenu").length <= 1) {
                        disabled = "arrow-disabled ";
                    }

                    var that = this;
                    var button = $("<div id='" + this.id + "-left-nav' class='" + disabled + "fa fa-arrow-left'></div>" + "<div id='" + this.id + "-right-nav' class='" + disabled + "fa fa-arrow-right'></div>").click(function (event) {
                        var historyItems = that.getItems(that.controller.staticHistoryMenu, "controller.staticHistoryMenu");
                        var item;
                        that.lastExecutedAction = $("#" + that.id).parent().find(".ui-dialog-title").html();
                        if (event.target.id == that.id + "-right-nav") {
                            that.executedAction = that.executedAction + 1;
                            if (that.executedAction >= historyItems.length) {
                                that.executedAction = 0;
                            }

                            var match = that.executedAction;
                            for (var i = 0; i < historyItems.length; i++) {
                                var currentItem = historyItems[i];
                                if (that.lastExecutedAction == currentItem.label) {
                                    match = i;
                                }
                            }

                            if (that.lastExecutedAction == historyItems[that.executedAction].label) {
                                that.executedAction = match + 1;
                            }

                            if (that.executedAction <= match) {
                                that.executedAction = match + 1;
                                if (that.executedAction >= historyItems.length) {
                                    that.executedAction = 0;
                                }
                            }
                        }
                        if (event.target.id == that.id + "-left-nav") {
                            that.executedAction = that.executedAction - 1;
                            if (that.executedAction <= -1) {
                                that.executedAction = historyItems.length - 1;
                            }

                            var match = that.executedAction;
                            for (var i = 0; i < historyItems.length; i++) {
                                var currentItem = historyItems[i];
                                if (that.lastExecutedAction == currentItem.label) {
                                    match = i;
                                }
                            }

                            if (that.lastExecutedAction == historyItems[that.executedAction].label) {
                                that.executedAction = match - 1;
                            }

                            if (that.executedAction <= -1) {
                                that.executedAction = historyItems.length - 1;
                            }

                            if (that.executedAction > match) {
                                that.executedAction = match - 1;
                                if (that.executedAction <= -1) {
                                    that.executedAction = historyItems.length - 1;
                                }
                            }
                        }
                        that.updateHistoryPosition = false;
                        item = historyItems[that.executedAction].action[0];
                        GEPPETTO.CommandController.execute(item, true);
                        $("#" + that.id).parent().find(".ui-dialog-title").html(historyItems[that.executedAction].label);
                        event.stopPropagation();
                    });

                    button.insertBefore(this.dialogParent.find("span.ui-dialog-title"));
                    $(button).addClass("widget-title-bar-button");
                }
            } else {
                if (leftNav.is(":visible") && rightNav.is(":visible")) {
                    leftNav.remove();
                    rightNav.remove();
                    this.executedAction = 0;
                }
            }
        }), _defineProperty(_Backbone$View$extend, 'showCloseButton', function showCloseButton(show) {
            if (show) {
                this.$el.parent().find(".ui-dialog-titlebar-close").show();
            } else {
                this.$el.parent().find(".ui-dialog-titlebar-close").hide();
            }
        }), _defineProperty(_Backbone$View$extend, 'addButtonToTitleBar', function addButtonToTitleBar(button) {
            this.dialogParent.find("div.ui-dialog-titlebar").prepend(button);
            $(button).addClass("widget-title-bar-button");
        }), _defineProperty(_Backbone$View$extend, 'setDraggable', function setDraggable(draggable) {
            if (draggable) {
                this.$el.parent().draggable({ disabled: false });
                // NOTE: this will wipe any class applied to the widget...
                this.setClass('');
            } else {
                this.$el.parent().draggable({ disabled: true });
                this.setClass('noStyleDisableDrag');
            }
        }), _defineProperty(_Backbone$View$extend, 'setTransparentBackground', function setTransparentBackground(isTransparent) {
            this.transparentBackground = isTransparent;

            if (isTransparent) {
                this.$el.parent().addClass('transparent-back');
                this.previousMaxTransparency = true;
            } else {
                this.$el.parent().removeClass('transparent-back');
            }
            return this;
        }), _defineProperty(_Backbone$View$extend, 'setClass', function setClass(className) {
            this.$el.dialog({ dialogClass: className }).dialogExtend();
        }), _defineProperty(_Backbone$View$extend, 'perfomEffect', function perfomEffect(effect, options, speed) {
            this.$el.parent().effect(effect, options, speed);
        }), _defineProperty(_Backbone$View$extend, 'shake', function shake(options, speed) {
            if (options === undefined) {
                options = { distance: 5, times: 3 };
            }
            if (speed === undefined) {
                speed = 500;
            }

            this.$el.parent().effect('shake', options, speed);
        }), _defineProperty(_Backbone$View$extend, 'render', function render() {
            var _$$dialog$dialogExten;

            var that = this;

            //create the dialog window for the widget
            this.dialog = $("<div id=" + this.id + " class='dialog' title='" + this.name + " Widget'></div>").dialog({
                resizable: true,
                draggable: true,
                top: 10,
                height: 300,
                width: 350,
                closeOnEscape: false,
                close: function close(event, ui) {
                    if (event.originalEvent && $(event.originalEvent.target).closest(".ui-dialog-titlebar-close").length) {
                        that.destroy();
                    }
                }
            }).dialogExtend((_$$dialog$dialogExten = {
                "closable": true,
                "maximizable": true,
                "minimizable": true,
                "collapsable": true,
                "restore": true,
                "minimizeLocation": "right",
                "icons": {
                    "maximize": "fa fa-expand",
                    "minimize": "fa fa-window-minimize",
                    "collapse": "fa  fa-chevron-circle-up",
                    "restore": "fa fa-compress"
                },
                "load": function load(evt, dlg) {
                    var icons = $("#" + that.id).parent().find(".ui-icon");
                    for (var i = 0; i < icons.length; i++) {
                        //remove text from span added by vendor library
                        $(icons[i]).text("");
                    }
                },
                "beforeMinimize": function beforeMinimize(evt, dlg) {
                    var label = that.name;
                    if (label != undefined) {
                        label = label.substring(0, 6);
                    }
                    that.$el.dialog({ title: label });
                },
                "beforeMaximize": function beforeMaximize(evt, dlg) {
                    var divheight = that.size.height;
                    var divwidth = that.size.width;
                    that.previousMaxSize = { width: divwidth, height: divheight };
                },
                "minimize": function minimize(evt, dlg) {
                    that.$el.dialog({ title: that.name });
                    $(".ui-dialog-titlebar-restore span").removeClass("fa-chevron-circle-down");
                    $(".ui-dialog-titlebar-restore span").removeClass("fa-compress");
                    $(".ui-dialog-titlebar-restore span").addClass("fa-window-restore");
                    that.$el.parent().css("z-index", zIndex.min);
                },
                "maximize": function maximize(evt, dlg) {
                    that.setTransparentBackground(false);
                    $(this).trigger('resizeEnd');
                    var divheight = $(window).height();
                    var divwidth = $(window).width();
                    that.$el.dialog({ height: divheight, width: divwidth });
                    $(".ui-dialog-titlebar-restore span").removeClass("fa-chevron-circle-down");
                    $(".ui-dialog-titlebar-restore span").removeClass("fa-window-restore");
                    $(".ui-dialog-titlebar-restore span").addClass("fa-compress");
                    that.maximize = true;
                    that.$el.parent().css("z-index", zIndex.max);
                    that.size = {
                        height: divheight,
                        width: divwidth
                    };
                }
            }, _defineProperty(_$$dialog$dialogExten, 'restore', function restore(evt, dlg) {
                if (that.maximize) {
                    that.setSize(that.previousMaxSize.height, that.previousMaxSize.width);
                    $(this).trigger('restored', [that.id]);
                }
                that.setTransparentBackground(that.previousMaxTransparency);
                $(this).trigger('resizeEnd');
                that.maximize = false;
                that.collapsed = false;
                that.$el.parent().css("z-index", zIndex.restore);
            }), _defineProperty(_$$dialog$dialogExten, "collapse", function collapse(evt, dlg) {
                $(".ui-dialog-titlebar-restore span").removeClass("fa-compress");
                $(".ui-dialog-titlebar-restore span").removeClass("fa-window-restore");
                $(".ui-dialog-titlebar-restore span").addClass("fa-chevron-circle-down");
                that.collapsed = true;
                that.$el.parent().css("z-index", zIndex.min);
            }), _$$dialog$dialogExten));

            this.$el = $("#" + this.id);
            this.dialogParent = this.$el.parent();

            //add history
            this.showHistoryIcon(true);

            //remove the jQuery UI icon
            this.dialogParent.find("button.ui-dialog-titlebar-close").html("");
            this.dialogParent.find("button").append("<i class='fa fa-close'></i>");

            //Take focus away from close button
            this.dialogParent.find("button.ui-dialog-titlebar-close").blur();

            //add help button
            this.showHelpIcon(true);
        }), _defineProperty(_Backbone$View$extend, 'registerEvent', function registerEvent(event, callback) {
            this.registeredEvents.push({ id: event, callback: callback });
        }), _defineProperty(_Backbone$View$extend, 'unregisterEvent', function unregisterEvent(event) {
            this.registeredEvents = _.reject(this.registeredEvents, function (el) {
                return el.id === event;
            });
        }), _defineProperty(_Backbone$View$extend, 'setHelpInfo', function setHelpInfo(helpInfo) {
            this.helpInfo = helpInfo;
        }), _defineProperty(_Backbone$View$extend, 'getHelp', function getHelp() {
            return this.helpInfo;
        }), _defineProperty(_Backbone$View$extend, 'setController', function setController(controller) {
            this.controller = controller;
        }), _defineProperty(_Backbone$View$extend, 'showHelpIcon', function showHelpIcon(show) {
            var that = this;
            if (show && this.$el.parent().find(".history-icon").length == 0) {
                this.addButtonToTitleBar($("<div class='fa fa-question help-icon' title='Widget Help'></div>").click(function () {
                    GEPPETTO.ComponentFactory.addComponent('MDMODAL', {
                        title: that.id.slice(0, -1) + ' help',
                        content: that.getHelp(),
                        show: true
                    }, document.getElementById("modal-region"));
                }));
            } else {
                this.$el.parent().find(".help-icon").remove();
            }
        }), _defineProperty(_Backbone$View$extend, 'showHistoryIcon', function showHistoryIcon(show) {
            var that = this;
            if (show && this.$el.parent().find(".history-icon").length == 0) {
                this.addButtonToTitleBar($("<div class='fa fa-history history-icon' title='Show Navigation History'></div>").click(function (event) {
                    that.showHistoryMenu(event);
                    event.stopPropagation();
                }));
            } else {
                this.$el.parent().find(".history-icon").remove();
            }
        }), _defineProperty(_Backbone$View$extend, 'getView', function getView() {
            // get default stuff such as id, position and size
            return {
                widgetType: this.widgetType,
                isWidget: this.isWidget(),
                showTitleBar: this.hasTitleBar,
                showHistoryNavigationBar: this.hasHistoryNavigationBar,
                transparentBackground: this.transparentBackground,
                name: this.name,
                size: {
                    height: this.size.height,
                    width: this.size.width
                },
                position: {
                    left: this.position.left,
                    top: this.position.top
                }
            };
        }), _defineProperty(_Backbone$View$extend, 'setView', function setView(view) {
            // set default stuff such as position and size
            if (view.size != undefined && view.size.height != 0 && view.size.width != 0) {
                this.setSize(view.size.height, view.size.width);
            } else {
                // trigger auto size if we have no size info
                this.setAutoWidth();
                this.setAutoHeight();
            }

            if (view.position != undefined) {
                this.setPosition(view.position.left, view.position.top);
            }

            if (view.name != undefined) {
                this.setName(view.name);
            }

            if (view.showTitleBar != undefined) {
                this.showTitleBar(view.showTitleBar);
            }

            if (view.showHistoryNavigationBar != undefined) {
                this.showHistoryNavigationBar(view.showHistoryNavigationBar);
            }

            if (view.transparentBackground != undefined) {
                this.setTransparentBackground(view.transparentBackground);
            }

            // after setting view through setView, reset dirty flag
            this.dirtyView = false;
        }), _defineProperty(_Backbone$View$extend, 'isStateLess', function isStateLess() {
            return this.stateless;
        }), _defineProperty(_Backbone$View$extend, 'isWidget', function isWidget() {
            return true;
        }), _Backbone$View$extend))
    };
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3372:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;/**
 * Variable visualiser Widget class
 * @module Widgets/VariableVisualiser
 * @author Dan Kruchinin (dkruchinin@acm.org)
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var Widget = __webpack_require__(2272);
    var $ = __webpack_require__(16);

    __webpack_require__(3373);

    return Widget.View.extend({
        root: null,
        variable: null,
        options: null,
        default_width: 350,
        default_height: 120,

        /**
         * Initialises variables visualiser with a set of options
         *
         * @param {Object} options - Object with options for the widget
         */
        initialize: function initialize(options) {
            Widget.View.prototype.initialize.call(this, options);

            if (!('width' in options)) {
                options.width = this.default_width;
            }
            if (!('height' in options)) {
                options.height = this.default_height;
            }

            this.render();
            this.setSize(options.height, options.width);
            this.dialog.append("<div class='varvis_header'></div><div class='varvis_body'></div>");
        },

        /**
         * Takes time series data and shows it as a floating point variable changing in time.
         *
         * @command addVariable(state, options)
         * @param {Object} state - time series data (a geppetto simulation variable)
         * @param {Object} options - options for the plotting widget, if null uses default
         */
        setVariable: function setVariable(state, options) {
            this.variable = {
                name: state.getInstancePath(),
                state: state
            };

            if (this.root == null) {
                this.root = $("#" + this.id);
            }

            this.setHeader(this.variable.name);
            this.updateVariable(0, false);

            // track change in state of the widget
            this.dirtyView = true;

            return "Variable visualisation added to widget";
        },

        /**
         * Clear variable
         *
         * @command removeVariable(state)
         *
         * @param {Object} state - geppetto similation variable to remove
         */
        clearVariable: function clearVariable() {
            if (this.variable == null) {
                return;
            }

            this.variable = null;
            this.setHeader("");
            this.setBody("");
        },

        /**
         * Updates variable values
         */
        updateVariable: function updateVariable(step) {
            if (typeof step != 'undefined' && (this.variable.state.getTimeSeries() != null || undefined)) {
                if (this.variable.state.getTimeSeries().length > step) {
                    this.setBody(this.variable.state.getTimeSeries()[step].toFixed(4) + this.variable.state.getUnit());
                }
            }
        },

        /**
         * Change name of the variable (if there's one)
         *
         * @param newName - the new name
         */
        renameVariable: function renameVariable(newName) {
            if (this.variable != null) {
                this.variable.name = newName;
                this.setHeader(newName);
            }
        },

        /**
         * @private
         */
        setHeader: function setHeader(content) {
            this.getSelector("varvis_header").html(content);
        },

        /**
         * @private
         */
        setBody: function setBody(content) {
            this.getSelector("varvis_body").html(content);
        },

        /**
         * @private
         */
        getSelector: function getSelector(name) {
            return $(this.root.selector + " ." + name);
        },

        getView: function getView() {
            var baseView = Widget.View.prototype.getView.call(this);

            // add data
            baseView.dataType = 'object';
            baseView.data = this.variable.name;

            return baseView;
        },

        setView: function setView(view) {
            // set base properties
            Widget.View.prototype.setView.call(this, view);

            if (view.dataType == 'object' && view.data != undefined && view.data != '') {
                var variable = eval(view.data);
                this.setVariable(variable);
            }

            // after setting view through setView, reset dirty flag
            this.dirtyView = false;
        }
    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3373:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(3374);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./VariableVisualiser.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./VariableVisualiser.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 3374:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\n.varvis_header {\n  width: 100%;\n  font-size: 14px;\n  color: white;\n  float: left;\n  text-align: center;\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.varvis_body {\n  width: 100%;\n  height: 100%;\n  font-size: 34px;\n  font-weight: bold;\n  color: #f23d7a;\n  float: left;\n  text-align: center;\n  vertical-align: middle;\n  resize: both;\n}\n", ""]);

// exports


/***/ })

});
//# sourceMappingURL=24.bundle.js.map