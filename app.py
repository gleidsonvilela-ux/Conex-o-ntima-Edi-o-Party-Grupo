import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import random
import copy
import re
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'conexao_intima_grupo_2026_prod'

socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='eventlet', 
    transports=['websocket', 'polling'],
    ping_timeout=60, 
    ping_interval=25
)

# 👥 BARALHO MASSIVO PARA GRUPOS E MULTI-CASAIS (PRESENCIAL & À DISTÂNCIA)
ORIGINAL_CARDS = {
    "fase1": {
        "verdade": {
            "direcionada": [
                "{mandante}, olhe para {alvo} e confesse: de 0 a 10, quão atraente você achou o visual dele(a) hoje?",
                "{mandante}, diga para a roda: qual é o traço mais marcante ou charmoso do estilo de {alvo}?",
                "{mandante}, responda com sinceridade: se estivessem só vocês dois em uma festa, qual seria a sua abordagem para conversar com {alvo}?",
                "{mandante}, qual figurinha ou emoji você mandaria no privado de {alvo} para puxar assunto de madrugada?",
                "{mandante}, se {alvo} te convidasse para tomar uma saideira hoje após o jogo, você aceitaria de primeira?",
                "{mandante}, olhe nos olhos de {alvo} e diga qual o elogio mais sincero e ousado que você tem para fazer a ele(a) agora.",
                "{mandante}, revele para o grupo: qual é a primeira coisa em que você repara em alguém antes de decidir se investe ou não?"
            ],
            "coletiva": [
                "RODA DA VERDADE: Todo mundo aponta ao mesmo tempo para a pessoa da roda que acha mais perigosa em uma festa! Quem for mais apontado(a) toma 1 shot!",
                "PRIMEIRA IMPRESSÃO: O grupo deve escolher uma pessoa para responder: quem da roda parece ser o mais tímido entre quatro paredes?",
                "TRIBUNAL DO GRUPO: Quem da roda é a pessoa que tem o histórico de conversas mais proibido no celular? O grupo vota e o mais votado revela um detalhe sem dar nomes!",
                "ENQUETE RÁPIDA: Quem da roda tem cara de que já mandou mensagem para o ex depois da terceira dose de bebida? Quem já fez isso, bebe!"
            ]
        },
        "desafio": {
            "direcionada": [
                "{mandante} deve se aproximar de {alvo}, dar um xêro no pescoço e sussurrar uma cantada bem cafona e provocante no ouvido dele(a).",
                "{mandante} e {alvo} devem dar um abraço apertado de 15 segundos na frente de todo mundo enquanto a roda faz pressão!",
                "{mandante} deve escolher {alvo} para fazer um dengo ou carinho no cabelo por 30 segundos seguidos.",
                "{mandante} deve tirar uma foto engraçada ou sexy ao lado de {alvo} e postar nos stories ou enviar no grupo do WhatsApp de vocês!",
                "{mandante} deve servir uma dose/drink para {alvo} e dar o primeiro gole na boca dele(a)!",
                "{mandante} deve morder levemente o lábio inferior olhando fixamente nos olhos de {alvo} até ele(a) sorrir ou desviar o olhar."
            ],
            "coletiva": [
                "DESAFIO DO BRINDO: Todo o grupo deve levantar seus copos, fazer um brinde ao vivo e tomar 2 goles fartos da bebida!",
                "CORRENTE DO ELOGIO: {mandante} deve dar um elogio afiado para a pessoa da sua esquerda, que passa outro elogio para a esquerda até fechar a roda!",
                "MÚSICA DA NOITE: O grupo escolhe uma música animada. Todo mundo deve dançar no lugar até o refrão terminar!"
            ]
        }
    },
    "fase2": {
        "verdade": {
            "direcionada": [
                "{mandante}, responda sem titubear: se você tivesse que escolher alguém nesta roda para passar 10 minutos em um quarto fechado, escolheria {alvo} ou outra pessoa?",
                "{mandante}, olhe para {alvo} e diga: você acha que o beijo dele(a) é mais calmo ou totalmente selvagem?",
                "{mandante}, qual seria a primeira reação de {alvo} se você mandasse uma foto provocante no privado dele(a) agora?",
                "{mandante}, se {alvo} te desafiasse para um beijo de 10 segundos agora na frente de todo mundo, você aceitaria ou pagaria o castigo?",
                "{mandante}, você já teve algum sonho ousado ou pensamento escondido com alguém que está presente neste grupo?",
                "{mandante}, diga para a roda: qual é o tipo de provocação em público que te faz perder o controle mais rápido?"
            ],
            "coletiva": [
                "🥂 EU NUNCA PICANTE: 'Eu nunca fiquei com mais de uma pessoa da mesma roda de amigos!' Quem já fez isso toma 2 doses!",
                "EU NUNCA MÍDIA: 'Eu nunca mandei uma foto/vídeo de visualização única no WhatsApp neste mês!' Quem já mandou dá um gole!",
                "SEGREDO REVELADO: O grupo escolhe uma pessoa para confessar: qual foi a maior loucura que você já fez por impulso em uma noite de festa?",
                "VOTAÇÃO TENSÃO: Quem da roda tem a postura mais dominante na hora da sedução? O grupo vota e a pessoa mais votada escolhe quem bebe com ela!"
            ]
        },
        "desafio": {
            "direcionada": [
                "{mandante} deve sentar no colo de {alvo} por 1 rodada inteira ou pagar o castigo de tomar 2 shots seguidos!",
                "{mandante} e {alvo} devem fazer o **Shot Espelhado**: tomar uma dose juntos, olho no olho, a menos de 5cm de distância de seus rostos!",
                "{mandante} deve passar a ponta das unhas suavemente pelos braços ou pescoço de {alvo} por 30 segundos provocando o grupo.",
                "{mandante} deve sussurrar no ouvido de {alvo} o fetiche mais ousado que consegue imaginar para uma festa em grupo.",
                "{mandante} deve tirar uma peça de roupa (jaqueta, calçado, acessório) e colocar em {alvo}!",
                "{mandante} deve dar 3 beijos estalados em pontos diferentes do rosto/pescoço de {alvo}!"
            ],
            "coletiva": [
                "TROCA DE LUGARES: Todo mundo que estiver vestindo alguma peça preta ou vermelha deve trocar de lugar imediatamente na roda!",
                "MARATONA DO SHOT: As três pessoas mais animadas da mesa devem tomar 1 shot juntos para esquentar o clima da Fase 2!",
                "FOTO OFICIAL DO GRUPO: Tirar uma selfie de todo o grupo fazendo uma pose sensual ou engraçada para guardar a lembrança da noite!"
            ]
        }
    },
    "fase3": {
        "verdade": {
            "direcionada": [
                "{mandante}, olhe nos olhos de {alvo} e diga exatamente o que você faria se a roda votasse para deixar vocês dois sozinhos no quarto por 10 minutos.",
                "{mandante}, se {alvo} estivesse totalmente livre esta noite, quão longe você iria com ele(a)?",
                "{mandante}, qual palavra dita no seu ouvido por {alvo} te deixaria completamente sem defesa?",
                "{mandante}, qual o limite máximo de ousadia que você aceita praticar na frente dos seus amigos em um jogo?"
            ],
            "coletiva": [
                "DUPLA DINÂMICA: O grupo escolhe qual dupla da roda tem a maior química visual. A dupla deve decidir se cumpre um desafio duplo ou se todo o grupo bebe!",
                "ULTIMATO DO GRUPO: Quem da roda é mais provável de terminar a noite em um encontro secreto? O mais votado bebe 2 doses!"
            ]
        },
        "desafio": {
            "direcionada": [
                "{mandante} deve dar um beijo de 10 segundos em {alvo} (na boca, no pescoço ou na bochecha, respeitando o limite do lobby)! 💥",
                "{mandante} deve fazer uma massagem provocante nos ombros e pescoço de {alvo} por 1 minuto enquanto o grupo assiste.",
                "{mandante} e {alvo} devem dançar juntos bem colados durante 30 segundos ao som da escolha da roda!",
                "{mandante} deve tirar uma foto da sua intimidade (por cima da roupa) e mostrar rapidamente apenas para {alvo} no celular!"
            ],
            "coletiva": [
                "CELEBRAÇÃO COLETIVA: Todo mundo da sala deve virar a sua bebida, dar um grito de comemoração e abraçar quem estiver ao lado!",
                "CLÍMAX DO GRUPO: O grupo deve definir uma prenda coletiva para ser paga na próxima festa!"
            ]
        }
    }
}

