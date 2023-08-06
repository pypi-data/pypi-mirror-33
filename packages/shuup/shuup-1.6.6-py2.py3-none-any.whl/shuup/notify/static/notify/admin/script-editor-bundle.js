var ScriptEditor =
/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports, __webpack_require__) {

	/**
	 * This file is part of Shuup.
	 *
	 * Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
	 *
	 * This source code is licensed under the OSL-3.0 license found in the
	 * LICENSE file in the root directory of this source tree.
	 */
	const style = __webpack_require__(1);  // eslint-disable-line no-unused-vars
	const cx = __webpack_require__(6);
	const Messages = window.Messages;

	var settings = {};
	const names = {};
	const infos = {};
	var controller = null;
	const optionLists = {};

	function showSuccessAndError(data) {
	    if (data.error) {
	        Messages.enqueue({
	            text: _.isString(data.error) ? data.error : gettext("An error occurred."),
	            tags: "error"
	        });
	    }
	    if (data.success) {
	        Messages.enqueue({
	            text: _.isString(data.success) ? data.success : gettext("Success."),
	            tags: "success"
	        });
	    }
	}

	function apiRequest(command, data, options) {
	    const request = _.extend({}, {"command": command}, data || {});
	    const req = m.request(_.extend({
	        method: "POST",
	        url: settings.apiUrl,
	        data: request,
	        config: function(xhr) {
	            xhr.setRequestHeader("X-CSRFToken", window.ShuupAdminConfig.csrf);
	        }
	    }, options));
	    req.then(function(response) {
	        showSuccessAndError(response);
	    }, function() {
	        Messages.enqueue({text: gettext("An unspecified error occurred."), tags: "error"});
	    });
	    return req;
	}

	function Controller() {
	    const ctrl = this;
	    ctrl.steps = m.prop([]);
	    ctrl.currentItem = m.prop(null);
	    ctrl.newStepItemModalInfo = m.prop(null);

	    apiRequest("getData").then(function(data) {
	        ctrl.steps(data.steps);
	    });

	    ctrl.removeStepItem = function(step, itemType, item) {
	        const listName = itemType + "s";
	        step[listName] = _.reject(step[listName], function(i) {
	            return i === item;
	        });
	        if (ctrl.currentItem() === item) {
	            ctrl.activateStepItem(null, null, null);
	        }
	    };

	    ctrl.addStepItem = function(step, itemType, identifier, activateForEdit) {
	        const item = {"identifier": identifier};
	        const listName = itemType + "s";
	        step[listName].push(item);
	        if (activateForEdit) {
	            ctrl.activateStepItem(step, itemType, item);
	        }
	    };
	    ctrl.setStepItemEditorState = function(state) {
	        if (state) {
	            document.getElementById("step-item-wrapper").style.display = "block";
	        } else {
	            document.getElementById("step-item-wrapper").style.display = "none";
	            document.getElementById("step-item-frame").src = "about:blank";
	        }
	    };
	    ctrl.activateStepItem = function(step, itemType, item) {
	        if (step && item) {
	            ctrl.currentItem(item);
	            const frm = _.extend(document.createElement("form"), {
	                target: "step-item-frame",
	                method: "POST",
	                action: settings.itemEditorUrl
	            });
	            frm.appendChild(_.extend(document.createElement("input"), {
	                name: "init_data",
	                type: "hidden",
	                value: JSON.stringify({
	                    eventIdentifier: settings.eventIdentifier,
	                    itemType: itemType,
	                    data: item
	                })
	            }));
	            document.body.appendChild(frm);
	            frm.submit();
	            ctrl.setStepItemEditorState(true);
	        } else {
	            ctrl.currentItem(null);
	            ctrl.setStepItemEditorState(false);
	        }
	    };
	    ctrl.receiveItemEditData = function(data) {
	        const currentItem = ctrl.currentItem();
	        if (!currentItem) {
	            alert(gettext("Unexpected edit data received."));
	            return;
	        }
	        m.startComputation();
	        ctrl.currentItem(_.extend(currentItem, data));
	        m.endComputation();
	    };
	    ctrl.saveState = function() {
	        apiRequest("saveData", {
	            steps: ctrl.steps()
	        });

	        // TODO: Handle errors here?
	    };
	    ctrl.deleteStep = function(step) {
	        ctrl.steps(_.reject(ctrl.steps(), function(s) {
	            return s === step;
	        }));
	    };
	    ctrl.addNewStep = function() {
	        const step = {
	            actions: [],
	            conditions: [],
	            enabled: true,
	            next: "continue",
	            condOp: "and"
	        };
	        const steps = ctrl.steps();
	        steps.push(step);
	        ctrl.steps(steps);
	    };
	    ctrl.moveStep = function(step, delta) {
	        const steps = ctrl.steps();
	        const oldIndex = _.indexOf(steps, step);
	        if (oldIndex === -1) {
	            return false;
	        }
	        const newIndex = oldIndex + delta;
	        steps.splice(newIndex, 0, steps.splice(oldIndex, 1)[0]);
	        ctrl.steps(steps);
	    };
	    ctrl.promptForNewStepItem = function(step, itemType) {
	        ctrl.newStepItemModalInfo({
	            step: step,
	            itemType: itemType,
	            title: gettext("Add new") + " " + itemType
	        });
	    };
	    ctrl.closeNewStepItemModal = function() {
	        ctrl.newStepItemModalInfo(null);
	    };
	    ctrl.createNewStepItemFromModal = function(identifier) {
	        const info = ctrl.newStepItemModalInfo();
	        ctrl.closeNewStepItemModal();
	        if (info === null) {
	            return;
	        }
	        ctrl.addStepItem(info.step, info.itemType, identifier, true);
	    };
	}

	function workflowItemList(ctrl, step, itemType) {
	    const listName = itemType + "s";
	    const nameMap = names[itemType];
	    const items = step[listName];
	    const list = m("ul.action-list", items.map(function(item) {
	        const name = nameMap[item.identifier] || item.identifier;
	        var tag = "li";
	        const current = (ctrl.currentItem() === item);
	        if (current) {
	            tag += ".current";
	        }
	        return m(tag,
	            [
	                m("a", {
	                    href: "#",
	                    onclick: (!current ? _.partial(ctrl.activateStepItem, step, itemType, item) : null)
	                }, name),
	                " ",
	                m("a.delete", {
	                    href: "#", onclick: function() {
	                        if (!confirm(gettext("Delete this item?\nThis can not be undone."))) {
	                            return;
	                        }
	                        ctrl.removeStepItem(step, itemType, item);
	                    }
	                }, m("i.fa.fa-trash"))
	            ]
	        );
	    }));
	    return m("div", [
	        list,
	        m("div.action-new", [m("a.btn.btn-xs.btn-primary", {
	            href: "#",
	            onclick: _.partial(ctrl.promptForNewStepItem, step, itemType)
	        }, m("i.fa.fa-plus"), " " + gettext("New") + " " + itemType)])
	    ]);
	}

	function stepTableRows(ctrl) {
	    return _.map(ctrl.steps(), function(step, index) {
	        const condOpSelect = m("select", {
	            value: step.cond_op,
	            onchange: m.withAttr("value", function(value) {
	                step.cond_op = value;  // eslint-disable-line camelcase
	            })
	        }, optionLists.condOps);
	        const stepNextSelect = m("select", {
	            value: step.next,
	            onchange: m.withAttr("value", function(value) {
	                step.next = value;
	            })
	        }, optionLists.stepNexts);

	        return m("div", {
	            className: cx("step", {disabled: !step.enabled}),
	            key: step.id
	        }, [
	            m("div.step-buttons", [
	                (index > 0 ? m("a", {
	                    href: "#",
	                    title: gettext("Move Up"),
	                    onclick: _.partial(ctrl.moveStep, step, -1)
	                }, m("i.fa.fa-caret-up")) : null),
	                (index < ctrl.steps().length - 1 ? m("a", {
	                    href: "#",
	                    title: gettext("Move Down"),
	                    onclick: _.partial(ctrl.moveStep, step, +1)
	                }, m("i.fa.fa-caret-down")) : null),
	                (step.enabled ?
	                    m("a", {
	                        href: "#", title: gettext("Disable"), onclick: function() {
	                            step.enabled = false;
	                        }
	                    }, m("i.fa.fa-ban")) :
	                    m("a", {
	                        href: "#", title: gettext("Enable"), onclick: function() {
	                            step.enabled = true;
	                        }
	                    }, m("i.fa.fa-check-circle"))
	                ),
	                m("a", {
	                    href: "#", title: gettext("Delete"), onclick: function() {
	                        if (confirm(gettext("Are you sure you wish to delete this step?"))) {
	                            ctrl.deleteStep(step);
	                        }
	                    }
	                }, m("i.fa.fa-trash"))
	            ]),
	            m("div.step-conds", [
	                m("span.hint", gettext("If"), condOpSelect, gettext("of these conditions hold...")),
	                workflowItemList(ctrl, step, "condition")
	            ]),
	            m("div.step-actions", [
	                m("span.hint", gettext("then execute these actions...")),
	                workflowItemList(ctrl, step, "action")
	            ]),
	            m("div.step-next", [
	                m("span.hint", gettext("and then...")),
	                stepNextSelect
	            ])
	        ]);
	    });
	}

	function renderNewStepItemModal(ctrl, modalInfo) {
	    return m("div.new-step-item-modal-overlay", {onclick: ctrl.closeNewStepItemModal}, [
	        m("div.new-step-item-modal", [
	            m("div.title", modalInfo.title),
	            m("div.item-options", _.map(_.sortBy(_.values(infos[modalInfo.itemType]), "name"), function(item) {
	                return m("div.item-option", {onclick: _.partial(ctrl.createNewStepItemFromModal, item.identifier)}, [
	                    m("div.item-name", item.name),
	                    (item.description ? m("div.item-description", item.description) : null)
	                ]);
	            }))
	        ])
	    ]);
	}

	function view(ctrl) {
	    var modal = null, modalInfo = null;
	    if ((modalInfo = ctrl.newStepItemModalInfo()) !== null) {
	        modal = renderNewStepItemModal(ctrl, modalInfo);
	    }
	    return m("div.step-list-wrapper", [
	        m("div.steps", [
	            stepTableRows(ctrl),
	            m("hr.script-separator"),
	            m(
	                "a.new-step-link.btn.btn-info.btn-sm",
	                {href: "#", onclick: ctrl.addNewStep},
	                m("i.fa.fa-plus"), " " + gettext("New step")
	            )
	        ]),
	        modal
	    ]);
	}

	function generateItemOptions(nameMap) {
	    return _.sortBy(_.map(nameMap, function(name, value) {
	        return m("option", {value: value}, name);
	    }), function(o) {
	        return o.children[0].toLowerCase();
	    });
	}

	function itemInfosToNameMap(itemInfos) {
	    return _(itemInfos).map(function (itemInfo, identifier){ return [identifier, itemInfo.name]; }).zipObject().value();
	}

	function init(iSettings) {
	    settings = _.extend({}, iSettings);
	    infos.condition = settings.conditionInfos;
	    infos.action = settings.actionInfos;
	    names.condition = itemInfosToNameMap(infos.condition);
	    names.action = itemInfosToNameMap(infos.action);
	    optionLists.condOps = generateItemOptions(settings.condOps);
	    optionLists.stepNexts = generateItemOptions(settings.stepNexts);

	    controller = m.mount(document.getElementById("step-table-container"), {
	        controller: Controller,
	        view: view
	    });
	    window.addEventListener("message", function(event) {
	        if (event.data.new_data) {
	            controller.receiveItemEditData(event.data.new_data);
	        }
	    }, false);
	}

	function save() {
	    controller.saveState();
	}

	module.exports.init = init;
	module.exports.save = save;
	module.exports.hideEditModal = function() {
	    if (controller) {
	        m.startComputation();
	        controller.setStepItemEditorState(false);
	        controller.activateStepItem(null);  // Deactivate the modal once data is received
	        m.endComputation();
	    }
	};


/***/ }),
/* 1 */
/***/ (function(module, exports, __webpack_require__) {

	
	var content = __webpack_require__(2);

	if(typeof content === 'string') content = [[module.id, content, '']];

	var transform;
	var insertInto;



	var options = {"hmr":true}

	options.transform = transform
	options.insertInto = undefined;

	var update = __webpack_require__(4)(content, options);

	if(content.locals) module.exports = content.locals;

	if(false) {
		module.hot.accept("!!../node_modules/css-loader/index.js!../node_modules/autoprefixer-loader/index.js!../node_modules/less-loader/dist/cjs.js!./script-editor.less", function() {
			var newContent = require("!!../node_modules/css-loader/index.js!../node_modules/autoprefixer-loader/index.js!../node_modules/less-loader/dist/cjs.js!./script-editor.less");

			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];

			var locals = (function(a, b) {
				var key, idx = 0;

				for(key in a) {
					if(!b || a[key] !== b[key]) return false;
					idx++;
				}

				for(key in b) idx--;

				return idx === 0;
			}(content.locals, newContent.locals));

			if(!locals) throw new Error('Aborting CSS HMR due to changed css-modules locals.');

			update(newContent);
		});

		module.hot.dispose(function() { update(); });
	}

/***/ }),
/* 2 */
/***/ (function(module, exports, __webpack_require__) {

	exports = module.exports = __webpack_require__(3)(false);
	// imports


	// module
	exports.push([module.id, ".step-list-wrapper {\n  position: relative;\n}\n.step {\n  border: 1px solid rgba(53, 164, 140, 0.75);\n  border-radius: 4px;\n  background: #fff;\n  margin-bottom: 1em;\n}\n@media (min-width: 768px) {\n  .step {\n    display: -ms-flexbox;\n    display: flex;\n  }\n}\n.step > div {\n  padding: 12px 15px;\n}\n@media (max-width: 767px) {\n  .step > div {\n    border: solid #ddd;\n    border-width: 1px 0px 0px 0px;\n  }\n  .step > div:first-child {\n    border-width: 0;\n    padding: 6px 15px;\n  }\n}\n.step.disabled .step-conds,\n.step.disabled .step-actions,\n.step.disabled .step-next {\n  opacity: 0.3;\n  pointer-events: none;\n}\n.step .hint {\n  display: block;\n  margin-bottom: 5px;\n}\n.step .hint select {\n  margin: 0px 5px;\n}\n.step-buttons {\n  background: #35A48C;\n}\n@media (min-width: 768px) {\n  .step-buttons {\n    -ms-flex: 0 0 auto;\n        flex: 0 0 auto;\n  }\n}\n.step-buttons a {\n  color: rgba(255, 255, 255, 0.7);\n  display: inline-block;\n  text-align: center;\n  padding: 6px 10px;\n  margin-right: 10px;\n  font-size: 16px;\n  line-height: 16px;\n  text-decoration: none;\n}\n.step-buttons a:hover,\n.step-buttons a:focus {\n  color: #fff;\n}\n@media (min-width: 768px) {\n  .step-buttons a {\n    display: block;\n    float: none;\n    margin: 4px 0px;\n    padding: 3px;\n    width: 20px;\n    height: 20px;\n  }\n}\n@media (min-width: 768px) {\n  .step-conds,\n  .step-actions,\n  .step-next {\n    -ms-flex: 2;\n        flex: 2;\n  }\n}\nul.action-list {\n  list-style: none;\n  margin: 0;\n  padding: 0;\n}\nul.action-list li {\n  padding: 2px;\n  display: block;\n  width: 100%;\n}\nul.action-list li.current {\n  font-weight: bold;\n}\nul.action-list li .delete {\n  margin-left: 5px;\n  padding: 3px;\n  color: #777777;\n}\nul.action-list li .delete:hover,\nul.action-list li .delete:focus {\n  color: #e74c3c;\n}\nhr.script-separator {\n  border-color: #ddd;\n}\n.action-new {\n  margin-top: 10px;\n}\n@media (min-width: 768px) {\n  .action-new {\n    padding-top: 10px;\n    border-top: 1px solid #ddd;\n  }\n}\n.new-step-item-modal-overlay {\n  position: absolute;\n  top: 0;\n  left: 0;\n  width: 100%;\n  height: 100%;\n  background: rgba(244, 244, 244, 0.75);\n}\n.new-step-item-modal {\n  max-width: 100%;\n  margin: auto;\n  margin-top: 1em;\n  background: #fff;\n  border: 1px solid #35A48C;\n  border-radius: 4px;\n  overflow: hidden;\n}\n@media (min-width: 768px) {\n  .new-step-item-modal {\n    width: 50%;\n  }\n}\n.new-step-item-modal .title {\n  padding: 10px 15px;\n  background: #35A48C;\n  color: #fff;\n  font-size: 1.8rem;\n}\n.new-step-item-modal .item-options {\n  max-height: 300px;\n  overflow-y: scroll;\n  margin: auto;\n  padding: 10px 0px;\n}\n.new-step-item-modal .item-option {\n  padding: 5px 15px;\n  cursor: pointer;\n}\n.new-step-item-modal .item-option:hover {\n  background: #eee;\n}\n.new-step-item-modal .item-option .item-name {\n  font-weight: normal;\n}\n.new-step-item-modal .item-option .item-description {\n  margin: 0.5em;\n  font-size: 90%;\n}\n#step-table-container {\n  margin-bottom: 15px;\n}\n.iframe-container {\n  padding-top: 30px;\n  margin-top: 15px;\n  border-top: 1px solid #ddd;\n}\n#step-item-frame {\n  width: 100%;\n  height: 100%;\n}\n", ""]);

	// exports


/***/ }),
/* 3 */
/***/ (function(module, exports) {

	/*
		MIT License http://www.opensource.org/licenses/mit-license.php
		Author Tobias Koppers @sokra
	*/
	// css base code, injected by the css-loader
	module.exports = function(useSourceMap) {
		var list = [];

		// return the list of modules as css string
		list.toString = function toString() {
			return this.map(function (item) {
				var content = cssWithMappingToString(item, useSourceMap);
				if(item[2]) {
					return "@media " + item[2] + "{" + content + "}";
				} else {
					return content;
				}
			}).join("");
		};

		// import a list of modules into the list
		list.i = function(modules, mediaQuery) {
			if(typeof modules === "string")
				modules = [[null, modules, ""]];
			var alreadyImportedModules = {};
			for(var i = 0; i < this.length; i++) {
				var id = this[i][0];
				if(typeof id === "number")
					alreadyImportedModules[id] = true;
			}
			for(i = 0; i < modules.length; i++) {
				var item = modules[i];
				// skip already imported module
				// this implementation is not 100% perfect for weird media query combinations
				//  when a module is imported multiple times with different media queries.
				//  I hope this will never occur (Hey this way we have smaller bundles)
				if(typeof item[0] !== "number" || !alreadyImportedModules[item[0]]) {
					if(mediaQuery && !item[2]) {
						item[2] = mediaQuery;
					} else if(mediaQuery) {
						item[2] = "(" + item[2] + ") and (" + mediaQuery + ")";
					}
					list.push(item);
				}
			}
		};
		return list;
	};

	function cssWithMappingToString(item, useSourceMap) {
		var content = item[1] || '';
		var cssMapping = item[3];
		if (!cssMapping) {
			return content;
		}

		if (useSourceMap && typeof btoa === 'function') {
			var sourceMapping = toComment(cssMapping);
			var sourceURLs = cssMapping.sources.map(function (source) {
				return '/*# sourceURL=' + cssMapping.sourceRoot + source + ' */'
			});

			return [content].concat(sourceURLs).concat([sourceMapping]).join('\n');
		}

		return [content].join('\n');
	}

	// Adapted from convert-source-map (MIT)
	function toComment(sourceMap) {
		// eslint-disable-next-line no-undef
		var base64 = btoa(unescape(encodeURIComponent(JSON.stringify(sourceMap))));
		var data = 'sourceMappingURL=data:application/json;charset=utf-8;base64,' + base64;

		return '/*# ' + data + ' */';
	}


/***/ }),
/* 4 */
/***/ (function(module, exports, __webpack_require__) {

	/*
		MIT License http://www.opensource.org/licenses/mit-license.php
		Author Tobias Koppers @sokra
	*/

	var stylesInDom = {};

	var	memoize = function (fn) {
		var memo;

		return function () {
			if (typeof memo === "undefined") memo = fn.apply(this, arguments);
			return memo;
		};
	};

	var isOldIE = memoize(function () {
		// Test for IE <= 9 as proposed by Browserhacks
		// @see http://browserhacks.com/#hack-e71d8692f65334173fee715c222cb805
		// Tests for existence of standard globals is to allow style-loader
		// to operate correctly into non-standard environments
		// @see https://github.com/webpack-contrib/style-loader/issues/177
		return window && document && document.all && !window.atob;
	});

	var getTarget = function (target) {
	  return document.querySelector(target);
	};

	var getElement = (function (fn) {
		var memo = {};

		return function(target) {
	                // If passing function in options, then use it for resolve "head" element.
	                // Useful for Shadow Root style i.e
	                // {
	                //   insertInto: function () { return document.querySelector("#foo").shadowRoot }
	                // }
	                if (typeof target === 'function') {
	                        return target();
	                }
	                if (typeof memo[target] === "undefined") {
				var styleTarget = getTarget.call(this, target);
				// Special case to return head of iframe instead of iframe itself
				if (window.HTMLIFrameElement && styleTarget instanceof window.HTMLIFrameElement) {
					try {
						// This will throw an exception if access to iframe is blocked
						// due to cross-origin restrictions
						styleTarget = styleTarget.contentDocument.head;
					} catch(e) {
						styleTarget = null;
					}
				}
				memo[target] = styleTarget;
			}
			return memo[target]
		};
	})();

	var singleton = null;
	var	singletonCounter = 0;
	var	stylesInsertedAtTop = [];

	var	fixUrls = __webpack_require__(5);

	module.exports = function(list, options) {
		if (false) {
			if (typeof document !== "object") throw new Error("The style-loader cannot be used in a non-browser environment");
		}

		options = options || {};

		options.attrs = typeof options.attrs === "object" ? options.attrs : {};

		// Force single-tag solution on IE6-9, which has a hard limit on the # of <style>
		// tags it will allow on a page
		if (!options.singleton && typeof options.singleton !== "boolean") options.singleton = isOldIE();

		// By default, add <style> tags to the <head> element
	        if (!options.insertInto) options.insertInto = "head";

		// By default, add <style> tags to the bottom of the target
		if (!options.insertAt) options.insertAt = "bottom";

		var styles = listToStyles(list, options);

		addStylesToDom(styles, options);

		return function update (newList) {
			var mayRemove = [];

			for (var i = 0; i < styles.length; i++) {
				var item = styles[i];
				var domStyle = stylesInDom[item.id];

				domStyle.refs--;
				mayRemove.push(domStyle);
			}

			if(newList) {
				var newStyles = listToStyles(newList, options);
				addStylesToDom(newStyles, options);
			}

			for (var i = 0; i < mayRemove.length; i++) {
				var domStyle = mayRemove[i];

				if(domStyle.refs === 0) {
					for (var j = 0; j < domStyle.parts.length; j++) domStyle.parts[j]();

					delete stylesInDom[domStyle.id];
				}
			}
		};
	};

	function addStylesToDom (styles, options) {
		for (var i = 0; i < styles.length; i++) {
			var item = styles[i];
			var domStyle = stylesInDom[item.id];

			if(domStyle) {
				domStyle.refs++;

				for(var j = 0; j < domStyle.parts.length; j++) {
					domStyle.parts[j](item.parts[j]);
				}

				for(; j < item.parts.length; j++) {
					domStyle.parts.push(addStyle(item.parts[j], options));
				}
			} else {
				var parts = [];

				for(var j = 0; j < item.parts.length; j++) {
					parts.push(addStyle(item.parts[j], options));
				}

				stylesInDom[item.id] = {id: item.id, refs: 1, parts: parts};
			}
		}
	}

	function listToStyles (list, options) {
		var styles = [];
		var newStyles = {};

		for (var i = 0; i < list.length; i++) {
			var item = list[i];
			var id = options.base ? item[0] + options.base : item[0];
			var css = item[1];
			var media = item[2];
			var sourceMap = item[3];
			var part = {css: css, media: media, sourceMap: sourceMap};

			if(!newStyles[id]) styles.push(newStyles[id] = {id: id, parts: [part]});
			else newStyles[id].parts.push(part);
		}

		return styles;
	}

	function insertStyleElement (options, style) {
		var target = getElement(options.insertInto)

		if (!target) {
			throw new Error("Couldn't find a style target. This probably means that the value for the 'insertInto' parameter is invalid.");
		}

		var lastStyleElementInsertedAtTop = stylesInsertedAtTop[stylesInsertedAtTop.length - 1];

		if (options.insertAt === "top") {
			if (!lastStyleElementInsertedAtTop) {
				target.insertBefore(style, target.firstChild);
			} else if (lastStyleElementInsertedAtTop.nextSibling) {
				target.insertBefore(style, lastStyleElementInsertedAtTop.nextSibling);
			} else {
				target.appendChild(style);
			}
			stylesInsertedAtTop.push(style);
		} else if (options.insertAt === "bottom") {
			target.appendChild(style);
		} else if (typeof options.insertAt === "object" && options.insertAt.before) {
			var nextSibling = getElement(options.insertInto + " " + options.insertAt.before);
			target.insertBefore(style, nextSibling);
		} else {
			throw new Error("[Style Loader]\n\n Invalid value for parameter 'insertAt' ('options.insertAt') found.\n Must be 'top', 'bottom', or Object.\n (https://github.com/webpack-contrib/style-loader#insertat)\n");
		}
	}

	function removeStyleElement (style) {
		if (style.parentNode === null) return false;
		style.parentNode.removeChild(style);

		var idx = stylesInsertedAtTop.indexOf(style);
		if(idx >= 0) {
			stylesInsertedAtTop.splice(idx, 1);
		}
	}

	function createStyleElement (options) {
		var style = document.createElement("style");

		if(options.attrs.type === undefined) {
			options.attrs.type = "text/css";
		}

		addAttrs(style, options.attrs);
		insertStyleElement(options, style);

		return style;
	}

	function createLinkElement (options) {
		var link = document.createElement("link");

		if(options.attrs.type === undefined) {
			options.attrs.type = "text/css";
		}
		options.attrs.rel = "stylesheet";

		addAttrs(link, options.attrs);
		insertStyleElement(options, link);

		return link;
	}

	function addAttrs (el, attrs) {
		Object.keys(attrs).forEach(function (key) {
			el.setAttribute(key, attrs[key]);
		});
	}

	function addStyle (obj, options) {
		var style, update, remove, result;

		// If a transform function was defined, run it on the css
		if (options.transform && obj.css) {
		    result = options.transform(obj.css);

		    if (result) {
		    	// If transform returns a value, use that instead of the original css.
		    	// This allows running runtime transformations on the css.
		    	obj.css = result;
		    } else {
		    	// If the transform function returns a falsy value, don't add this css.
		    	// This allows conditional loading of css
		    	return function() {
		    		// noop
		    	};
		    }
		}

		if (options.singleton) {
			var styleIndex = singletonCounter++;

			style = singleton || (singleton = createStyleElement(options));

			update = applyToSingletonTag.bind(null, style, styleIndex, false);
			remove = applyToSingletonTag.bind(null, style, styleIndex, true);

		} else if (
			obj.sourceMap &&
			typeof URL === "function" &&
			typeof URL.createObjectURL === "function" &&
			typeof URL.revokeObjectURL === "function" &&
			typeof Blob === "function" &&
			typeof btoa === "function"
		) {
			style = createLinkElement(options);
			update = updateLink.bind(null, style, options);
			remove = function () {
				removeStyleElement(style);

				if(style.href) URL.revokeObjectURL(style.href);
			};
		} else {
			style = createStyleElement(options);
			update = applyToTag.bind(null, style);
			remove = function () {
				removeStyleElement(style);
			};
		}

		update(obj);

		return function updateStyle (newObj) {
			if (newObj) {
				if (
					newObj.css === obj.css &&
					newObj.media === obj.media &&
					newObj.sourceMap === obj.sourceMap
				) {
					return;
				}

				update(obj = newObj);
			} else {
				remove();
			}
		};
	}

	var replaceText = (function () {
		var textStore = [];

		return function (index, replacement) {
			textStore[index] = replacement;

			return textStore.filter(Boolean).join('\n');
		};
	})();

	function applyToSingletonTag (style, index, remove, obj) {
		var css = remove ? "" : obj.css;

		if (style.styleSheet) {
			style.styleSheet.cssText = replaceText(index, css);
		} else {
			var cssNode = document.createTextNode(css);
			var childNodes = style.childNodes;

			if (childNodes[index]) style.removeChild(childNodes[index]);

			if (childNodes.length) {
				style.insertBefore(cssNode, childNodes[index]);
			} else {
				style.appendChild(cssNode);
			}
		}
	}

	function applyToTag (style, obj) {
		var css = obj.css;
		var media = obj.media;

		if(media) {
			style.setAttribute("media", media)
		}

		if(style.styleSheet) {
			style.styleSheet.cssText = css;
		} else {
			while(style.firstChild) {
				style.removeChild(style.firstChild);
			}

			style.appendChild(document.createTextNode(css));
		}
	}

	function updateLink (link, options, obj) {
		var css = obj.css;
		var sourceMap = obj.sourceMap;

		/*
			If convertToAbsoluteUrls isn't defined, but sourcemaps are enabled
			and there is no publicPath defined then lets turn convertToAbsoluteUrls
			on by default.  Otherwise default to the convertToAbsoluteUrls option
			directly
		*/
		var autoFixUrls = options.convertToAbsoluteUrls === undefined && sourceMap;

		if (options.convertToAbsoluteUrls || autoFixUrls) {
			css = fixUrls(css);
		}

		if (sourceMap) {
			// http://stackoverflow.com/a/26603875
			css += "\n/*# sourceMappingURL=data:application/json;base64," + btoa(unescape(encodeURIComponent(JSON.stringify(sourceMap)))) + " */";
		}

		var blob = new Blob([css], { type: "text/css" });

		var oldSrc = link.href;

		link.href = URL.createObjectURL(blob);

		if(oldSrc) URL.revokeObjectURL(oldSrc);
	}


/***/ }),
/* 5 */
/***/ (function(module, exports) {

	
	/**
	 * When source maps are enabled, `style-loader` uses a link element with a data-uri to
	 * embed the css on the page. This breaks all relative urls because now they are relative to a
	 * bundle instead of the current page.
	 *
	 * One solution is to only use full urls, but that may be impossible.
	 *
	 * Instead, this function "fixes" the relative urls to be absolute according to the current page location.
	 *
	 * A rudimentary test suite is located at `test/fixUrls.js` and can be run via the `npm test` command.
	 *
	 */

	module.exports = function (css) {
	  // get current location
	  var location = typeof window !== "undefined" && window.location;

	  if (!location) {
	    throw new Error("fixUrls requires window.location");
	  }

		// blank or null?
		if (!css || typeof css !== "string") {
		  return css;
	  }

	  var baseUrl = location.protocol + "//" + location.host;
	  var currentDir = baseUrl + location.pathname.replace(/\/[^\/]*$/, "/");

		// convert each url(...)
		/*
		This regular expression is just a way to recursively match brackets within
		a string.

		 /url\s*\(  = Match on the word "url" with any whitespace after it and then a parens
		   (  = Start a capturing group
		     (?:  = Start a non-capturing group
		         [^)(]  = Match anything that isn't a parentheses
		         |  = OR
		         \(  = Match a start parentheses
		             (?:  = Start another non-capturing groups
		                 [^)(]+  = Match anything that isn't a parentheses
		                 |  = OR
		                 \(  = Match a start parentheses
		                     [^)(]*  = Match anything that isn't a parentheses
		                 \)  = Match a end parentheses
		             )  = End Group
	              *\) = Match anything and then a close parens
	          )  = Close non-capturing group
	          *  = Match anything
	       )  = Close capturing group
		 \)  = Match a close parens

		 /gi  = Get all matches, not the first.  Be case insensitive.
		 */
		var fixedCss = css.replace(/url\s*\(((?:[^)(]|\((?:[^)(]+|\([^)(]*\))*\))*)\)/gi, function(fullMatch, origUrl) {
			// strip quotes (if they exist)
			var unquotedOrigUrl = origUrl
				.trim()
				.replace(/^"(.*)"$/, function(o, $1){ return $1; })
				.replace(/^'(.*)'$/, function(o, $1){ return $1; });

			// already a full url? no change
			if (/^(#|data:|http:\/\/|https:\/\/|file:\/\/\/|\s*$)/i.test(unquotedOrigUrl)) {
			  return fullMatch;
			}

			// convert the url to a full url
			var newUrl;

			if (unquotedOrigUrl.indexOf("//") === 0) {
			  	//TODO: should we add protocol?
				newUrl = unquotedOrigUrl;
			} else if (unquotedOrigUrl.indexOf("/") === 0) {
				// path should be relative to the base url
				newUrl = baseUrl + unquotedOrigUrl; // already starts with '/'
			} else {
				// path should be relative to current directory
				newUrl = currentDir + unquotedOrigUrl.replace(/^\.\//, ""); // Strip leading './'
			}

			// send back the fixed url(...)
			return "url(" + JSON.stringify(newUrl) + ")";
		});

		// send back the fixed css
		return fixedCss;
	};


/***/ }),
/* 6 */
/***/ (function(module, exports, __webpack_require__) {

	var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/*!
	  Copyright (c) 2016 Jed Watson.
	  Licensed under the MIT License (MIT), see
	  http://jedwatson.github.io/classnames
	*/
	/* global define */

	(function () {
		'use strict';

		var hasOwn = {}.hasOwnProperty;

		function classNames () {
			var classes = [];

			for (var i = 0; i < arguments.length; i++) {
				var arg = arguments[i];
				if (!arg) continue;

				var argType = typeof arg;

				if (argType === 'string' || argType === 'number') {
					classes.push(arg);
				} else if (Array.isArray(arg)) {
					classes.push(classNames.apply(null, arg));
				} else if (argType === 'object') {
					for (var key in arg) {
						if (hasOwn.call(arg, key) && arg[key]) {
							classes.push(key);
						}
					}
				}
			}

			return classes.join(' ');
		}

		if (typeof module !== 'undefined' && module.exports) {
			module.exports = classNames;
		} else if (true) {
			// register as 'classnames', consistent with npm package name
			!(__WEBPACK_AMD_DEFINE_ARRAY__ = [], __WEBPACK_AMD_DEFINE_RESULT__ = function () {
				return classNames;
			}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__), __WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
		} else {
			window.classNames = classNames;
		}
	}());


/***/ })
/******/ ]);