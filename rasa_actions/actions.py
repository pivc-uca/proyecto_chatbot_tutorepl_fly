# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, UserUttered
import requests
import os
import json

URL_APP_FLASK = os.getenv("URL_APP")
URL_ARCHIVOS_APP = os.getenv("URL_ARCHIVOS")
   

class ActionAyudaImplementacionCaso(Action):

    def name(self) -> Text:
        return "action_ayuda_implementacion_caso"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(f"Entro action_ayuda_implementacion_caso") 
        caso_estudio = tracker.get_slot("caso_estudio")
        if caso_estudio == "Planta de energía nuclear":
            dispatcher.utter_message(response = "utter_ayuda_implementacion_planta_energia_nuclear")
        elif caso_estudio == "Tráfico de carreteras":
            dispatcher.utter_message(response = "utter_ayuda_implementacion_trafico_carretera")
        else:
            dispatcher.utter_message(response = "utter_sin_caso_estudio")
        return []
    
class ActionDatosCaso(Action):

    def name(self) -> Text:
        return "action_datos_caso"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(f"Entro action_datos_caso")  
        caso_estudio = tracker.get_slot("caso_estudio")
        print(f"Valor del slot caso_estudio : {caso_estudio}") # Para depuración
        
        # ruta = obtener_urls()

        if caso_estudio == "Planta de energía nuclear":
            # ruta_archivo = f"{ruta['URL_ARCHIVOS']}/archivos/datos_planta_energia_nuclear.txt"
            ruta_archivo = f"{URL_ARCHIVOS_APP}/datos_planta_energia_nuclear.txt" 
            
            mensaje = (
            f"Para descargar el archivo **.txt** con los datos del caso de estudio **{caso_estudio}**, "
            f"haz clic en este enlace: [Descargar archivo]({ruta_archivo})\n\n"
            f"Una vez descargado, copia y pega su contenido en el espacio **Time And Event Sequence**. Revisa si es necesario actualizar el nombre de los eventos antes de continuar."
            )
        
            dispatcher.utter_message(text=mensaje)
            #dispatcher.utter_message(response = "utter_datos_planta_energia_nuclear")
        elif caso_estudio == "Tráfico de carreteras":
            # ruta_archivo = f"{ruta['URL_ARCHIVOS']}/archivos/datos_trafico_carreteras.txt"
            ruta_archivo = f"{URL_ARCHIVOS_APP}/datos_trafico_carreteras.txt" 
            
            mensaje = (
            f"Para descargar el archivo **.txt** con los datos del caso de estudio **{caso_estudio}**, "
            f"haz clic en este enlace: [Descargar archivo]({ruta_archivo})\n\n"
            f"Una vez descargado, copia y pega su contenido en el espacio **Time And Event Sequence**. Revisa si es necesario actualizar el nombre de los eventos antes de continuar."
            )
            
            dispatcher.utter_message(text=mensaje)
            # dispatcher.utter_message(response = "utter_datos_trafico_carreteras")
        else:
            dispatcher.utter_message(response = "utter_sin_caso_estudio")
        return []  

class ActionPreguntarIA(Action):
    def name(self):
        return "action_preguntar_ia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict):
        print(f"Entro action_preguntar_ia") 
        # Obtener el valor del slot 'interaccion_ia'
        interaccion_ia_activada = tracker.get_slot("interaccion_ia")
        print(f"Valor del slot 'interaccion_ia': {interaccion_ia_activada}") # Para depuración
        
        # urls = obtener_urls()
        # urls_app_flask = f"{urls['URL_APP']}/chat"
        url_endpoint_chat = f"{URL_APP_FLASK}/chat"
        
        # Validar si el slot es True
        # if interaccion_ia_activada:
        user_message = tracker.latest_message.get("text")
        print(f"Valor user_message: {user_message}") # Para depuración
        print("Entro interaccion IA en action_preguntar_ia")

        try:
            # response = requests.post(urls_app_flask, json={"prompt": user_message})
            response = requests.post(url_endpoint_chat, json={"prompt": user_message})
            # response = requests.post("http://localhost:5000/chat", json={"prompt": user_message})
            response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
            reply = response.json().get("response", "No se recibió respuesta del modelo de IA.")
            dispatcher.utter_message(text=reply)

        except requests.exceptions.ConnectionError as e:
            dispatcher.utter_message(text="No pude conectar con el modelo local de IA. Por favor, asegúrate de que esté funcionando.")
            print(f"Error de conexión con el modelo IA: {e}")
        except requests.exceptions.RequestException as e:
                dispatcher.utter_message(text="Hubo un problema al obtener una respuesta del modelo de IA.")
                print(f"Error en la petición al modelo IA: {e}")
        except Exception as e:
            dispatcher.utter_message(text="Ocurrió un error inesperado al procesar tu solicitud con la IA.")
            print(f"Error inesperado en action_preguntar_ia: {e}")

        # else:
            # Si interaccion_ia es False, no hacer nada y posiblemente informar al usuario.
            #dispatcher.utter_message(text="La función de interacción con la IA no está activada en este momento.")
            # print("Interacción con IA deshabilitada por slot 'interaccion_ia'.")

        return []
    