ORIGINAL_NEVER_CARDS = [
    "Eu nunca fiquei com alguém que conheci no mesmo dia em uma festa.",
    "Eu nunca mandei uma mensagem ousada para a pessoa errada no WhatsApp sem querer.",
    "Eu nunca me envolvi com mais de uma pessoa da mesma roda de amigos em momentos diferentes.",
    "Eu nunca fingi que estava bêbado(a) só para ter coragem de dar em cima de alguém.",
    "Eu nunca fiz um jogo de bebidas que terminou sem roupas na sala."
]

ORIGINAL_PUNISHMENTS = [
    "Tomar 2 shots seguidos da bebida escolhida pelo grupo sem fazer careta! 🥃🥃",
    "Ficar o restante do jogo sem poder usar as mãos para segurar o próprio copo (alguém precisa servir).",
    "Mandar um áudio de 10 segundos no grupo do WhatsApp imitando um gemido engraçado.",
    "Deixar o grupo escolher uma figurinha vergonhosa para enviar na primeira conversa do seu WhatsApp.",
    "Pagar 10 flexões ou agachamentos na frente de todo mundo enquanto o grupo conta!"
]

ACTIVE_ROOMS = {}

def generate_room_id():
    while True:
        room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        if room_id not in ACTIVE_ROOMS:
            return room_id

