from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random # usato solamente per generare un numero casuale per la stanza, non ne avremo bisogno all'interno del progetto
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple_secret_key' # imposto la chiave segreta, in produzione deve essere molto più complessa
socketio = SocketIO(app)

# dizionario che conterrà tutte le stanze, la chiave sarà il codice della stanza e il valore sarà un dizionario con i dati della stanza
rooms = {} 

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break

    return code

@app.route('/', methods=['GET', 'POST'])
def home():
    session.clear()
    if request.method == 'POST':
        # in python il form è visto come un dizionario
        # se il campo che cerco non esiste imposto la variabile a False
        name = request.form.get('name') # ottengo il nome dal form
        code = request.form.get('code') # ottengo il codice dal form
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        # se non  è stato inserito il nome, messaggio di errore
        if not name:
            # passiamo anche code e name perche qundo invio una POST request è come se stessi aggirnando la pagina
            return render_template('home.html', error='Devi inserire un nome', code = code, name = name)
        
        # tento di entrare senza aver inserito un codice
        if join != False and not code:
            # passiamo anche code e name perche qundo invio una POST request è come se stessi aggirnando la pagina
            return render_template('home.html', error='Devi inserire un codice', code = code, name = name)
        
        room = code
        # ho premuto il tasto per creare una stanza
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []} # per creare la stanza la aggiungo al dizionario delle stanze
        elif code not in rooms:
            return render_template('home.html', error='La stanza non esiste', code = code, name = name)

        # salvo i dati in una sessione per evitare non implementare tutta la logica di login
        session['room'] = room
        session['name'] = name

        return redirect(url_for('room'))

    return render_template('home.html')


@app.route('/room')
def room():
    room = session.get('room')
    # posso accedere alla stanza solo dalla home
    if room is None or session.get('name') is None or room not in rooms:
        return redirect(url_for('home'))


    return render_template('room.html')

@socketio.on('connect')
def connect(auth):
    room = session.get('room')
    name = session.get('name')

    # esco se provo a collegarmi al socket senza aver prima inserito i dati
    if not room or not name:
        return
    # se la stanza non è presente all'intero del dizionario, esco
    if room not in rooms:
        leave_room(room)
        return
    
    # mi collego alla stanza
    join_room(room)
    # invio un messaggio
    send({"name": name,"message": "è entrato nella stanza"},to = room)

    # aggiorno il numero di membri nella stanza
    rooms[room]["members"] += 1
    print(f"{name} è entrato nella stanza {room}") # debugging purpose

@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    name = session.get('name')
    leave_room(room)

    # ogni volta che una persona esce dalla stanza aggiorno il numero nel dizionario
    if room in rooms:
        rooms[room]['members'] -= 1
        if rooms[room]['members'] <= 0:
            del rooms[room]
    
    send({"name": name,"message": "è uscito dalla stanza"},to = room)
    print(f"{name} è uscito dalla stanza {room}") # debugging purpose

if __name__ == '__main__':
    socketio.run(app, debug=True)