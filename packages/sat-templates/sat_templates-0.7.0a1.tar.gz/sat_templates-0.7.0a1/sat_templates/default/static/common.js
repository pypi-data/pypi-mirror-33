var __session_storage_available;
var __local_storage_available;

function storageAvailable(type) {
    /* check if session or local storage is available
     *
     * @param type(string): "session" or "storage"
     * @return (boolean): true if requested storage is available
     */
    console.assert(type == 'session' || type == 'storage', "bad storage type (%s)", type);
    const var_name = '__' + type + '_storage_available';
    var available = window[var_name];
    if (available === undefined) {
        // test method from https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API
        var storage = window[type + 'Storage'];
        try {
            x = '__storage_test__';
            storage.setItem(x, x);
            storage.removeItem(x);
            available = true;
        }
        catch(e) {
            available = e instanceof DOMException && (
                    // everything except Firefox
                    e.code === 22 ||
                    // Firefox
                    e.code === 1014 ||
                    // test name field too, because code might not be present
                    // everything except Firefox
                    e.name === 'QuotaExceededError' ||
                    // Firefox
                    e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
                // acknowledge QuotaExceededError only if there's something already stored
                storage.length !== 0;
        }

        if (!available) {
            console.warn("%s storage not available", type);
        }
        window[var_name] = available;
    }

    return available;
}

function toggle_clicked_class_tag(tag_name, class_name='clicked') {
    for (let elt of document.getElementsByTagName(tag_name)) {
        elt.classList.toggle(class_name);
    }
}

function toggle_clicked_class_sel(selectors, class_name='clicked') {
    for (let elt of document.querySelectorAll(selectors)) {
        elt.classList.toggle(class_name);
    }
}

function set_clicked_class_id(trigger_elem_id, target_elem_id=null, class_name='clicked') {
    if (target_elem_id === null) { target_elem_id = trigger_elem_id; }
    document.getElementById(trigger_elem_id).addEventListener(
        "click",
        function() {
            document.getElementById(target_elem_id).classList.toggle(class_name);
        }
    );
}

function get_elt(arg) {
    if (typeof arg === 'string') {
        // we should have an id
        return document.getElementById(arg);
    }
    else {
        // we should have an element
        return arg;
    }
}

function clicked_cls(elt) {
    /* toggle "clicked" class on each click, and remove "init" class if present */
    // init
    if (elt.classList.contains("init")) {
        elt.classList.remove("init");
    }

    // clicked
    elt.classList.toggle("clicked");
}

function clicked_mh_fix(arg) {
    /* toggle clicked, and fix max-height on transitionend
     *
     * needed to workaround transition issue with max-height:none
     * inspired from https://css-tricks.com/using-css-transitions-auto-dimensions,
     * thanks to Brandon Smith
     *
     * @param arg: element to toggle (id as string, or element itself)
     * */
    elt = get_elt(arg);

    if (!elt.classList.contains("clicked")) {
        /* expand */
        var fix_expand = function(event) {
            elt.removeEventListener("transitionend", fix_expand, false);
            if (elt.classList.contains("clicked")) {
                /* if event is clicked quicker than transition time,
                 * this callback can be called on reduce */
                elt.style.maxHeight = "none";
            }
        };

        elt.setAttribute('max_height_init', elt.clientHeight);
        elt.addEventListener("transitionend", fix_expand, false);
        clicked_cls(elt);
        elt.style.maxHeight = elt.scrollHeight + 'px';
    }
    else {
        /* reduce */
        var transition_save = elt.style.transition;
        elt.style.transition = '';
        requestAnimationFrame(function() {
            elt.style.maxHeight = elt.scrollHeight + 'px';
            elt.style.transition = transition_save;

            requestAnimationFrame(function() {
                elt.style.maxHeight = elt.getAttribute('max_height_init') + 'px';
                elt.removeAttribute('max_height_init');
                elt.style.maxHeight = null;
            });
        });

        clicked_cls(elt);
    }
}
