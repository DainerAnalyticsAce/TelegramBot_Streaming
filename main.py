import telebot
import re
import os
from telebot import types
import sqlite3
import random
import pandas as pd
import time
import subprocess #Para ejecutar Script
import logging  # Para registro de actividad
import hashlib

# Cargar datos desde el archivo CSV
df = pd.read_csv('usuarios.csv')

last_message_id = None  # Para almacenar el ID del último mensaje

user_banned = {}


# Reemplaza 'TOKEN' con tu token de acceso del bot
TOKEN = ''
bot = telebot.TeleBot(TOKEN)

#exit()
#Detener bot
#bot.stop_polling()

def reiniciar_variables():
    global last_message_id
    global user_banned

    last_message_id = None
    user_banned = {}

# Límite de intentos y tiempo de bloqueo
intentos_limite = 5
tiempo_bloqueo = 300  # En segundos (5 minutos)

# Diccionario para rastrear los intentos de inicio
intentos_inicio = {}

@bot.message_handler(content_types=["text", "photo"])
def mensajes_escritos_texto(message):
    user_id = message.from_user.id
    
    if user_id in user_banned and user_banned[user_id] > time.time():
        bot.send_message(message.chat.id, "Estás temporalmente bloqueado. Intenta más tarde.")
        return
    
    if message.text and message.text.startswith("/start"):
        bot.send_message(message.chat.id, "¡Bienvenido! Puedes iniciar el bot ahora.🤖")
        handle_start(message)
    else:
        if user_id not in intentos_inicio:
            intentos_inicio[user_id] = 1
        else:
            intentos_inicio[user_id] += 1

        if intentos_inicio[user_id] >= intentos_limite:
            user_banned[user_id] = time.time() + tiempo_bloqueo
            bot.send_message(message.chat.id, "Has excedido el número de intentos permitidos. Estás bloqueado temporalmente.")
            return

        bot.send_message(message.chat.id, "Debes iniciar el Bot🤖. Ingresa `/start` para comenzar.")


@bot.message_handler(commands=['start'])
def handle_start(message):

    global last_message_id

    # Si hay un mensaje anterior, lo eliminamos
    if last_message_id:
        bot.delete_message(message.chat.id, last_message_id)

    user_id = message.from_user.id
    # Si el usuario está baneado, se le impide interactuar con el bot
    if user_id in user_banned and user_banned[user_id] > time.time():
        # Usuario aún está baneado, mostrar un mensaje o bloquear la interacción
        bot.send_message(message.chat.id, "Estás temporalmente bloqueado. Intenta más tarde.")
        return
    

    # Saludo personalizado
    user_name = message.from_user.first_name
    welcome_text = f"Hola, {user_name}! ¡Bienvenido a DduranmeBot_Sof!\nSoy el bot🤖 más completo para ayudarte con cuentas de Streaming."

    streaming_text = (
        "¡Automatización para plataformas de Streaming🤖📡!\n\n"
        "Netflix🔴, HBO Max🟣, Disney🔵, Paramount⚪️ y más. "
        "Informamos sobre errores de acceso, solicitudes de pago, caídas "
        "y gestionamos cambios de claves para resolver cortes. ⏳"
    )

    # Creación de los botones estilo inline con emojis
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton('▶️ Iniciar Bot', callback_data='start_bot')
    item2 = types.InlineKeyboardButton('🤖 Quiero el Bot', callback_data='get_bot')
    item3 = types.InlineKeyboardButton('🛠️ Soporte', callback_data='Soporte')
    item4 = types.InlineKeyboardButton('📢Canal Informativo👥', callback_data='info_channel')

    # Adición de los botones al markup
    markup.add(item1, item2, item3, item4)

    # Envío del mensaje con el saludo, el texto informativo y los botones
    sent_message = bot.send_message(message.chat.id, f"{welcome_text}\n\n{streaming_text}", reply_markup=markup)
    last_message_id = sent_message.message_id

    reiniciar_variables()


# Función para manejar la interacción del botón "Iniciar Bot"
@bot.callback_query_handler(func=lambda call: call.data == 'start_bot')
def iniciar_bot(callback_query):
    message = callback_query.message

    bot.send_message(message.chat.id, "<b>Para confirmar que eres usuario nuestro⚡️</b>, y suscriptor del Bot debes ingresar el siguiente Dato👇🏼\n\n", parse_mode='HTML')
    bot.send_message(message.chat.id, "Para asegurar la autenticidad y seguridad de tu cuenta, te pedimos ingresar tu código de Verificación de <b>5 dígitos</b>. Por favor, asegúrate de ingresar solo números y de que el código contenga exactamente 5 dígitos.\n\n", parse_mode='HTML')

    bot.register_next_step_handler(message, verificar_codigo)
    # Eliminar el mensaje que contiene el formulario
    # Oculta el formulario editando el mensaje con un mensaje vacío

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    
    



