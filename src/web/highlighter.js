class Highlighter {
    addonPackage = document.currentScript
        .getAttribute("src")
        .match(/_addons\/(.+?)\//)[1];

    constructor() {
        this.timeoutID = undefined;
    }

    _injectStylesheet(root, editable, url) {
        const link = document.createElement("link");
        link.title = "Editor Highlighter Field Styles";
        link.type = "text/css";
        link.rel = "stylesheet";
        link.href = url;
        root.insertBefore(link, editable);
    }
    _inject(editable) {
        const root = editable.getRootNode();
        if (!root.querySelector("link[title*='Editor Highlighter']")) {
            this._injectStylesheet(
                root,
                editable,
                `/_addons/${this.addonPackage}/user_files/highlight.css`
            );
        }
    }

    _highlight(element, terms) {
        const instance = new Mark(element);
        for (const [classes, patterns] of Object.entries(terms)) {
            let classList = [];
            if (classes.trim()) {
                classList.push(...classes.trim().split(" "));
            }
            for (const pattern of patterns) {
                let markFunc = instance.mark;
                let keyword;
                if (typeof pattern === "object") {
                    markFunc = instance.markRegExp;
                    let flags = new Set(["g"]);
                    for (const flag of (pattern.flags ?? "").split(" ")) {
                        flags.add(flag);
                    }
                    keyword = new RegExp(
                        pattern.pattern,
                        Array.from(new Set(flags)).join("")
                    );
                } else {
                    keyword = pattern;
                }
                markFunc(keyword, {
                    element: "span",
                    className: "highlight",
                    acrossElements: true,
                    filter: (e) => {
                        if (
                            e.parentNode.dataset &&
                            e.parentNode.dataset.markjs
                        ) {
                            return false;
                        }
                        return true;
                    },
                    each: (e) => {
                        if (classList.length) {
                            e.classList.add(...classList);
                        }
                    },
                });
            }
        }
    }

    _registerInputHandler(editable, terms) {
        editable.addEventListener("input", () => {
            clearTimeout(this.timeoutID);
            this.timeoutID = setTimeout(() => {
                this._highlight(editable, terms);
            }, 100);
        });
    }

    async highlight(terms) {
        if (document.getElementById("fields")) {
            [...document.getElementById("fields").children].forEach((field) => {
                const editable = field.editingArea.editable;
                this._inject(editable);
                this._highlight(editable, terms);
                this._registerInputHandler(editable, terms);
            });
        } else {
            const NoteEditor = require("anki/NoteEditor");
            const svelteStore = require("svelte/store");
            while (!NoteEditor.instances[0]?.fields?.length) {
                await new Promise(requestAnimationFrame);
            }
            NoteEditor.instances[0].fields.forEach(async (field) => {
                const richText = svelteStore.get(
                    field.editingArea.editingInputs
                )[0];
                const editable = await richText.element;
                this._inject(editable);
                this._highlight(editable, terms);
                this._registerInputHandler(editable, terms);
            });
        }
    }
}

globalThis.highlighter = new Highlighter();
