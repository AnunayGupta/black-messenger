document.addEventListener('DOMContentLoaded',() =>{
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
  socket.on('connect', () => {

        // Notify the server user has joined
        socket.emit('joined');

        // Forget user's last channel when clicked on '+ Channel'
        document.querySelector('#newChannel').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });
        document.querySelector('#leave').addEventListener('click', () => {

            // Notify the server user has left
            socket.emit('left');

            localStorage.removeItem('last_channel');
            window.location.replace('/');
        });
        document.querySelector('#logout').addEventListener('click', () => {
           localStorage.removeItem('last_channel');
        });
        document.querySelector('#comment').addEventListener("keydown", event => {
            if (event.key == "Enter") {
                document.getElementById("send-button").click();
            }
        });
        document.querySelector('#send-button').addEventListener("click", () => {

    // Save time in format HH:MM:SS
        let timestamp = new Date;
        timestamp = timestamp.toLocaleTimeString();

    // Save user input
        let msg = document.getElementById("comment").value;

        socket.emit('send message', msg, timestamp);

    // Clear input
        document.getElementById("comment").value = '';
    });
  });
  socket.on('status', data => {

    // Broadcast message of joined user.
    let row = '<' + `${data.msg}` + '>'
    document.querySelector('#chat').value += row + '\n';

    // Save user current channel on localStorage
    localStorage.setItem('last_channel', data.channel)
    })

// When a message is announced, add it to the textarea.
    socket.on('announce message', data => {

    // Format message
    let row = '<' + `${data.timestamp}` + '> - ' + '[' + `${data.user}` + ']:  ' + `${data.msg}`
    document.querySelector('#chat').value += row + '\n'
  })

});
