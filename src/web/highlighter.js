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

    _highlight(element, patterns) {
        const instance = new Mark(element);
        for (const pattern of patterns) {
            instance.markRegExp(new RegExp(pattern, "g"), {
                element: "span",
                className: "highlight",
                acrossElements: true,
                filter: (e) => {
                    if (e.parentNode.dataset && e.parentNode.dataset.markjs) {
                        return false;
                    }
                    return true;
                },
            });
        }
    }

    _registerInputHandler(editable, patterns) {
        editable.addEventListener("input", () => {
            clearTimeout(this.timeoutID);
            this.timeoutID = setTimeout(() => {
                this._highlight(editable, patterns);
            }, 100);
        });
    }

    async highlight(patterns) {
        if (document.getElementById("fields")) {
            [...document.getElementById("fields").children].forEach((field) => {
                const editable = field.editingArea.editable;
                this._inject(editable);
                this._highlight(editable, patterns);
                this._registerInputHandler(editable, patterns);
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
                this._highlight(editable, patterns);
                this._registerInputHandler(editable, patterns);
            });
        }
    }
}

globalThis.highlighter = new Highlighter();
