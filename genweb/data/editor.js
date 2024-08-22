// MARK: Globals
const MAXIMUM_TYPE_AHEAD = 50;
var server_state = {people:undefined, metadata:undefined};
const input_types = ['input', 'select', 'textarea'];
const values_to_clear = [
    "title",
    "path",
    "file",
    "mod_date",
    "people",
    "caption",
    "folder",
    "height",
    "width",
    "contents",
    "references",
    "original"
];
const visible_fields = {
    id:["inline","href", "picture"],
    title:["inline", "href", "picture"],
    path:["inline", "href", "picture"],
    file:["inline", "href", "picture"],
    people:["inline", "href", "picture"],
    mod_date:["inline", "picture", "href"],
    folder:["href"],
    original:["picture"],
    height:["picture"],
    caption:["picture"],
    width:["picture"],
    contents:["inline"],
    references:["inline"],
};

// MARK: Helpers

function type_change(selector_id) {
    var selector = document.getElementById(selector_id);
    
    for (const field in visible_fields) {
        var field_row = document.getElementById(field);

        if (visible_fields[field].includes(selector.value)) {
            field_row.style.display = "table-row";
        } else {
            field_row.style.display = "none";
        }
    }
}

function reset_select(field, values) {
    var select = document.getElementById(field);
    
    while (select.options.length > 0) {
        select.remove(select.options.length - 1);
    }

    for (var i = 0; i < values.length; ++i) {
        var option = document.createElement("option");
        option.value = values[i];
        option.innerHTML = values[i];
        select.appendChild(option);
    }
}

function report_if_errors(request) {
    if (request.readyState == 4 && request.status != 200) {
        var errors = document.getElementById("errors");
        var error_area = document.getElementById("error_area");
        const nowUTC = new Date();
        const now_str = nowUTC.toLocaleString("en-US", {timezone: Intl.DateTimeFormat().resolvedOptions().timeZone})
            
        errors.value = now_str + "\n" + request.responseText + "\n\n" + errors.value;
        error_area.style.display = "block";
    }
}
// MARK: Loading initial state

function load_into(url, field) {
    var request = new XMLHttpRequest();

    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            server_state[field] = JSON.parse(request.responseText);
        }

        report_if_errors(this);
    }

    request.open("GET", url, true);
    request.send();
}

function load_values() {
    load_into("/api/v1/people", "people");
    load_into("/api/v1/metadata", "metadata");
}

// MARK: Type ahead

function words_match(words, value) {
    const word_list = words.split(" ").map((x) => x.toLowerCase());;
    const lower_value = value.toLowerCase();
    const matches = word_list.filter((word) => lower_value.includes(word));

    return matches.length == word_list.length;
}

function type_ahead(input_id, field, autoshow) {
    if (server_state[field]) {
        var input = document.getElementById(input_id);
        var options = document.getElementById(input_id+"-options");
        const matches = server_state[field].filter(function (i) {
            return words_match(input.value, i);
        }).slice(0,MAXIMUM_TYPE_AHEAD);

        reset_select(input_id+"-options", [""].concat(matches));

        if (autoshow) {
            options.style.display = matches ? "" : "none";
        }

        options.size = matches.length + 1;
    }
}

function blur_type_ahead(input_id, field, clearOnMismatch) {
    var input = document.getElementById(input_id);
    var options = document.getElementById(input_id+"-options");

    if (clearOnMismatch && !server_state[field].includes(input.value)) {
        setTimeout(() => { 
            options.style.display="none";
            input.value = "";
    }, 400);
}
}

function set_focus(input_id) {
    var input = document.getElementById(input_id);

    input.focus();
}

function select_type_ahead(input_id) {
    var input = document.getElementById(input_id);
    var options = document.getElementById(input_id+"-options");

    input.value = options.value;
    options.style.display = "none";
}

function get_row_input(row_id) {
    var row = document.getElementById(row_id);
    var row_input = [];

    for (var i = 0; i < input_types.length; ++i) {
        row_input = row.getElementsByTagName(input_types[i]);

        if (row_input.length > 0) {
            break;
        }
    }

    return row_input;
}

// MARK: Loading metdata

