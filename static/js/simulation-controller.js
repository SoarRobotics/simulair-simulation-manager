$(document).ready(function(){
    var socket = io.connect('http://' + document.domain + ':' + location.port); //setup namespace
    socket.on("connection-accepted", function(msg){
      console.log(msg);
      if(msg.connected){
        $("#notification").text("Socket.io have successfully connected on " + document.domain + ":" + location.port);
      }
    });
});
