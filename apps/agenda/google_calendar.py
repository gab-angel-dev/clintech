import json
import logging
from decouple import config
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES   = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = "America/Sao_Paulo"


def _get_service():
    token_json = config("GOOGLE_CALENDAR_TOKEN_JSON")
    if not token_json:
        logger.error(
            "GOOGLE_CALENDAR_TOKEN_JSON não encontrada nas variáveis de ambiente. "
            "Verifique o arquivo .env e reinicie o servidor."
        )
        raise EnvironmentError("google_calendar_not_configured")

    try:
        token_data = json.loads(token_json)
    except json.JSONDecodeError as e:
        logger.error("GOOGLE_CALENDAR_TOKEN_JSON contém JSON inválido: %s", e)
        raise EnvironmentError("google_calendar_invalid_token")

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )

    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def verificar_disponibilidade(calendar_id, start_time, end_time):
    try:
        service = _get_service()
        result  = service.events().list(
            calendarId=calendar_id,
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = result.get("items", [])
        if not events:
            return {"available": True}
        first = events[0]
        return {
            "available": False,
            "conflict": {
                "id":      first.get("id", ""),
                "summary": first.get("summary", "Sem título"),
                "start":   (first.get("start") or {}).get("dateTime", ""),
                "end":     (first.get("end") or {}).get("dateTime", ""),
            },
        }
    except EnvironmentError:
        raise  # já logado em _get_service
    except Exception as e:
        logger.error("Erro ao verificar disponibilidade no Google Calendar: %s", e)
        raise


def adicionar_evento(calendar_id, summary, start_time, end_time, description=""):
    try:
        service = _get_service()
        event   = service.events().insert(
            calendarId=calendar_id,
            body={
                "summary":     summary,
                "description": description,
                "start": {"dateTime": start_time, "timeZone": TIMEZONE},
                "end":   {"dateTime": end_time,   "timeZone": TIMEZONE},
            },
        ).execute()
        logger.info(
            "Evento criado no Google Calendar: %s (calendar: %s)",
            event.get("id"), calendar_id
        )
        return {
            "id":      event.get("id", ""),
            "summary": event.get("summary", ""),
            "start":   (event.get("start") or {}).get("dateTime", ""),
            "end":     (event.get("end") or {}).get("dateTime", ""),
        }
    except EnvironmentError:
        raise
    except Exception as e:
        logger.error("Erro ao criar evento no Google Calendar: %s", e)
        raise


def deletar_evento(calendar_id, event_id):
    try:
        service = _get_service()
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        logger.info("Evento deletado do Google Calendar: %s", event_id)
    except HttpError as e:
        if e.resp.status == 404:
            logger.warning("Evento %s não encontrado no Google Calendar (já deletado?)", event_id)
            return
        logger.error("Erro HTTP ao deletar evento %s: %s", event_id, e)
        raise
    except EnvironmentError:
        raise
    except Exception as e:
        logger.error("Erro ao deletar evento %s do Google Calendar: %s", event_id, e)
        raise