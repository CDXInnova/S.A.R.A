import speech_recognition as sr
import openai
import pyttsx3
import mysql.connector
import os
import subprocess

openai.api_key = "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"


# Funciones relacionadas a la base de datos
def establecer_conexion():
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'database': 'bitacora',
        'raise_on_warnings': True
    }
    cnx = mysql.connector.connect(**config)
    return cnx


def cerrar_conexion(cnx):
    cnx.close()


def insertar_consultoria(cnx, numero, pregunta, respuesta_corta, respuesta_detallada):
    cursor = cnx.cursor()
    query = "INSERT INTO consultoria (numero, pregunta, respuesta_corta, respuesta_detallada) VALUES (%s, %s, %s, %s)"
    values = (numero, pregunta, respuesta_corta, respuesta_detallada)
    cursor.execute(query, values)
    cnx.commit()
    cursor.close()


def obtener_respuesta(cnx, pregunta, respuesta_type):
    cursor = cnx.cursor()
    query = "SELECT respuesta_corta, respuesta_detallada FROM consultoria WHERE pregunta = %s"
    cursor.execute(query, (pregunta,))
    row = cursor.fetchone()

    if row is not None:
        if respuesta_type == "corta":
            return row[0]
        elif respuesta_type == "detallada":
            return row[1]
    else:
        return "No tengo respuesta para esa pregunta. ¿Deseas que aprenda algo nuevo?"


# Funciones de reconocimiento de voz
def transformar_audio_a_texto():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        print("Ya puedes hablar!")
        audio = r.listen(source)
        try:
            pedido = r.recognize_google(audio, language="es-PE")
            print("You: " + pedido)
            return pedido
        except sr.UnknownValueError:
            print("Ups, no entendí!")
            return "Sigo esperando"
        except sr.RequestError:
            print("Ups, no hay servicio!")
            return "Sigo esperando"
        except Exception:
            print("Ups, algo salió mal!")
            return "Sigo esperando"


# Funciones de síntesis de voz
def hablar(mensaje):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    voices = engine.getProperty('voices')
    for voice in voices:
        if "spanish" in voice.languages and "peru" in voice.id:
            engine.setProperty('voice', voice.id)
            break
    engine.say(mensaje)
    engine.runAndWait()


# Función para verificar y crear el archivo en el directorio actual
def crear_archivo(archivo):
    file_path = os.path.join(os.getcwd(), archivo)
    if os.path.exists(file_path):
        return archivo
    else:
        try:
            with open(file_path, 'w') as file:
                archivo_lower = archivo.lower()  # Convertir el nombre del archivoa minúsculas
                if archivo_lower.endswith(".py"):
                    file.write("# Código en Python\n\n")
                elif archivo_lower.endswith(".html"):
                    file.write("<!-- Código HTML -->\n\n")
                elif archivo_lower.endswith(".css"):
                    file.write("/* Código CSS */\n\n")
                elif archivo_lower.endswith(".js"):
                    file.write("// Código JavaScript\n\n")
                return archivo
        except Exception as e:
            print("Ocurrió un error al crear el archivo:", str(e))
            return None


# Función para abrir el archivo en Visual Studio Code
def abrir_en_vscode(archivo):
    archivo_lower = archivo.lower()  # Convertir el nombre del archivo a minúsculas
    try:
        subprocess.run(["code", archivo_lower])  # Usar archivo_lower en lugar de archivo
    except Exception as e:
        print("Ocurrió un error al abrir el archivo en Visual Studio Code:", str(e))


def mostrar_categorias():
    hablar("Puedes elegir entre las siguientes categorías:")
    hablar("1. Desarrollo web")
    hablar("2. Aplicación móvil")
    hablar("Por favor, elige una categoría diciendo el número correspondiente.")


def obtener_categoria():
    opcion = transformar_audio_a_texto().lower()
    if opcion == "1" or opcion == "uno":
        return "desarrollo web"
    elif opcion == "2" or opcion == "dos":
        return "aplicación móvil"
    else:
        return None


def mostrar_extensiones(categoria):
    hablar("Elige una extensión para el archivo de la categoría " + categoria + ".")
    if categoria == "desarrollo web":
        hablar("1. .html")
        hablar("2. .css")
        hablar("3. .js")
    elif categoria == "aplicación móvil":
        hablar("1. .java")
        hablar("2. .swift")
        hablar("3. .dart")


