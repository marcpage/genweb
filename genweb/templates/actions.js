const closed = "▸";
const open = "▾";

function show_hide(identifier) {
    var div = document.getElementById(identifier);
    var button = document.getElementById(identifier+"-button");

    if (button.innerText == closed) {
        button.innerText = open;
        div.style.display = "block";
    } else {
        button.innerText = closed;
        div.style.display = "none";
    }
}
