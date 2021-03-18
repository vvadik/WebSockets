const chars = [...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'];
const id = [...Array(8)].map(i => chars[0 | Math.random() * chars.length]).join('');
const msg_re = /@(\w+):\s+(.*)/;

window.onload = () => {
    const [msg_text, send_btn, messages] = [
        'message', 'send', 'messages'
    ].map(x => document.getElementById(x));

    const ws = new WebSocket(`ws://${window.location.host}/chat`);
    let ping = void null;

    ws.onopen = () => {
        console.log('connection open');
        ws.send(JSON.stringify({'mtype': 'INIT', id}));
        send_btn.disabled = false;

        messages.value = `Hello, ${id}!\n`;
        ping = setInterval(() => void ws.send("ping"), 5000);
    }

    ws.onclose = () => {
        console.log('connection closed');
        send_btn.disabled = true;
        clearInterval(ping);
    }


    ws.onmessage = evt => {
        if (evt.data === 'pong') return;

        let {id, mtype, text} = JSON.parse(evt.data);
        switch (mtype) {
            case 'MSG':
                messages.value += `[${id}]: ${text}\n`;
                break;

            case 'DM':
                messages.value += `[DM || ${id}]: ${text}\n`;
                break;

            case 'USER_ENTER':
                messages.value += `User ${id} entered the chat\n`;
                break;

            case 'USER_LEAVE':
                messages.value += `User ${id} leaved the chat\n`;
                break;
        }
    }

    send_btn.onclick = () => {
        let text = msg_text.value;
        let to = null;

        if (msg_re.test(text)) {
            [to, text] = msg_re.exec(text).slice(1);
        }
        ws.send(JSON.stringify({'mtype': 'TEXT', id, to, text}));

        messages.value += `me: ${text}\n`;
        msg_text.value = '';
        msg_text.focus();
    }
}