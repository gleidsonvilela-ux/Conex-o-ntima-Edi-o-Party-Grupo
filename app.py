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

# 👥 BARALHO MASSIVO, EXPLÍCITO E COM FETICHES - PARTY & GRUPO
ORIGINAL_CARDS = {
    "fase1": {
        "verdade": {
            "H_M": [
                "{mandante}, olhe para {alvo} e confesse: de 0 a 10, quão gostosa ela está hoje e o que ela precisaria fazer para chegar ao 10?",
                "{mandante}, se você pudesse mandar {alvo} tirar uma peça de roupa por foto ou ao vivo agora, qual peça você escolheria?",
                "{mandante}, qual foi a primeira coisa que passou pela sua cabeça quando viu o decote, lingerie ou visual de {alvo} nesta sala?",
                "{mandante}, confesse para o grupo: você prefere ver {alvo} de lingerie rendada com salto alto ou totalmente sem nada por baixo?",
                "{mandante}, qual o fetiche visual em {alvo} que mais te chama atenção: o salto alto, a lingerie ou a forma como ela olha?",
                "{mandante}, se você pudesse ver {alvo} caminhando de salto alto devagar na sua direção agora, qual seria a sua reação?",
                "{mandante}, qual detalhe no corpo ou no perfume de {alvo} te deu um arrepio imediato quando você chegou?",
                "{mandante}, se {alvo} pedisse para você segurar a cintura dela com firmeza agora, você saberia exatamente como fazer?"
            ],
            "M_H": [
                "{mandante}, diga para {alvo}: qual é o detalhe no corpo ou no estilo dele que mais te dá pensamentos impróprios?",
                "{mandante}, se você e {alvo} ficassem sozinhos em um quarto por 10 minutos hoje, qual seria sua primeira atitude?",
                "{mandante}, qual o tom de voz grave ou frase de {alvo} que mais consegue te deixar molhada no meio de uma festa?",
                "{mandante}, olhe para {alvo} e confesse: você aceitaria um beijo de língua dele agora na frente do grupo?",
                "{mandante}, você prefere quando {alvo} tem uma pegada mais firme e dominadora na cintura ou quando ele é mais provocante e lento?",
                "{mandante}, qual fetiche em relação aos homens da mesa você mais tem curiosidade de realizar em um jogo?",
                "{mandante}, se {alvo} te pegasse pelo pescoço com cuidado e sussurrasse algo no seu ouvido agora, você arrepiaria?"
            ],
            "M_M": [
                "{mandante}, olhe bem para {alvo} e confesse: você já teve curiosidade de saber como é a pegada ou o beijo de uma mulher?",
                "{mandante}, qual é o detalhe no corpo ou na lingerie de {alvo} que você acha mais atraente e sensual?",
                "{mandante}, se a roda desafiasse você e {alvo} para um beijo triplo ou selinho demorado, você toparia sem pensar?",
                "{mandante}, qual fetiche feminino (lingeries, saltos, carícias) você mais gosta de exibir para ver a reação das pessoas?"
            ],
            "H_H": [
                "{mandante}, diga para {alvo}: quem da roda tem mais cara de que vai dar PT ou dar em cima de todo mundo hoje?",
                "{mandante}, confesse para o grupo: qual foi a maior vergonha que você já viu {alvo} passar por causa de bebida?"
            ],
            "COLETIVA": [
                "RODA DA VERDADE: Todo mundo aponta ao mesmo tempo para a pessoa da roda que acha mais safada! Quem for mais apontado(a) toma 1 shot!",
                "TRIBUNAL DO GRUPO: Quem da roda tem o histórico de conversas mais proibido no WhatsApp? O mais votado paga 1 dose!",
                "FETICHE COLETIVO: Cada pessoa da roda deve confessar qual acessório (salto, lingerie, venda, algemas, óleo) mais te desperta tesão!"
            ]
        },
        "desafio": {
            "H_M": [
                "{mandante} deve se aproximar de {alvo}, puxar ela suavemente pela cintura com pegada firme e dar um xêro bem demorado no pescoço dela.",
                "{mandante} deve sentar do lado de {alvo} e fazer uma massagem sensual nas coxas ou ombros dela por 30 segundos com o grupo assistindo.",
                "{mandante} deve olhar fixamente nos olhos de {alvo} sem piscar por 30 segundos enquanto passa os dedos pelo cabelo ou pescoço dela.",
                "{mandante} deve se ajoelhar na frente de {alvo}, segurar a perna dela e dar um beijo provocante na coxa ou na curva do tornozelo do salto!",
                "{mandante} deve olhar para {alvo} com olhar dominante e sussurrar no ouvido dela: 'Você é minha por essa rodada'."
            ],
            "M_H": [
                "{mandante} deve sentar no colo de {alvo} de salto alto por 1 rodada inteira ou pagar o castigo de tomar 2 shots de bebida!",
                "{mandante} deve passar a ponta dos dedos pelo peitoral/pescoço de {alvo} e sussurrar o seu fetiche mais secreto no ouvido dele.",
                "{mandante} deve dar um tiro de bebida/shot no peito ou pescoço de {alvo}!",
                "{mandante} deve tirar o salto alto ou sapato devagar na frente de {alvo} e usar a ponta do pé descalço para acariciar a perna dele."
            ],
            "M_M": [
                "{mandante} e {alvo} devem dar um beijo de língua de 5 segundos ao vivo na frente da roda! 💋🔥",
                "{mandante} deve dar um xêro no pescoço de {alvo} e dar um tapa provocante na bunda dela!",
                "{mandante} e {alvo} devem dançar bem coladas durante 30 segundos ao som da escolha do grupo!"
            ],
            "H_H": [
                "{mandante} e {alvo} devem fazer um **Shot Espelhado**: tomar uma dose olhando olho no olho a 5cm de distância sem rir!",
                "{mandante} deve pagar 1 shot para {alvo} ou virar uma dose sozinho de uma vez!"
            ],
            "COLETIVA": [
                "BRINDE DA FESTA: Todo o grupo levanta os copos, faz um brinde ao vivo e toma 2 goles caprichados!",
                "MARATONA DO SHOT: As três pessoas mais animadas da mesa devem virar 1 shot juntas agora!"
            ]
        }
    },
    "fase2": {
        "verdade": {
            "H_M": [
                "{mandante}, olhe nos olhos de {alvo} e responda: se a gente apagasse as luzes agora, onde a sua mão iria primeiro no corpo dela?",
                "{mandante}, qual o fetiche mais louco que você gostaria de realizar com {alvo} depois que o jogo acabar?",
                "{mandante}, qual tipo de lingerie em {alvo} te deixaria completamente sem controle na cama: renda preta, fio-dental ou cetim?",
                "{mandante}, você prefere dominar {alvo} pela voz e pela pegada ou deixar que ela tome o controle total da situação?",
                "{mandante}, confesse: qual a cena mais safada em que você imaginou {alvo} usando esse salto alto ou essa roupa hoje?",
                "{mandante}, se {alvo} pedisse para você fechar os olhos e adivinhar onde ela está te tocando, você aceitaria?",
                "{mandante}, qual o tipo de gemido ou suspiro de {alvo} no seu ouvido que te faria perder a cabeça no ato?"
            ],
            "M_H": [
                "{mandante}, se {alvo} te tirasse para dançar no escuro e te pegasse pela cintura agora, você deixaria ele te beijar?",
                "{mandante}, qual parte do corpo de {alvo} te deixa mais desconcentrada durante o jogo?",
                "{mandante}, qual atitude masculina durante a provocação te faz ficar molhada instantaneamente?",
                "{mandante}, se {alvo} sussurrasse no seu ouvido uma ordem direta na frente de todo mundo, você obedeceria?",
                "{mandante}, confesse para a roda: o que você sente quando um homem segura o seu pescoço com firmeza e carinho?",
                "{mandante}, se você pudesse mandar {alvo} tirar a camisa e ficar só de calça até o fim da festa, você mandaria?",
                "{mandante}, qual é a provocação que {alvo} poderia fazer no seu corpo agora que te faria arrepiar inteira?"
            ],
            "M_M": [
                "{mandante}, você aceitaria um desafio de provocação a sós no quarto com {alvo} enquanto o grupo espera na sala?",
                "{mandante}, qual o nível de tesão que te dá ver outra mulher se exibindo de salto e lingerie em uma brincadeira de roda?",
                "{mandante}, se você e {alvo} tivessem que inventar um fetiche duplo para provocar os homens da mesa, qual seria?",
                "{mandante}, confesse: qual a parte do corpo de {alvo} que você mais sente vontade de passar as unhas ou a boca?"
            ],
            "H_H": [
                "{mandante}, diga para a roda: qual amigo daqui é o mais ruim de papo na hora de xavecar alguém na festa?",
                "{mandante}, quem do grupo tem mais cara de que é dominado dentro de casa e finge que é o bravo na rua?"
            ],
            "COLETIVA": [
                "🥂 EU NUNCA PICANTE: 'Eu nunca fiquei com mais de uma pessoa desta mesma roda de amigos!' Quem já fez, toma 2 doses!",
                "EU NUNCA FETICHE: 'Eu nunca usei lingeries especiais, saltos, vendas ou algemas em um encontro!' Quem já fez, bebe!",
                "VOTAÇÃO DA RODA: Quem aqui tem mais cara de que gosta de dar ordens na cama? O mais votado bebe 1 shot!",
                "CONFISSÃO DE MÍDIA: Quem da roda já tirou uma foto ousada no espelho do banheiro hoje antes de vir para o jogo?"
            ]
        },
        "desafio": {
            "H_M": [
                "{mandante} deve dar um beijo de 10 segundos na boca de {alvo} sem tirar as mãos do quadril/bunda dela!",
                "{mandante} deve deslizar as mãos por baixo da blusa/saia de {alvo} por 20 segundos sentindo a pele e a lingerie dela!",
                "COMANDO DA RODADA: {mandante} ganha o direito de inventar UM DESAFIO PICANTE para {alvo} cumprir na hora!",
                "{mandante} deve segurar {alvo} pela nuca com firmeza, aproximar os rostos a 1cm e dizer no ouvido dela exatamente o que quer fazer na cama.",
                "{mandante} deve tirar uma peça de roupa/acessório de {alvo} usando apenas a boca!",
                "{mandante} deve vendar os olhos de {alvo} com um pano/manga de blusa e passar os dentes e lábios pelo pescoço dela por 30 segundos.",
                "{mandante} deve posicionar a mão de {alvo} no seu próprio peitoral/barriga e mandar ela sentir seus batimentos acelerados.",
                "{mandante} deve puxar {alvo} para o seu colo, segurar a cintura dela e dar 3 mordidinhas provocantes no pescoço/saboneteira!"
            ],
            "M_H": [
                "{mandante} deve abotoar/desabotoar a camisa de {alvo} usando apenas os dentes na frente do grupo!",
                "{mandante} deve dar uma rebolada provocante no colo de {alvo} de salto alto por 20 segundos enquanto a roda faz pressão!",
                "COMANDO DA RODADA: {mandante} ganha o direito de ditar UMA ORDEM PICANTE para {alvo} executar imediatamente!",
                "{mandante} deve vendar os olhos de {alvo} e fazer ele adivinhar qual parte do seu corpo de lingerie/pele está encostando no rosto dele!",
                "{mandante} deve sentar de frente para {alvo}, travar as pernas nele e dar um beijo lento e profundo de 10 segundos!",
                "{mandante} deve passar uma pedra de gelo ou drink no peitoral de {alvo} e tomar com a boca diretamente na pele dele!",
                "{mandante} deve dar um tapa estalado na bunda de {alvo} e mandar ele servir a sua próxima bebida de joelhos!"
            ],
            "M_M": [
                "{mandante} e {alvo} devem dar um beijo de 10 segundos na boca e tirar uma foto da dupla para o grupo!",
                "{mandante} deve passar a mão por dentro da roupa de {alvo} e dar um aperto provocante no bumbum dela por 15 segundos!",
                "{mandante} de salto deve andar até {alvo}, sentar no colo dela de frente e dar um cheiro profundo no decote!",
                "{mandante} e {alvo} devem sussurrar simultaneamente um fetiche no ouvido uma da outra e depois dar um selinho demorado!"
            ],
            "H_H": [
                "{mandante} e {alvo} devem escolher duas mulheres da roda e servir um drink na boca delas sem usar as mãos!",
                "{mandante} e {alvo} devem pagar 1 shot duplo para a dupla mais bonita da sala agora!"
            ],
            "COLETIVA": [
                "TROCA DE ROUPAS: Todo mundo que estiver de peça preta ou vermelha deve trocar de lugar imediatamente na roda!",
                "SINAL DE LUZ: Apaguem as luzes principais da sala por 1 minuto. Todo mundo deve dar um abraço/beijo em quem estiver ao lado no escuro!",
                "CORRENTE DO BEIJO: {mandante} dá um beijo na bochecha/pescoço da pessoa à direita, que passa para a outra até rodar a mesa toda!"
            ]
        }
    },
    "fase3": {
        "verdade": {
            "H_M": [
                "{mandante}, confesse ao vivo: o quanto você está ereto/excitado olhando para as provocações e a lingerie/corpo de {alvo} nesta noite?",
                "{mandante}, qual fetiche extremo envolvendo salto, lingerie, amarras ou exibições você realizaria com {alvo} hoje mesmo?",
                "{mandante}, se {alvo} te desafiasse para ir ao banheiro da festa agora com ela por 3 minutos, você iria sem pensar duas vezes?",
                "{mandante}, se a roda te autorizasse a tirar a lingerie de {alvo} agora no quarto, qual seria a primeira coisa que faria na pele dela?",
                "{mandante}, olhe para o corpo de {alvo} de cima a baixo e diga em tom dominante qual parte você quer morder primeiro."
            ],
            "M_H": [
                "{mandante}, qual o limite máximo de loucura que você topa fazer com {alvo} assim que essa festa terminar?",
                "{mandante}, confesse: o quanto a pegada firme e a voz grave de {alvo} ao longo do jogo te deixaram morrendo de vontade de ir para o quarto?",
                "{mandante}, se você pudesse ver {alvo} tirando a roupa toda na sua frente agora, qual parte do corpo dele você olharia primeiro?",
                "{mandante}, qual o comando masculino de {alvo} na cama que te faria perder o controle e suspirar bem alto?",
                "{mandante}, você prefere que {alvo} te pegue no colo com força contra a parede ou que te deite devagar na cama?"
            ],
            "M_M": [
                "{mandante} e {alvo}, confessem para o grupo: vocês teriam coragem de ir juntas para um quarto no meio desta festa?",
                "{mandante}, qual fetiche entre duas mulheres em um encontro em grupo você mais tem vontade de experimentar na prática?",
                "{mandante}, quão excitante é ver os homens da mesa olhando para o charme, salto e corpo de {alvo} ao mesmo tempo que você?"
            ],
            "H_H": [
                "{mandante}, qual conselho safado e sem filtros você daria para {alvo} conseguir levar a parceira para o quarto no final da noite?",
                "{mandante}, confesse para o grupo: quem daqui é o amigo mais perigoso quando decide virar o jogo na Fase 3?"
            ],
            "COLETIVA": [
                "TRIBUNAL CRUCIAL: O grupo vota no casal/dupla de maior química da sala. A dupla deve dar um beijo de cinema ou virar 2 shots de tequila!",
                "REVELAÇÃO FINAL: Cada pessoa da mesa deve confessar quem da roda foi a pessoa que mais te deu tesão e vontade de pegar durante a noite!",
                "PERGUNTA PROIBIDA DA RODA: O grupo tem o direito de fazer UMA pergunta explícita para {mandante}. Ele(a) responde ou tira 2 peças de roupa!"
            ]
        },
        "desafio": {
            "H_M": [
                "{mandante} deve levar {alvo} para um canto da sala ou quarto por 1 minuto e dar um beijo intenso de língua longe dos olhos do grupo! 💥",
                "{mandante} deve desatar a lingerie/sutiã de {alvo} ou puxar a alça devagar usando apenas uma das mãos e os dentes na frente da roda!",
                "ORDEM SUPREMA: {mandante} deve ditar UM DESAFIO EXPLÍCITO para {alvo} fazer no seu corpo agora (beijo no pescoço, toque ou sussurro)!",
                "{mandante} deve deitar no sofá/mesa e deixar {alvo} sentar por cima do seu quadril para um beijo de 15 segundos na boca!",
                "{mandante} deve puxar {alvo} para um beijo colado, deslizar a mão por baixo da roupa dela até a calcinha/lingerie e sussurrar uma sacanagem no fone dela!",
                "{mandante} deve prender as mãos de {alvo} para cima com uma das mãos e dar 3 beijos demorados no decote e pescoço dela!",
                "{mandante} deve colocar {alvo} de costas para ele, puxar o quadril dela firme contra o dele e morder o ombro dela suavemente por 20 segundos!",
                "{mandante} deve tirar a própria camisa e pedir para {alvo} passar a língua do seu umbigo até o pescoço enquanto o grupo vibra!"
            ],
            "M_H": [
                "{mandante} deve guiar a mão de {alvo} para sentir a temperatura do seu corpo por dentro da roupa/lingerie por 20 segundos!",
                "{mandante} de salto alto deve dar um beijo de cinema em {alvo} segurando ele pelo pescoço com força e pernas entrelaçadas!",
                "ORDEM SUPREMA: {mandante} ganha o poder de mandar {alvo} fazer O QUE ELA QUISER no corpo dele por 30 segundos seguidos!",
                "{mandante} deve sentar no colo de {alvo}, colocar as mãos por dentro da camisa dele e dar mordidas provocantes nos lábios dele!",
                "{mandante} deve tirar o sutiã ou blusa por baixo da roupa e jogar no rosto de {alvo} olhando fixamente na lente dos olhos dele!",
                "{mandante} deve fazer uma dança privativa de 30 segundos no colo de {alvo} com as mãos dele segurando a cintura dela!",
                "{mandante} deve sussurrar no microfone/ouvido de {alvo} a coisa mais suja e proibida que quer que ele faça com ela no quarto hoje!"
            ],
            "M_M": [
                "{mandante} e {alvo} devem dar um beijo triplo com um dos homens do grupo ou um beijo duplo inesquecível de 15 segundos entre as duas!",
                "{mandante} deve tirar a alça da roupa de {alvo} e dar um beijo provocante no ombro, no decote e na boca dela!",
                "{mandante} e {alvo} devem dançar bem coladas, com as mãos nas bundas uma da outra por 30 segundos na frente do grupo!",
                "{mandante} deve sussurrar um desejo de fetiche no ouvido de {alvo} e dar uma moididinha na orelha dela até ela arfar!"
            ],
            "H_H": [
                "{mandante} e {alvo} devem virar um shot duplo de tequila/bebida forte sem fazer careta para fechar a Fase 3 com chave de ouro!",
                "{mandante} e {alvo} ganham o direito de mandar o grupo inteiro tomar 1 shot de bebida juntos agora!"
            ],
            "COLETIVA": [
                "CLÍMAX DO GRUPO: Todo mundo vira a sua bebida, dá um grito de comemoração e abraça/beija quem estiver ao lado!",
                "ORGASMO DA RESENHA: Cada participante deve gravar ou falar na roda o seu melhor gemido/suspiro em tom audível para a mesa!",
                "FOTO EXPLÍCITA DO GRUPO: Tirar uma foto de todos os participantes no espelho, com poses sensuais/provocantes para marcar a noite!",
                "ÚLTIMA RODADA DE SHOTS: Virar os copos de uma vez e decidir na roda quem vai para o quarto com quem no final do jogo!"
            ]
        }
    }
}

