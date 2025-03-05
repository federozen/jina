import os
import streamlit as st
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(page_title="AI Web Scraper Chatbot", page_icon="🌐")

# Inicializar estado de sesión para el historial de chat
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Título y descripción
st.title("🌐 Web Scraper Chatbot con Jina.ai")
st.write("Obtén información de cualquier sitio web usando Jina.ai")

# Obtener API Key de variable de entorno
openai_api_key = os.getenv('OPENAI_API_KEY')

# Verificar si la API Key está configurada
if not openai_api_key:
    st.warning("Por favor, configura la variable de entorno OPENAI_API_KEY")
    st.stop()

# Función para hacer scraping del sitio web con Jina.ai
def scrape_website(url):
    try:
        # Uso correcto de Jina.ai: prepend https://r.jina.ai/ a la URL original
        jina_url = f"https://r.jina.ai/{url}"
        
        # Configurar headers para evitar bloqueos
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Realizar la solicitud
        response = requests.get(jina_url, headers=headers)
        
        if response.status_code == 200:
            # Limitar la longitud del contenido para no sobrecargar el modelo
            return response.text[:15000]
        else:
            return f"Error al obtener el contenido. Código de estado: {response.status_code}"
    except Exception as e:
        return f"Error de scraping: {str(e)}"

# Función para obtener respuesta de IA
def get_ai_response(user_input, scraped_content):
    try:
        # Inicializar cliente de OpenAI
        client = OpenAI(api_key=openai_api_key)
        
        # Preparar prompt
        prompt = f"""
        Soy un asistente de IA especializado en analizar contenido web.

        Pregunta del usuario: {user_input}

        Contenido del sitio web:
        {scraped_content}

        Por favor, analiza el contenido y responde a la pregunta de manera clara y concisa.
        Si el contenido no es relevante o no contiene información suficiente para responder, explícalo.
        """
        
        # Generar respuesta
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente útil para analizar contenido web."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generando respuesta: {str(e)}"

# Función principal de la aplicación
def main():
    # Input de URL
    url = st.text_input("Ingresa la URL del sitio web", placeholder="https://ejemplo.com")
    
    # Input de chat
    user_input = st.chat_input("Haz una pregunta sobre el sitio web")
    
    # Procesar entrada de usuario
    if user_input and url:
        # Verificar si ya existe esta conversación para evitar duplicados
        if not st.session_state.messages or st.session_state.messages[-1]["role"] != "assistant":
            # Añadir mensaje de usuario al historial
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Mostrar mensaje de usuario
            with st.chat_message("user"):
                st.write(user_input)
            
            # Scrapear sitio web con Jina.ai
            with st.spinner("Obteniendo contenido del sitio web con Jina.ai..."):
                scraped_content = scrape_website(url)
            
            # Generar respuesta de IA
            with st.spinner("Generando respuesta..."):
                ai_response = get_ai_response(user_input, scraped_content)
            
            # Añadir respuesta de IA al historial
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            # Mostrar respuesta de IA
            with st.chat_message("assistant"):
                st.write(ai_response)

    # Mostrar historial de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Ejecutar la aplicación
if __name__ == "__main__":
    main()