def obtener_extension():
    opcion = transformar_audio_a_texto().lower()
    if opcion == "1" or opcion == "uno":
        return ".html"
    elif opcion == "2" or opcion == "dos":
        return ".css"
    elif opcion == "3" or opcion == "tres":
        return ".js"
    else:
        return None


def escribir_codigo(codigo, archivo):
    file_path = os.path.join(os.getcwd(), archivo)
    try:
        with open(file_path, 'w') as file:
            file.write(codigo)
        return True
    except Exception as e:
        print("Ocurrió un error al escribir el código en el archivo:", str(e))
        return False


def crear_archivo_con_categoria():
    mostrar_categorias()
    categoria = obtener_categoria()

    while categoria is None:
        hablar("Lo siento, no entendí. Por favor, elige una categoría válida.")
        categoria = obtener_categoria()

    mostrar_extensiones(categoria)
    extension = obtener_extension()

    while extension is None:
        hablar("Lo siento, no entendí. Por favor, elige una extensión válida.")
        extension = obtener_extension()

    hablar("Por favor, proporciona el nombre del archivo.")
    nombre_archivo = transformar_audio_a_texto().lower()
    archivo = nombre_archivo + extension

    archivo_creado = crear_archivo(archivo)

    if archivo_creado:
        hablar("El archivo " + archivo_creado + " ha sido creado correctamente.")
        hablar("Ahora, por favor, abre el archivo en Visual Studio Code.")
        abrir_en_vscode(archivo_creado)
        hablar("Cuando estés listo, dime el código que deseas escribir.")
        codigo = transformar_audio_a_texto()

        if escribir_codigo(codigo, archivo_creado):
            hablar("El código ha sido escrito correctamente en el archivo.")
        else:
            hablar("Ocurrió un error al escribir el código en el archivo.")
    else:
        hablar("Ha ocurrido un error al crear el archivo.")


def main():
    conversation = ""
    cnx = establecer_conexion()

    hablar("Hola! Soy SARA, tu asesora virtual. Estoy aquí para apoyarte. ¿Hay algo que pueda hacer por ti?")

    while True:
        question = transformar_audio_a_texto().lower()

        if "consultoria para emprendedores" in question:
            hablar("¿Deseas una respuesta corta o detallada?")
            respuesta_type = transformar_audio_a_texto().lower()
            if respuesta_type == "corta":
                respuesta_column = "respuesta_corta"
            elif respuesta_type == "detallada":
                respuesta_column = "respuesta_detallada"
            else:
                respuesta_column = "respuesta_corta"

            respuesta = obtener_respuesta(cnx, question, respuesta_column)
            hablar(respuesta)

        elif "sara es hora de aprender" or "sara es hora de que aprendas" or "Sara recuerda esto" in question:
            hablar("Perfecto. Por favor, dime la pregunta o lo que deseas agregar a la base de datos.")
            nueva_pregunta = transformar_audio_a_texto().lower()
            hablar("Por favor, dime la respuesta corta correspondiente.")
            nueva_respuesta = transformar_audio_a_texto().lower()
            agregar_columna = "Información adicional"

            if nueva_pregunta and nueva_respuesta:
                insertar_consultoria(cnx, 1, nueva_pregunta, nueva_respuesta, agregar_columna)
                hablar("La nueva información ha sido agregada a la base de datos. ¿Hay algo más en lo que pueda ayudarte?")
            else:
                hablar("No se ha proporcionado información suficiente para agregar a la base de datos. ¿Hay algo más en lo que pueda ayudarte?")

        elif "escribir código" in question:
            crear_archivo_con_categoria()

        else:
            conversation += "\nYou: " + question + "\nSARA:"
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=conversation,
                temperature=0.5,
                max_tokens=100,
                top_p=0.3,
                frequency_penalty=0.5,
                presence_penalty=0.0,
                stop=["\n", " You:", " SARA:"]
            )
            answer = response.choices[0].text.strip()
            conversation += answer
            print("SARA: " + answer + "\n")
            hablar(answer)

    cerrar_conexion(cnx)


if __name__ == "__main__":
    main()
elif "escribir código" in transformar_audio_a_texto().lower():
    crear_archivo_con_categoria()