function clear_form() {
    for (var i = 0; i < values_to_clear.length; ++i) {
        var row_input = get_row_input(values_to_clear[i]);

        row_input[0].value = "";
    }
}

function load_metadata_into(metadata_identifier) {
    var request = new XMLHttpRequest();
    
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var metadata_info = JSON.parse(request.responseText);

            clear_form();

            for(var field in metadata_info) {
                var row_input = get_row_input(field);
                const field_has_row = (row_input.length > 0);

                if ( field_has_row && (field == 'people' || field == 'references')) {
                    row_input[0].value = metadata_info[field].join("\n");
                } else if ( field_has_row && field != 'id') {
                        row_input[0].value = metadata_info[field];
                } else if ( field != 'id') {
                    console.log("Unknown field: " + field + " = " + metadata_info[field]);
                }
            }

            type_change('type-selector');
        }

        report_if_errors(this);
    }

    request.open("GET", "/api/v1/metadata/" + metadata_identifier, true);
    request.send();
}

function update_submit_name() {
    var id_row = document.getElementById("id");
    var id_input = id_row.getElementsByTagName("input");
    var submit_row = document.getElementById("submit");
    var submit = submit_row.getElementsByTagName("input");

    if (server_state.metadata.includes(id_input[0].value)) {
        submit[0].value = "Update";
        load_metadata_into(id_input[0].value);
    } else {
        submit[0].value = "Add";
    }
}

function toggle_display(element_id, phase1, phase2) {
    var element = document.getElementById(element_id);

    if (element.style.display != phase1) {
        element.style.display = phase1;
    } else {
        element.style.display = phase2;
    }
}

// MARK: Loading a person

function load_person_into(person_identifier, person, parents, spouses, children) {
    var request = new XMLHttpRequest();
    
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var person_info = JSON.parse(request.responseText);
            var area = document.createElement("li");

            area.innerHTML = "<b>" + person_info.id + "</b><br/>" 
                            + "(" + person_info.gender + ") " + person_info.surname + "," + person_info.given + "<br/>"
                            + person_info.birthdate + " - " + person_info.deathdate
            person.appendChild(area);

            if (parents) {
                for (var i = 0; i < person_info.parents.length; ++i) {
                    load_person_into(person_info.parents[i], parents, undefined, undefined, undefined);
                }
            }

            if (spouses) {
                for (var i = 0; i < person_info.spouses.length; ++i) {
                    load_person_into(person_info.spouses[i], spouses, undefined, undefined, undefined);
                }
            }

            if (children) {
                for (var i = 0; i < person_info.children.length; ++i) {
                    load_person_into(person_info.children[i], children, undefined, undefined, undefined);
                }
            }
        }

        report_if_errors(this);
    }

    request.open("GET", "/api/v1/people/" + person_identifier, true);
    request.send();
}

function load_person(person_element_id) {
    var element = document.getElementById(person_element_id);
    var person = document.getElementById('person_lookup');
    var parents = document.getElementById('parents_lookup');
    var spouses = document.getElementById('spouses_lookup');
    var children = document.getElementById('children_lookup');
    
    person.innerHTML = "";
    parents.innerHTML = "";
    spouses.innerHTML = "";
    children.innerHTML = "";

    if (!server_state.people.includes(element.value)) {
        return;  // person not found
    }

    load_person_into(element.value, person, parents, spouses, children);
}

// MARK: Save Metadata

function get_form_json() {
    var type_input = get_row_input("type");
    var results = {type: type_input[0].value};

    for (var field in visible_fields) {
        var value = get_row_input(field);

        results[field] = value[0].value;
    }

    return results;
}

function save_form(button_id) {
    var request = new XMLHttpRequest();
    var form_info = get_form_json();
    var submit_button = document.getElementById(button_id);

    submit_button.disabled = true;

    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            if (!server_state.metadata.includes(form_info.id)) {
                server_state.metadata.push(form_info.id);
            }
        }

        report_if_errors(this);
        
        if (this.readyState == 4) {
            submit_button.disabled = false;
        }
    }

    request.open("POST", "/api/v1/metadata/" + form_info.id, true);
    request.setRequestHeader("Content-Type", "text/json;charset=UTF-8");
    request.send(JSON.stringify(form_info));
}