@bot.callback_query_handler(func=lambda call: call.data == 'get_bot')
def quiero_el_bot(callback_query):
    message = callback_query.message
    
    texto_html = '👤<u>Ingresa al siguiente link del Admin✍🏼</u>\n\n' \
            'Vamos respondiendo por orden de llegada⌨️, en el menor tiempo posible se te envia la información⏱' \
            '<a href="https://www.tiktok.com/@dainerduranm">Ingresar al Perfil👤</a>. \n\n' \
            'Ahora si lograras Automatizar tu trabajo🤖'
            
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_atras = types.InlineKeyboardButton('Atrás 🔙', callback_data='go_back')
    markup.add(item_atras)

    bot.send_message(message.chat.id, text=texto_html, parse_mode='HTML', reply_markup=markup)

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)





#FUNCIONA PARA EL BOTÓN ATRAS DE LA FUNCIÓN  quiero_el_bot y SALGA EL FORMULARIO DE INICIO
@bot.callback_query_handler(func=lambda call: call.data == 'go_back')
def go_back(callback_query):
    message = callback_query.message
    handle_start(message)

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# Función para manejar el botón "Soporte"
@bot.callback_query_handler(func=lambda call: call.data == 'Soporte')
def soporte(callback_query):
    message = callback_query.message

    texto = '⚠️<u>Reporte de Fallas</u>⚠️\n\n' \
            'Si tienes problemas, comunícate con nuestro equipo ' \
            '<a href="https://t.me/SoportesDduranmeBot_Sof">Soportes DduranmeBot_Sof</a>. ' \
            'Tu ayuda es crucial para mejorar nuestros servicios.'

    markup = types.InlineKeyboardMarkup(row_width=1)
    item_atras = types.InlineKeyboardButton('Atrás 🔙', callback_data='go_back')
    markup.add(item_atras)

    bot.send_message(message.chat.id, text=texto, parse_mode='HTML', reply_markup=markup)

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)




# Función para manejar el botón "Canal Informativo"
@bot.callback_query_handler(func=lambda call: call.data == 'info_channel')
def canal_informativo(callback_query):
    message = callback_query.message
    
    texto_html = '<b><u>⬇️Ingresa a nuestro Grupo⬇️</u></b>\n\n' \
                 'En este grupo tendrás la información que necesitas para asesorarte de todo el bot y sus actualizaciones.\n\n' \
                 '<b><a href="https://t.me/+cF9mnfMVAWgyYWRh">Ingresa al Grupo DduranmeSoft</a></b>'

    markup = types.InlineKeyboardMarkup(row_width=1)
    item_atras = types.InlineKeyboardButton('Atrás 🔙', callback_data='go_back')
    markup.add(item_atras)

    bot.send_message(message.chat.id, text=texto_html, parse_mode='HTML', reply_markup=markup)

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)




#En lugar de usar códigos simples, podrías generar códigos únicos y seguros con una función de hash:
def generar_hash(codigo):
    # Si el código es un entero, conviértelo a cadena antes de encriptar
    if isinstance(codigo, int):
        codigo = str(codigo)
    return hashlib.sha256(codigo.encode()).hexdigest()

intentos_maximos = 3
tiempo_limite = 60  # En segundos
intentos_fallidos = {}

# Función para verificar el código ingresado por el usuario
def verificar_codigo(message):
    codigo_ingresado = message.text.strip()
    user_id = message.from_user.id
    usuario_valido = False  # Inicializar con un valor por defecto

    # Verificar si el código ingresado es numérico
    if codigo_ingresado.isdigit():
        # Encriptar el código ingresado para comparación segura
        codigo_encriptado = generar_hash(codigo_ingresado)

        # Verificar si el código encriptado coincide con alguna contraseña válida
        usuario_valido = any(df['password'].apply(generar_hash) == codigo_encriptado)
    else:
        bot.send_message(message.chat.id, "Por favor, ingresa solo números (0-9) como código de seguridad.")
        return

    if usuario_valido:
        formulario_inicio(message)
    else:
        if user_id not in intentos_fallidos:
            intentos_fallidos[user_id] = 1  # Inicializar el contador para el usuario
        else:
            intentos_fallidos[user_id] += 1  # Incrementar el contador existente

        if intentos_fallidos[user_id] >= intentos_maximos:
            user_banned[user_id] = time.time() + tiempo_limite
            logging.info(f"Usuario {user_id} bloqueado por exceder los intentos.")
            bot.send_message(message.chat.id, "Has excedido el número de intentos permitidos. Estás bloqueado temporalmente.")