class ActionSeleccionarCaso(Action):

    def name(self) -> Text:
        return "action_seleccionar_caso"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(f"Entro action_seleccionar_caso") 
        # Obtener el ID del caso
        v_id_caso = tracker.get_slot("id_caso")
        print(f"Valor del slot id_caso: {v_id_caso}") # Para depuración

        if v_id_caso == "1":
            v_caso_estudio = "Planta de energía nuclear"
            v_interaccion_ia = False
        elif v_id_caso == "2":
             v_caso_estudio = "Tráfico de carreteras"
             v_interaccion_ia = False
        else:
            v_caso_estudio = "Libre guiado por IA"
            v_interaccion_ia = True
            
        print(f"Valor del slot interaccion_ia asignacion: {v_interaccion_ia}") # Para depuración    

        dispatcher.utter_message(text=f"Has seleccionado el caso de estudio **{v_caso_estudio}**.")

        return [SlotSet("caso_estudio", v_caso_estudio), SlotSet("interaccion_ia", v_interaccion_ia)]      

class ActionProcesarErrorEpl(Action):
    def name(self) -> Text:
        return "action_procesar_error_epl"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(f"Entro action_procesar_error_epl")
        # Obtener el valor del slot 'interaccion_ia'
        interaccion_ia_activada = tracker.get_slot("interaccion_ia")
        print(f"Valor del slot 'interaccion_ia_activada': {interaccion_ia_activada}") # Para depuración    

        # url = obtener_urls()
        # url_app_flask = f"{url['URL_APP']}/chat"  
        url_endpoint_chat = f"{URL_APP_FLASK}/chat"        

        # 1. Extraer el error enviado desde la web
        # Si lo envías como /error_epl_detectado{"error_epl": "mensaje"}
        error_detectado = tracker.get_slot("error_epl")
        id_caso = tracker.get_slot("id_caso")
        
        # if not error_detectado:
            # Fallback por si el slot viene vacío, usamos el texto del último mensaje
            # error_detectado = tracker.latest_message.get("text")

        print(f"Procesando error: {error_detectado} para Caso: {id_caso}")
        
        # --- CASO 3: INTERACCIÓN CON IA ---
        if interaccion_ia_activada:
            # user_message = tracker.latest_message.get("text")
            print("Entro interaccion IA en action_procesar_error_epl")

            try:
                # response = requests.post(url_app_flask, json={"prompt": error_detectado})
                response = requests.post(url_endpoint_chat, json={"prompt": error_detectado})
                # response = requests.post("http://localhost:5000/chat", json={"prompt": error_detectado})
                response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
                reply = response.json().get("response", "No se recibió respuesta del modelo de IA.")
                # print(f"Respuesta del modelo IA: {reply}")
                dispatcher.utter_message(text=reply)

            except requests.exceptions.ConnectionError as e:
                dispatcher.utter_message(text="No pude conectar con el modelo local de IA. Por favor, asegúrate de que esté funcionando.")
                print(f"Error de conexión con el modelo IA: {e}")
            except requests.exceptions.RequestException as e:
                dispatcher.utter_message(text="Hubo un problema al obtener una respuesta del modelo de IA.")
                print(f"Error en la petición al modelo IA: {e}")
            except Exception as e:
                dispatcher.utter_message(text="Ocurrió un error inesperado al procesar tu solicitud con la IA.")
                print(f"Error inesperado en action_preguntar_ia: {e}")
        return []            