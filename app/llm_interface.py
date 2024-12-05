import logging
from typing import Generator

import ollama
import streamlit as st
import yaml
from deep_translator import GoogleTranslator  # Use deep-translator

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

config = load_config()

system_prompt = """
You are an AI assistant for Revenue Management decisions for a hotel that provides detailed answers based solely on the given context.

Instructions:

- Use **only** the information in the "Context" to answer the "Question".
- Do **not** include any external knowledge or assumptions.
- If the context doesn't contain sufficient information to answer the question, respond: "The context does not provide enough information to answer this question."

Formatting Guidelines:

- Use clear and concise language.
- Organize your answer into paragraphs for readability.
- Use bullet points or numbered lists to break down complex information when appropriate.
- Include headings or subheadings if relevant.
- Ensure proper grammar, punctuation, and spelling.

Remember: Base your entire response solely on the information provided in the context.
"""

def call_llm(context: str, prompt: str, language: str) -> Generator[str, None, None]:
    """Calls the language model with context and prompt to generate a response, translating if necessary."""
    try:
        # Debug: Log context and prompt
        logging.info(f"Context passed to LLM:\n{context[:500]}")  # Log first 500 characters for brevity
        logging.info(f"Prompt passed to LLM: {prompt}")
        
        if not context.strip():
            yield "The context is empty. Please provide valid data."
            return
        
        # If the selected language is English, stream the response directly
        if language == 'en':
            response = ollama.chat(
                model=config['llm_model'],
                stream=True,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"Context: {context}\nQuestion: {prompt}",
                    },
                ],
            )
            for chunk in response:
                if chunk["done"] is False:
                    yield chunk["message"]["content"]
                else:
                    break
        else:
            # For other languages, collect the response and translate it
            response = ollama.chat(
                model=config['llm_model'],
                stream=False,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"Context: {context}\nQuestion: {prompt}",
                    },
                ],
            )
            full_response = response["message"]["content"]
            translated_text = translate_text(full_response, language)
            yield translated_text  # Yield the translated text
    except Exception as e:
        logging.error(f"An error occurred while generating the response: {e}")
        st.error(f"An error occurred while generating the response: {e}")

def translate_text(text: str, dest_language: str) -> str:
    """Translates text to the desired language using deep-translator."""
    try:
        if not text.strip():
            return "The original response is empty. Translation is not possible."
        translator = GoogleTranslator(source='auto', target=dest_language)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        logging.error(f"An error occurred during translation: {e}")
        st.error(f"An error occurred during translation: {e}")
        return text  # Return original text if translation fails