# Esta será tu función para enviar el problema matemático
def enviar_problema_matematico(message):
    pregunta = "Resuelve este problema matemático: 2 + 2 = ?"
    opciones = ['3', '4', '5', '6']  # Supongamos que la respuesta correcta es '4'

    markup = types.InlineKeyboardMarkup(row_width=2)  # Definimos el ancho de la fila de botones
    buttons = [types.InlineKeyboardButton(text=opcion, callback_data=opcion) for opcion in opciones]
    
    markup.add(*buttons)

    bot.send_message(message.chat.id, pregunta, reply_markup=markup)
    bot.register_next_step_handler(message, verificar_respuesta)



def verificar_respuesta(message):
    user_id = message.from_user.id
    respuesta = message.text.strip()
    
    if respuesta.isdigit():
        if respuesta == '4':
            reiniciar_variables()
            handle_start(message)  # Cargar la función de nuevo
        else:
            # Se banea al usuario por 5 minutos
            bot.send_message(message.chat.id, "Debes esperar para cargar el Bot")
            user_banned[user_id] = time.time() + 300  # 300 segundos = 5 minutos
            bot.send_message(message.chat.id, "Usted ha sido baneado por 5 minutos.")
            time.sleep(300)  # Esperar 5 minutos
            handle_start(message)  # Cargar la función handle_start después de 5 minutos
    else:
        bot.send_message(message.chat.id, "Por favor, ingresa solo números (0-9) como código de seguridad.")
        

def formulario_inicio(message):
    username = message.from_user.username if message.from_user.username else ""
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    iteminicio1 = types.InlineKeyboardButton('Netflix🔴', callback_data='netflix')
    iteminicio2 = types.InlineKeyboardButton('HBO Max🟣', callback_data='hbo_max')
    iteminicio3 = types.InlineKeyboardButton('Disney🔵', callback_data='disney')
    iteminicio4 = types.InlineKeyboardButton('Paramount⚪️', callback_data='paramount')
    iteminicio5 = types.InlineKeyboardButton('Atrás 🔙', callback_data='atras')

    markup.add(iteminicio1, iteminicio2, iteminicio3, iteminicio4, iteminicio5)

    greeting_message = "<b>Bienvenido User👤 {}</b>, recuerda ingresar a tu Drive y actualizar tu tabla para que hagamos la conexión🛜\n\n".format(username)
    bot.send_message(message.chat.id, greeting_message, parse_mode='HTML')
    bot.send_message(message.chat.id, "Selecciona la plataforma de Streaming que deseas Automatizar🏁:", reply_markup=markup)

####################################################################
####################################################################
####################################################################
#ACÁ VAMOS A CREAR LAS FUNCIONES CORRESPONDIENTE DE CADA PLATAFORMA STREAMING A EJECUTAR.

@bot.callback_query_handler(func=lambda call: call.data == 'netflix')
def netflix_selected(callback_query):
    message = callback_query.message

    # Texto informando la función que va a ejecutar
    texto_info = "Seleccionaste Netflix. Elige una función a continuación:"

    markup = types.InlineKeyboardMarkup(row_width=1)

    # Creación de botones con diseños personalizados
    btn1 = types.InlineKeyboardButton('🥇Funcionalidad Netflix', callback_data='func_netflix')
    btn2 = types.InlineKeyboardButton('🥈Cambio de Clave Netflix', callback_data='clave_netflix')
    btn3 = types.InlineKeyboardButton('🥉Organizar Perfil Netflix', callback_data='perfil_netflix')

    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, texto_info, reply_markup=markup)

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)




# Funciones para cada botón

# Función para 'Funcionalidad Netflix'
@bot.callback_query_handler(func=lambda call: call.data == 'func_netflix')
def Form_Net_Funcionalidad_netflix_selected(callback_query):
    message = callback_query.message

    texto_info = (
        "Seleccionaste Funcionalidad Netflix. "
        "Te recomendamos actualizar tu tabla de Excel en tu carpeta privada en Drive."
        "\n\n¿Ya actualizaste tu tabla?"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)

    btn_si = types.InlineKeyboardButton('🏆Sí, Ejecutar', callback_data='actualizado_si')
    btn_no = types.InlineKeyboardButton('🔙No, ya verifico', callback_data='actualizado_no')

    markup.add(btn_si, btn_no)

    bot.send_message(message.chat.id, texto_info, reply_markup=markup)

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)



