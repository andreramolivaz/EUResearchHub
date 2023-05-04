// in questo modo mi connetto al server
var socketio = io()

const message = $('#messages')

const createMessage = (name, msg) => {
    const content = `
        <div>
            <span>
                <strong>${name}</strong>: ${msg}
            </span>
        </div>
    `
    message.append(content)
}

// ascoltiamo l'evento message
socketio.on('message', (data) => {
    createMessage(data.name, data.message)
})

const sendMessage = () => {
    console.log('msg')
}