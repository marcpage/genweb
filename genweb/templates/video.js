function playPauseVideo(identifier) {
    var myVideo = document.getElementById(identifier);
    if (myVideo.paused)
        myVideo.play();
    else
        myVideo.pause();
}

function setWidth(identifier, size) {
    var myVideo = document.getElementById(identifier);
    myVideo.width = size;
}