# Condicionales para los botones

# Si selecciona 'Sí'
@bot.callback_query_handler(func=lambda call: call.data == 'actualizado_si')
def actualizado_si(callback_query):
    message = callback_query.message
    bot.send_message(message.chat.id, "¡Perfecto! Acabas de ejecutar el codigo.")
    
    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    try:
        # Ejecutar el script 'Netflix_Bot_2024.py'
        subprocess.run(['python', 'Netflix_Bot_2024.py'])
        mensaje = (
            "El script de Netflix se ha ejecutado correctamente. En breve, el resultado estará disponible "
            "en la carpeta Drive."
        )
        bot.send_message(callback_query.message.chat.id, mensaje)
    except subprocess.CalledProcessError as e:
        mensaje_error = (
            f"El script de Netflix ha finalizado con un error. Código de error: {e.returncode}."
        )
        bot.send_message(callback_query.message.chat.id, mensaje_error)
    except Exception as e:
        # Otros errores que puedan ocurrir durante la ejecución del script
        mensaje_error = f"Ocurrió un error al ejecutar el script de Netflix: {e}"
        bot.send_message(callback_query.message.chat.id, mensaje_error)

# Si selecciona 'No'
@bot.callback_query_handler(func=lambda call: call.data == 'actualizado_no')
def actualizado_no(callback_query):
    message = callback_query.message
    bot.send_message(message.chat.id, "Por favor, actualiza tu tabla en Drive lo antes posible.")

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    # Volver al inicio del flujo del bot
    handle_start(message)



# Función para 'Cambio de Clave Netflix'  ######################################################################
@bot.callback_query_handler(func=lambda call: call.data == 'clave_netflix')
def Form_Net_CambioClave_netflix_selected(callback_query):
    message = callback_query.message

    texto_info = (
        "Seleccionaste Funcionalidad Netflix. "
        "Te recomendamos actualizar tu tabla de Excel en tu carpeta privada en Drive."
        "\n\n¿Ya actualizaste tu tabla?"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)

    btn_si_Net_sso = types.InlineKeyboardButton('🏆Sí, Ejecutar', callback_data='actualizado_si_Net_pass_sso')
    btn_no_Net_sso = types.InlineKeyboardButton('🔙No, ya verifico', callback_data='actualizado_no_Net_pass_sso')

    markup.add(btn_si_Net_sso, btn_no_Net_sso)

    bot.send_message(message.chat.id, texto_info, reply_markup=markup)

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

# Si selecciona 'Sí'
@bot.callback_query_handler(func=lambda call: call.data == 'actualizado_si_Net_pass_sso')
def actualizado_si_Net_pass_sso(callback_query):
    message = callback_query.message
    bot.send_message(message.chat.id, "¡Perfecto! Acabas de ejecutar el codigo.")
    
    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    try:
        # Ejecutar el script 'Net-automa.py'
        subprocess.run(['python', 'Net-password-sso.py'])
        mensaje = (
            "El script de Netflix se ha ejecutado correctamente. En breve, el resultado estará disponible "
            "en la carpeta Drive."
        )
        bot.send_message(callback_query.message.chat.id, mensaje)
    except subprocess.CalledProcessError as e:
        mensaje_error = (
            f"El script de Netflix ha finalizado con un error. Código de error: {e.returncode}."
        )
        bot.send_message(callback_query.message.chat.id, mensaje_error)
    except Exception as e:
        # Otros errores que puedan ocurrir durante la ejecución del script
        mensaje_error = f"Ocurrió un error al ejecutar el script de Netflix: {e}"
        bot.send_message(callback_query.message.chat.id, mensaje_error)

# Si selecciona 'No'
@bot.callback_query_handler(func=lambda call: call.data == 'actualizado_no_Net_pass_sso')
def actualizado_no_Net_pass_sso(callback_query):
    message = callback_query.message
    bot.send_message(message.chat.id, "Por favor, actualiza tu tabla en Drive lo antes posible.")

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    # Volver al inicio del flujo del bot
    handle_start(message)


# Función para 'Organizar Perfil Netflix' ######################################################################
@bot.callback_query_handler(func=lambda call: call.data == 'perfil_netflix')
def Form_Net_OrganizarPerf_netflix_selected(callback_query):
    message = callback_query.message
    bot.send_message(message.chat.id, "Actualizando servidor para esta nueva función")
    # Lógica para organizar el perfil de Netflix
    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id) 

    # Iniciar de nuevo la conversación
    handle_start(message)



