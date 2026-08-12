import re

import requests
from decouple import config


# CONEXÃO COM EVOLUTION
base_url_evo = config('BASE_URL_EVO')
instance_token = config('API_KEY_EVO')
instance_name = config('INSTANCE_NAME')

headers = {'Content-Type': 'application/json', 'apikey': instance_token}


class EvolutionAPI:
    def __init__(self):
        self.base_url_evo = base_url_evo
        self.instance_name = instance_name
        self.headers = headers

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f'{self.base_url_evo}{endpoint}/{self.instance_name}'
        response = requests.post(url=url, headers=self.headers, json=payload)

        response.raise_for_status()
        return response.json()

    def sender_text(self, number: str, text: str) -> list[dict]:
        
        # Remove apenas espaços em branco excessivos, mantém \n
        texto = text.strip()
        
        # Divide por parágrafos (blocos separados por \n\n)
        paragrafos = [p.strip() for p in texto.split('\n\n') if p.strip()]
        
        responses = []
        
        for paragrafo in paragrafos:
            # Se parágrafo > 300 chars, quebra em frases
            if len(paragrafo) > 300:
                # Split inteligente: só quebra após ., !, ? seguidos de espaço
                frases = re.split(r'(?<=[.!?])\s+', paragrafo)
                
                for frase in frases:
                    if not frase.strip():
                        continue
                        
                    payload = {
                        'number': number,
                        'text': frase.strip(),
                        'delay': min(len(frase) * 30, 3000),  # Simula digitação (max 3s)
                        'presence': 'composing',
                    }
                    
                    response = self._post(endpoint='/message/sendText', payload=payload)
                    responses.append(response)
            else:
                # Parágrafo curto: envia inteiro
                payload = {
                    'number': number,
                    'text': paragrafo,
                    'delay': min(len(paragrafo) * 30, 3000),
                    'presence': 'composing',
                }
                
                response = self._post(endpoint='/message/sendText', payload=payload)
                responses.append(response)
        
        return responses