def get_initial_room_state():
    return {
        "state": {
            "players": {}, 
            "current_player": None,
            "target_player": None,
            "current_cards": {},
            "game_started": False,
            "location_mode": "presencial", # 'presencial' ou 'distancia'
            "game_type": "cards", 
            "scores": {}, # pid: int
            "game_over": False,
            "rounds_played": {"fase1": 0, "fase2": 0, "fase3": 0},
            "creator_name": ""
        },
        "session_cards": copy.deepcopy(ORIGINAL_CARDS),
        "session_never": list(ORIGINAL_NEVER_CARDS),
        "session_punishments": copy.deepcopy(ORIGINAL_PUNISHMENTS)
    }

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_room')
def handle_create_room():
    room_id = generate_room_id()
    ACTIVE_ROOMS[room_id] = get_initial_room_state()
    emit('room_created', {'room_id': room_id})

@socketio.on('check_room_status')
def handle_check_room(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id in ACTIVE_ROOMS:
        emit('room_status_checked', {
            'valid': True,
            'creator_name': ACTIVE_ROOMS[room_id]["state"]["creator_name"]
        })
    else:
        emit('room_status_checked', {'valid': False})

@socketio.on('join_game')
def handle_join(data):
    room_id = data.get('room_id', '').strip().upper()
    player_name = data.get('name', 'Convidado').strip()
    gender = data.get('gender', 'H')
    pref = data.get('pref', 'hetero') # 'hetero' ou 'ambos'
    location_mode = data.get('location_mode', 'presencial')
    
    if room_id not in ACTIVE_ROOMS:
        emit('error', {'msg': 'Código de sala inválido ou encerrado!'})
        return

    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    join_room(room_id)
    
    if len(game_state["players"]) == 0:
        game_state["creator_name"] = player_name
        game_state["location_mode"] = location_mode

    # Registra ou reconecta o jogador na sala de grupo
    game_state["players"][request.sid] = {
        "name": player_name, 
        "gender": gender, 
        "pref": pref,
        "ready": False
    }
    if request.sid not in game_state["scores"]:
        game_state["scores"][request.sid] = 0

    update_all_clients(room_id)

@socketio.on('player_ready')
def handle_ready(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    if request.sid in game_state["players"]:
        game_state["players"][request.sid]["ready"] = True
        p_ids = list(game_state["players"].keys())
        
        # Inicia quando pelo menos 3 participantes marcarem pronto (ou no mínimo 2)
        if len(p_ids) >= 2 and all(game_state["players"][uid]["ready"] for uid in p_ids):
            game_state["game_started"] = True
            game_state["game_over"] = False
            room["session_cards"] = copy.deepcopy(ORIGINAL_CARDS)
            
            sortear_proximo_turno(room_id)

@socketio.on('draw_card')
def handle_draw(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    if not game_state["game_started"] or game_state["game_over"]: return
    if request.sid != game_state["current_player"]: return

    fase = data.get('fase', 'fase1')
    tipo = data.get('type', 'desafio')
    
    mandante_nome = game_state["players"][game_state["current_player"]]["name"]
    alvo_nome = game_state["players"][game_state["target_player"]]["name"] if game_state["target_player"] else "GRUPO"

    session_cards = room["session_cards"]
    
    # Sorteia se a carta é direcionada entre 2 pessoas ou coletiva
    is_coletiva = (game_state["target_player"] is None) or (random.random() < 0.25)
    categoria_key = "coletiva" if is_coletiva else "direcionada"
    
    if fase in session_cards and tipo in session_cards[fase]:
        pool = session_cards[fase][tipo][categoria_key]
        if not pool:
            session_cards[fase][tipo][categoria_key] = copy.deepcopy(ORIGINAL_CARDS[fase][tipo][categoria_key])
            pool = session_cards[fase][tipo][categoria_key]
            
        text = pool.pop(random.randint(0, len(pool) - 1))
        text_formatado = text.replace("{mandante}", mandante_nome).replace("{alvo}", alvo_nome)
        
        pontos = {"fase1": 1, "fase2": 2, "fase3": 4}[fase]
        labels = {"fase1": "AQUECIMENTO DE GRUPO", "fase2": "TENSÃO & FESTA", "fase3": "SEM LIMITES"}
        
        game_state["current_cards"] = {
            "fase_key": f"cards_{fase}_{tipo}",
            "real_fase": fase,
            "type": f"👥 {labels[fase]} - {tipo.upper()}", 
            "text": text_formatado,
            "points": pontos
        }
        update_all_clients(room_id)

@socketio.on('trigger_punishment')
def handle_punishment(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    if not room["session_punishments"]: room["session_punishments"] = copy.deepcopy(ORIGINAL_PUNISHMENTS)
    mandante_nome = game_state["players"][request.sid]["name"]

    punish_text = room["session_punishments"].pop(random.randint(0, len(room["session_punishments"]) - 1))
    
    game_state["current_cards"] = {
        "fase_key": "punishment",
        "real_fase": "fase1",
        "type": "🛑 CASTIGO DE GRUPO",
        "text": f"{mandante_nome} pulou a rodada!\n\nCumpra o seguinte castigo perante o grupo:\n\n{punish_text}",
        "points": 0
    }
    update_all_clients(room_id)

@socketio.on('next_turn')
def handle_next_turn(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    executed = data.get('executed', False)
    if executed and request.sid in game_state["scores"]:
        game_state["scores"][request.sid] += game_state["current_cards"].get('points', 0)
        fase_atual = game_state["current_cards"].get('real_fase', 'fase1')
        game_state["rounds_played"][fase_atual] += 1
        
    game_state["current_cards"] = {}
    sortear_proximo_turno(room_id)

def sortear_proximo_turno(room_id):
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    players = game_state["players"]
    p_ids = list(players.keys())
    
    if len(p_ids) < 2: return
    
    # 1. Sorteia o Mandante da Rodada
    mandante_id = random.choice(p_ids)
    mandante = players[mandante_id]
    
    # 2. Algoritmo de Compatibilidade de Gênero / Orientação
    candidatos_compativeis = []
    for pid in p_ids:
        if pid == mandante_id: continue
        p = players[pid]
        
        # Valida restrições do Mandante e do Alvo
        cand_ok_para_mandante = (mandante["pref"] == "ambos") or (p["gender"] != mandante["gender"])
        mandante_ok_para_cand = (p["pref"] == "ambos") or (mandante["gender"] != p["gender"])
        
        if cand_ok_para_mandante and mandante_ok_para_cand:
            candidatos_compativeis.append(pid)
            
    # Se houver par compatível, sorteia o Alvo; se não, a rodada vira Ação Coletiva do Grupo
    alvo_id = random.choice(candidatos_compativeis) if candidatos_compativeis else None
    
    game_state["current_player"] = mandante_id
    game_state["target_player"] = alvo_id
    
    socketio.emit('start_roulette_animation', {
        'winner_name': players[mandante_id]["name"],
        'target_name': players[alvo_id]["name"] if alvo_id else "TODOS DO GRUPO"
    }, to=room_id)
    
    update_all_clients(room_id)

@socketio.on('end_game')
def handle_end_game(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    game_state["game_over"] = True
    scores = game_state["scores"]
    players = game_state["players"]
    
    # Ordena o placar da festa
    ranking = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    top_text = "🏆 CAMPEÕES DA NOITE DE GRUPO:\n\n"
    for idx, (pid, pts) in enumerate(ranking):
        pname = players[pid]["name"] if pid in players else "Convidado"
        top_text += f"{idx+1}º Lugar: {pname} — {pts} pts\n"
        
    socketio.emit('game_update', {
        'card': {
            "fase_key": "game_over",
            "type": "🏁 FIM DA RESENHA DE GRUPO",
            "text": top_text + "\nChegou a hora de pagar as últimas apostas da noite!",
            "points": 0
        },
        'game_started': True,
        'game_over': True,
        'score_board': "Jogo Concluído!"
    }, to=room_id)
    
    ACTIVE_ROOMS.pop(room_id, None)

def update_all_clients(room_id):
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    p_ids = list(game_state["players"].keys())
    
    # Monta a string do placar geral de todos os participantes
    score_parts = []
    for pid in p_ids:
        pname = game_state["players"][pid]["name"]
        pts = game_state["scores"].get(pid, 0)
        score_parts.append(f"{pname}: {pts}p")
    score_text = " 📊 " + " | ".join(score_parts)
    
    current_name = game_state["players"][game_state["current_player"]]["name"] if game_state["current_player"] in game_state["players"] else "..."
    target_name = game_state["players"][game_state["target_player"]]["name"] if (game_state["target_player"] and game_state["target_player"] in game_state["players"]) else "TODOS DO GRUPO"

    players_status = []
    for pid in p_ids:
        p = game_state["players"][pid]
        p_pref = "Hétero" if p["pref"] == "hetero" else "Livre/Ambos"
        r_label = "Pronto ✓" if p["ready"] else "Aguardando..."
        players_status.append(f"{p['name']} ({p['gender']} - {p_pref}): {r_label}")

    for uid in p_ids:
        socketio.emit('game_update', {
            'is_my_turn': (uid == game_state["current_player"]),
            'room_id': room_id,
            'current_player_name': current_name,
            'target_player_name': target_name,
            'card': game_state["current_cards"],
            'game_started': game_state["game_started"],
            'game_over': game_state["game_over"],
            'score_board': score_text,
            'rounds_played': game_state["rounds_played"],
            'players_status': players_status,
            'am_i_ready': game_state["players"][uid]["ready"],
            'location_mode': game_state["location_mode"]
        }, room=uid)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