ORIGINAL_NEVER_CARDS = [
    "Eu nunca fiquei com alguém que conheci no mesmo dia em uma festa.",
    "Eu nunca mandei uma nudes para a pessoa errada no WhatsApp.",
    "Eu nunca me envolvi com mais de uma pessoa da mesma roda de amigos em momentos diferentes.",
    "Eu nunca fingi que estava bêbado(a) só para ter coragem de dar em cima de alguém.",
    "Eu nunca fiz um jogo que terminou em amassos no quarto.",
    "Eu nunca usei lingeries secretas ou saltos exclusivamente para um jogo de provocação.",
    "Eu nunca fui para o banheiro de um bar/festa para um momento íntimo rápido com alguém da mesa."
]

ORIGINAL_PUNISHMENTS = [
    "Tomar 2 shots seguidos da bebida escolhida pelo grupo sem fazer careta! 🥃🥃",
    "Ficar o restante do jogo sem poder usar as mãos para segurar o copo (alguém precisa servir).",
    "Mandar um áudio de 10 segundos no grupo do WhatsApp dando 3 gemidos provocantes.",
    "Tirar mais uma peça de roupa/acessório na frente de todo mundo!",
    "Pagar 10 flexões ou agachamentos enquanto a roda conta e debocha!",
    "Deixar o par ou o grupo fazer uma pergunta proibida e responder sem mentir!",
    "Servir um shot no próprio pescoço ou peito para o parceiro/alvo virar com a boca!"
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
            "game_type": "cards", 
            "scores": {},
            "game_over": False,
            "player_rounds": {}, # guarda {"fase1": count, "fase2": count, "fase3": count} por sid
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
    
    if room_id not in ACTIVE_ROOMS:
        emit('error', {'msg': 'Código de sala inválido!'})
        return

    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    join_room(room_id)
    
    if len(game_state["players"]) == 0:
        game_state["creator_name"] = player_name

    game_state["players"][request.sid] = {
        "name": player_name, 
        "gender": gender, 
        "pref": pref,
        "ready": False
    }
    
    if request.sid not in game_state["scores"]:
        game_state["scores"][request.sid] = 0
        
    if request.sid not in game_state["player_rounds"]:
        game_state["player_rounds"][request.sid] = {"fase1": 0, "fase2": 0, "fase3": 0}

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
    
    mandante = game_state["players"][game_state["current_player"]]
    alvo = game_state["players"].get(game_state["target_player"]) if game_state["target_player"] else None

    if alvo:
        comb_key = f"{mandante['gender']}_{alvo['gender']}"
    else:
        comb_key = "COLETIVA"

    session_cards = room["session_cards"]
    
    if fase in session_cards and tipo in session_cards[fase]:
        pool = session_cards[fase][tipo].get(comb_key)
        if not pool:
            pool = session_cards[fase][tipo].get("COLETIVA", [])
            
        if not pool:
            session_cards[fase][tipo] = copy.deepcopy(ORIGINAL_CARDS[fase][tipo])
            pool = session_cards[fase][tipo].get(comb_key, session_cards[fase][tipo]["COLETIVA"])
            
        text = random.choice(pool)
        mandante_nome = mandante["name"]
        alvo_nome = alvo["name"] if alvo else "GRUPO"
        text_formatado = text.replace("{mandante}", mandante_nome).replace("{alvo}", alvo_nome)
        
        pontos = {"fase1": 1, "fase2": 2, "fase3": 4}[fase]
        labels = {"fase1": "AQUECIMENTO", "fase2": "TENSÃO & FESTA", "fase3": "SEM LIMITES"}
        
        game_state["current_cards"] = {
            "fase_key": f"cards_{fase}_{tipo}",
            "real_fase": fase,
            "type": f"🔥 {labels[fase]} - {tipo.upper()}", 
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
        "type": "🛑 CASTIGO COMPULSÓRIO",
        "text": f"{mandante_nome} pulou a rodada!\n\nCumpra o seguinte castigo perante a roda agora:\n\n{punish_text}",
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
        if request.sid in game_state["player_rounds"]:
            game_state["player_rounds"][request.sid][fase_atual] += 1
        
    game_state["current_cards"] = {}
    sortear_proximo_turno(room_id)

def sortear_proximo_turno(room_id):
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    players = game_state["players"]
    p_ids = list(players.keys())
    
    if len(p_ids) < 2: return
    
    mandante_id = random.choice(p_ids)
    mandante = players[mandante_id]
    
    candidatos = []
    for pid in p_ids:
        if pid == mandante_id: continue
        p = players[pid]
        
        c1 = (mandante["pref"] == "ambos") or (p["gender"] != mandante["gender"])
        c2 = (p["pref"] == "ambos") or (mandante["gender"] != p["gender"])
        
        if c1 and c2:
            candidatos.append(pid)
            
    alvo_id = random.choice(candidatos) if candidatos else None
    
    game_state["current_player"] = mandante_id
    game_state["target_player"] = alvo_id
    
    socketio.emit('start_roulette_animation', {
        'winner_name': players[mandante_id]["name"],
        'target_name': players[alvo_id]["name"] if alvo_id else "TODOS DA RODA"
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
    
    ranking = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    top_text = "🏆 PLACAR FINAL DA FESTA:\n\n"
    for idx, (pid, pts) in enumerate(ranking):
        pname = players[pid]["name"] if pid in players else "Convidado"
        top_text += f"{idx+1}º Lugar: {pname} — {pts} pts\n"
        
    socketio.emit('game_update', {
        'card': {
            "fase_key": "game_over",
            "type": "🏁 FIM DO JOGO DE GRUPO",
            "text": top_text + "\nChegou a hora de pagar os últimos desafios da noite!",
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

    # LÓGICA DE LIBERAÇÃO DE FASES POR JOGADOR (TODOS DEVEM CUMPRIR PELO MENOS 1 RODADA)
    all_done_f1 = len(p_ids) > 0 and all(game_state["player_rounds"].get(uid, {}).get("fase1", 0) >= 1 for uid in p_ids)
    all_done_f2 = len(p_ids) > 0 and all(game_state["player_rounds"].get(uid, {}).get("fase2", 0) >= 1 for uid in p_ids)

    for uid in p_ids:
        my_f1 = game_state["player_rounds"].get(uid, {}).get("fase1", 0)
        my_f2 = game_state["player_rounds"].get(uid, {}).get("fase2", 0)
        
        socketio.emit('game_update', {
            'is_my_turn': (uid == game_state["current_player"]),
            'room_id': room_id,
            'current_player_name': current_name,
            'target_player_name': target_name,
            'card': game_state["current_cards"],
            'game_started': game_state["game_started"],
            'game_over': game_state["game_over"],
            'score_board': score_text,
            'players_status': players_status,
            'am_i_ready': game_state["players"][uid]["ready"],
            'fase2_unlocked': all_done_f1,
            'fase3_unlocked': (all_done_f1 and all_done_f2),
            'my_f1_count': my_f1,
            'my_f2_count': my_f2
        }, room=uid)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