###############################################################################################
###############################################################################################


# Función para manejar la selección de HBO Max
@bot.callback_query_handler(func=lambda call: call.data == 'hbo_max')
def hbo_max_selected(callback_query):
    message = callback_query.message

    texto_info = (
        "Con esta función del Bot podrás ejecutar y saber el funcionamiento de las cuentas de HBO Max "
        "que estén en el archivo de Excel en Google Drive.\n\n¿Deseas empezar el proceso?"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)

    btn_empezar = types.InlineKeyboardButton('Empezar proceso', callback_data='start_hbo_max')
    btn_atras = types.InlineKeyboardButton('Atrás', callback_data='atras')

    markup.add(btn_empezar, btn_atras)

    bot.send_message(message.chat.id, texto_info, reply_markup=markup)
    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)



# Función para manejar la opción de empezar el proceso de HBO Max
@bot.callback_query_handler(func=lambda call: call.data == 'start_hbo_max')
def Form_HBO_Max(callback_query):
    message = callback_query.message

    texto_info = (
        "Con esta función del Bot podrás ejecutar y saber el funcionamiento de las cuentas de HBO Max que estén en el archivo de EXCEL DRIVE."
    )

    markup = types.InlineKeyboardMarkup(row_width=2)

    btn_si = types.InlineKeyboardButton('🏆Sí, Ejecutar', callback_data='actualizar_si_hbomax')
    btn_no = types.InlineKeyboardButton('🔙No, ya verifico', callback_data='actualizar_no_hbomax')

    markup.add(btn_si, btn_no)

    bot.send_message(message.chat.id, texto_info, reply_markup=markup)
    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'actualizar_si_hbomax')
def actualizar_si_hbomax(callback_query):
    message = callback_query.message
    bot.send_message(message.chat.id, "Ejecutando el script para HBO Max...")

    try:
        # Ejecutar el script 'hbomax-auto.py'
        subprocess.run(['python', 'hbomax-auto.py'])
        mensaje = (
            "El script de HBO Max se ha ejecutado correctamente. En breve, el resultado estará disponible "
            "en la carpeta Drive."
        )
        bot.send_message(callback_query.message.chat.id, mensaje)
    except subprocess.CalledProcessError as e:
        mensaje_error = (
            f"El script de HBO Max ha finalizado con un error. Código de error: {e.returncode}."
        )
        bot.send_message(callback_query.message.chat.id, mensaje_error)
    except Exception as e:
        # Otros errores que puedan ocurrir durante la ejecución del script
        mensaje_error = f"Ocurrió un error al ejecutar el script de HBO Max: {e}"
        bot.send_message(callback_query.message.chat.id, mensaje_error)

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'actualizar_no_hbomax')
def actualizar_no_hbomax(callback_query):
    message = callback_query.message
    bot.send_message(message.chat.id, "Por favor, verifica tu tabla en Drive lo antes posible.")

    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    # Regresar al inicio del flujo del bot
    handle_start(message)



@bot.callback_query_handler(func=lambda call: call.data == 'disney')
def disney_selected(callback_query):
    message = callback_query.message
    # Lógica para manejar la selección de Disney
    bot.send_message(message.chat.id, "Actualizando servidor para esta nueva función")
    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    # Iniciar de nuevo la conversación
    handle_start(message)





@bot.callback_query_handler(func=lambda call: call.data == 'paramount')
def paramount_selected(callback_query):
    message = callback_query.message
    # Lógica para manejar la selección de Paramount
    bot.send_message(message.chat.id, "Actualizando servidor para esta nueva función")
    # Eliminar el historial de mensajes y reiniciar la conversación
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    # Iniciar de nuevo la conversación
    handle_start(message)




@bot.callback_query_handler(func=lambda call: call.data == 'atras')
def atras_selected(callback_query):
    message = callback_query.message

    markup = types.InlineKeyboardMarkup(row_width=1)
    item_atras = types.InlineKeyboardButton('Atrás 🔙', callback_data='go_back')
    markup.add(item_atras)

    # Eliminar el historial de mensajes
    user_id = callback_query.from_user.id
    last_message_id = None
    intentos_inicio[user_id] = 0  # Reiniciar los intentos de inicio
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    # Iniciar de nuevo la conversación
    handle_start(message)






if __name__ == '__main__':
    print('Iniciado el Bot')
    bot.polling(none_stop=True)

