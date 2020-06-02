document.addEventListener("DOMContentLoaded", () => {
    var socket = io.connect(location.protocol + "//" + document.domain + ':' + location.port);

    //Channels preview
    let channels_previews = document.querySelectorAll(".channel");
    for (let i = 0; i < channels_previews.length; i++) {
        channels_previews[i].addEventListener('click', () => {

            document.querySelector(".message_view").style.lineHeight = "normal";
            channels_previews[i].classList.add('active');


            for (let j = 0; j < channels_previews.length; j++) {
                if (i !== j) {
                    channels_previews[j].classList.remove('active');
                }
            }
            socket.emit('show_messages', {"channel_id":
                    channels_previews[i].getAttribute('channel_id')});
        });
    }


    //Add event to "send" button
    socket.on('connect', () => {
        let button = document.querySelector('#send');
        button.onclick = () => {

            const content = document.querySelector('#content').value;
            let chat_id = document.querySelector('.active').getAttribute('channel_id');
            socket.emit('send_message', {"content": content, "chat_id": chat_id});
            document.querySelector("#content").value = "";

        };
    });

    //Show sent message
    socket.on('send_message', data => {
        let div = document.createElement('div');
        div.classList.add("message");
        let cookie_name =  document.cookie.split('=')[1];
        if (cookie_name == data.remember_token) {
                div.classList.add("active_user");
            }
        div.innerHTML = `
                    <span class="message_content">${data.content}</span>
                    <span class="message_meta">
                        <span class="message_name">${data.name}</span>
                        <span class="message_time">${data.time}</span>
                    </span>
            `;
        document.querySelector('#messages').append(div);
    });


    //Show all messages
    socket.on('chat_messages', data => {
        let el = document.querySelector('#messages');
        el.innerHTML = '';
        data['messages'].forEach(item => {
            let div = document.createElement('div');
            if (item.message_username === data.name) {
                div.classList.add("active_user");
            }
            div.classList.add("message" );
            div.innerHTML = `
                    <span class="message_content">${item.content}</span>
                    <span class="message_meta">
                        <span class="message_name">${item.message_username}</span>
                        <span class="message_time">${item.time}</span>
                    </span>
            `;
            el.append(div);
        });
    });

});