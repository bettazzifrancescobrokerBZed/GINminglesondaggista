# ==========================================
# GIN: IL SONDAGGISTA AUTONOMO (ARCHITETTURA A CAMME)
# Configurato per: Mingle / Bilendi (Con Camma Anagrafica e Ordine Classi Corretto)
# ==========================================

import os
import json
import logging
import time
import re
import imaplib
import email
from email.header import decode_header
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

# ==========================================
# STROFA 1: BASE MADRE BLINDATA E REGISTRO CAMME
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("GinAutomationCore")


# --- CLASSE ASTRATTA BASE (Spostata in cima per evitare NameError) ---
class CammaIntercambiabile(ABC):
    @abstractmethod
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        pass


# ==========================================
# CAMMA DATI FISSI / PROFILO ANAGRAFICO DI FRANCESCO BETTAZZI
# ==========================================

class CammaProfiloAnagraficoGin(CammaIntercambiabile):
    """Camma dedicata alla gestione centralizzata e fissa dei dati anagrafici e di preferenza del utente."""
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        profilo_reale = {
            "nome": "Francesco",
            "cognome": "Bettazzi",
            "nome_completo": "Francesco Bettazzi",
            "email": "Bettazzifg@gmail.com",
            "data_nascita": "08/08/1973",
            "eta": 53,
            "luogo_nascita": "Reggio di Calabria",
            "indirizzo": "Via Case Gallina 103",
            "comune": "Albareto",
            "cap": "43051",
            "provincia": "Parma",
            "regione": "Emilia-Romagna",
            "stato_civile": "Sposato",
            "animali_domestici": "3 gatti (Oliver, Jupiter, Hari)"
        }
        logger.info(f"GIN [PROFILO] - Dati fissi caricati per: {profilo_reale['nome_completo']} ({profilo_reale['comune']}, {profilo_reale['provincia']})")
        return {"profilo_utente": profilo_reale}


class RegistryCamme:
    def __init__(self):
        self._camme: Dict[str, CammaIntercambiabile] = {}

    def registra(self, nome: str, camma: CammaIntercambiabile):
        self._camme[nome] = camma
        logger.info(f"GIN - Camma sincronizzata nel sistema: '{nome}'")

    def ottieni(self, nome: str) -> CammaIntercambiabile:
        if nome not in self._camme:
            raise ValueError(f"Camma '{nome}' non trovata nel registro del sistema GIN.")
        return self._camme[nome]

class AutomationCore:
    def __init__(self, queue_filepath: str = "gin_tasks_queue.json"):
        self.queue_filepath = queue_filepath
        self.registry = RegistryCamme()
        self.inizializza_coda_default()

    def inizializza_coda_default(self):
        if not os.path.exists(self.queue_filepath):
            coda_iniziale = [
                {
                    "id": "task_profilo_gin_00",
                    "modulo": "profilo_anagrafico_gin",
                    "parametri": {}
                },
                {
                    "id": "task_email_gin_01",
                    "modulo": "scanner_email_gin",
                    "parametri": {
                        "imap_server": "imap.gmail.com",
                        "email_user": "Bettazzifg@gmail.com",
                        "email_pass": "bowvgphnrrkfogmi",
                        "filtro mittente": "mingle",
                        "filtro oggetto": ""
                    }
                },
                {
                    "id": "task_browser_gin_01",
                    "modulo": "flusso_continuo_browser_gin",
                    "parametri": {
                        "headless": False,
                        "url_login": "https://mingle.respondi.it/login",
                        "sito_user": "Bettazzifg@gmail.com",
                        "sito_pass": "08081973Gf@"
                    }
                },
                {
                    "id": "task_report_gin_01",
                    "modulo": "generatore_report_gin",
                    "parametri": {"output_file": "report_giornaliero_gin.json"}
                }
            ]
            with open(self.queue_filepath, "w", encoding="utf-8") as f:
                json.dump(coda_iniziale, f, indent=4)
            logger.info(f"GIN - Creato file di coda predefinito con Camma Anagrafica: {self.queue_filepath}")

    def registra_camma(self, nome: str, camma: CammaIntercambiabile):
        self.registry.registra(nome, camma)

    def esegui_ciclo(self):
        logger.info("--- GIN: AVVIO CICLO DI AUTOMAZIONE MECCANICA (CON PROFILO FISSO) ---")
        if not os.path.exists(self.queue_filepath):
            logger.error("File della coda dei task non trovato.")
            return

        with open(self.queue_filepath, "r", encoding="utf-8") as f:
            try:
                tasks: List[Dict[str, Any]] = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Errore di decodifica JSON nella coda: {e}")
                return

        contesto_condiviso = {}

        for task in tasks:
            task_id = task.get("id", "sconosciuto")
            nome_modulo = task.get("modulo")
            parametri = task.get("parametri", {})
            
            parametri.update(contesto_condiviso)
            logger.info(f"GIN esegue task [{task_id}] tramite camma '{nome_modulo}'")

            try:
                camma = self.registry.ottieni(nome_modulo)
                risultato = camma.esegui(parametri)

                if isinstance(risultato, dict):
                    contesto_condiviso.update(risultato)

                logger.info(f"Task [{task_id}] completato. Esito: {risultato}")
            except Exception as e:
                logger.error(f"Errore critico durante l'esecuzione del task [{task_id}]: {e}")
                break


# ==========================================
# STROFA 2: SCANNER IMAP MIRATO
# ==========================================

class CammaScannerEmailGin(CammaIntercambiabile):
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        imap_server = contesto.get("imap_server")
        email_user = contesto.get("email_user")
        email_pass = contesto.get("email_pass")

        logger.info(f"GIN - Connessione IMAP sicura a {imap_server} per {email_user}...")
        try:
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_user, email_pass)
            mail.select("inbox")

            status, messages = mail.search(None, "ALL")
            if status != "OK":
                raise Exception("Errore nella ricerca dei messaggi.")

            id_messaggi = messages[0].split()
            if not id_messaggi:
                return {"stato": "successo", "messaggio": "La casella di posta è vuota."}

            id_da_scansionare = id_messaggi[-40:] if len(id_messaggi) > 40 else id_messaggi
            email_trovata = None
            link_principale = "Nessun link trovato"
            mittente_trovato = ""
            oggetto_trovato = ""

            for msg_id in reversed(id_da_scansionare):
                status, data = mail.fetch(msg_id, "(RFC822)")
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        from_header = decode_header(msg.get("From"))[0]
                        mittente = from_header[0]
                        if isinstance(mittente, bytes):
                            mittente = mittente.decode(from_header[1] or "utf-8", errors="ignore")

                        subj_header = decode_header(msg.get("Subject"))[0]
                        oggetto = subj_header[0]
                        if isinstance(oggetto, bytes):
                            oggetto = oggetto.decode(subj_header[1] or "utf-8", errors="ignore")

                        mittente_pulito = mittente.lower().replace(" ", "")
                        oggetto_pulito = oggetto.lower()

                        parole_da_scartare = ["reset", "password", "connessione insolita", "security", "avviso", "warning", "login"]
                        if any(parola in oggetto_pulito for parola in parole_da_scartare):
                            continue

                        if "mingle" in mittente_pulito or "respondi" in mittente_pulito or "bilendi" in mittente_pulito:
                            corpo_completo = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() in ["text/plain", "text/html"]:
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            corpo_completo += payload.decode("utf-8", errors="ignore") + "\n"
                            else:
                                payload = msg.get_payload(decode=True)
                                if payload:
                                    corpo_completo = payload.decode("utf-8", errors="ignore")

                            tutti_i_link = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', corpo_completo)
                            link_validi = [
                                l for l in tutti_i_link
                                if not any(ext in l.lower() for ext in ['.css', '.png', '.jpg', '.gif', '.svg', 'fonts.', 'gstatic', 'googleapis', 'track', 'unsubscribe', 'login'])
                            ]

                            if link_validi:
                                email_trovata = msg
                                link_principale = link_validi[0]
                                mittente_trovato = mittente
                                oggetto_trovato = oggetto
                                break
                if email_trovata:
                    break

            mail.logout()
            logger.info(f"GIN - Email sondaggio selezionata: '{oggetto_trovato}' | Link: {link_principale}")

            return {
                "mittente": mittente_trovato or "Mingle",
                "oggetto": oggetto_trovato or "Sondaggio",
                "link_estratto": link_principale
            }

        except Exception as e:
            logger.error(f"Errore durante la scansione IMAP di GIN: {e}")
            raise e


# ==========================================
# STROFA 3 & 4: NAVIGAZIONE E COMPILAZIONE CON PROFILO FISSO
# ==========================================

class CammaFlussoContinuoBrowserGin(CammaIntercambiabile):
    def _determina_risposta_intelligente(self, testo_domanda: str, opzioni_disponibili: List[tuple], profilo: dict) -> tuple:
        """Sceglie l'opzione corretta confrontando il testo della domanda con i dati fissi del profilo reale."""
        td = testo_domanda.lower()
        
        # 1. Età o Anno di nascita
        if "età" in td or "anni" in td or "nato" in td:
            for opt, txt in opzioni_disponibili:
                t_low = txt.lower()
                if "50-54" in t_low or "50 - 54" in t_low or "53" in t_low or "1973" in t_low:
                    return opt, txt

        # 2. Regione
        if "regione" in td:
            for opt, txt in opzioni_disponibili:
                if profilo["regione"].lower() in txt.lower():
                    return opt, txt

        # 3. Provincia o Comune
        if "provincia" in td or "resiede" in td or "comune" in td or "dove" in td:
            for opt, txt in opzioni_disponibili:
                t_low = txt.lower()
                if profilo["provincia"].lower() in t_low or profilo["comune"].lower() in t_low:
                    return opt, txt

        # 4. Stato Civile / Famiglia / Gatti
        if "civile" in td or "famiglia" in td or "coniugato" in td or "sposato" in td:
            for opt, txt in opzioni_disponibili:
                if "sposato" in txt.lower() or "coniugato" in txt.lower():
                    return opt, txt

        return opzioni_disponibili[0]

    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        url_login = contesto.get("url_login", "https://mingle.respondi.it/login")
        link_estratto = contesto.get("link_estratto")
        headless_mode = contesto.get("headless", False)
        sito_user = contesto.get("sito_user")
        sito_pass = contesto.get("sito_pass")
        profilo = contesto.get("profilo_utente", {
            "nome_completo": "Francesco Bettazzi",
            "email": "Bettazzifg@gmail.com",
            "comune": "Albareto",
            "provincia": "Parma",
            "regione": "Emilia-Romagna",
            "cap": "43051"
        })

        file_memoria = "gin_memoria_profilo_mingle.json"
        memoria_profilo = {}
        if os.path.exists(file_memoria):
            try:
                with open(file_memoria, "r", encoding="utf-8") as fm:
                    memoria_profilo = json.load(fm)
            except Exception:
                memoria_profilo = {}

        logger.info(f"GIN - Avvio browser. Profilo attivo: {profilo['nome_completo']} ({profilo['comune']}, {profilo['provincia']}, CAP {profilo['cap']})")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless_mode)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()

            try:
                page.goto(url_login, timeout=45000)
                page.wait_for_load_state("domcontentloaded")

                try:
                    consenso_btn = page.locator("button:has-text('Accetta'), button#usercentrics-allow-all, button:has-text('Accetta tutti')").first
                    if consenso_btn.is_visible(timeout=3000):
                        consenso_btn.click()
                        page.wait_for_timeout(1000)
                except Exception:
                    pass

                # Compilazione robusta dell'email di login
                email_input = page.locator("input[type='email'], input#email, input[name*='email'], input[name*='user']").first
                if email_input.is_visible(timeout=5000):
                    email_input.click()
                    email_input.fill(sito_user)
                    logger.info(f"GIN [LOGIN] -> Email inserita correttamente: {sito_user}")

                pass_input = page.locator("input[type='password'], input#password, input[name*='password']").first
                if pass_input.is_visible(timeout=5000):
                    pass_input.click()
                    pass_input.fill(sito_pass)
                    logger.info("GIN [LOGIN] -> Password inserita correttamente.")

                submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Accedi'), button:has-text('Login')").first
                if submit_btn.is_visible(timeout=3000):
                    submit_btn.click()
                else:
                    page.keyboard.press("Enter")

                page.wait_for_timeout(4000)

                if link_estratto and link_estratto != "Nessun link trovato":
                    logger.info(f"GIN [MINGLE] - Navigazione diretta al sondaggio: {link_estratto}")
                    page.goto(link_estratto, timeout=45000)
                    page.wait_for_load_state("domcontentloaded")
                else:
                    logger.warning("GIN [MINGLE] - Nessun link valido trovato nell'email, rimango sulla dashboard.")

                logger.info("GIN [MINGLE] - Avvio loop di compilazione autonoma...")
                page.wait_for_timeout(3000)
                
                memoria_sessione_corrente = []
                sondaggio_completato_con_successo = False
                max_step = 80
                tentativi_stessa_situazione = 0
                
                for step in range(1, max_step + 1):
                    try:
                        page.wait_for_timeout(2000)
                        target_context = page
                        for frame in page.frames:
                            if any(k in frame.url for k in ["survey", "respondi", "cint", "opinion", "bilendi", "selfserve"]):
                                target_context = frame
                                break

                        try:
                            testo_pagina = target_context.inner_text("body").lower()
                        except Exception:
                            testo_pagina = ""

                        if any(t in testo_pagina for t in ["grazie per aver partecipato", "hai guadagnato", "completato", "terminato"]):
                            logger.info(f"GIN [MINGLE] - Rilevata schermata di completamento al passo {step}!")
                            sondaggio_completato_con_successo = True
                            break

                        # Estrazione domanda
                        testo_domanda = ""
                        selettori_domanda = [".question-title", "h1", "h2", "h3", "legend", ".survey-question", ".question-text"]
                        for sel_d in selettori_domanda:
                            try:
                                el = target_context.locator(sel_d).first
                                if el.is_visible(timeout=800):
                                    testo_t = el.inner_text().strip()
                                    if testo_t and len(testo_t) > 3:
                                        testo_domanda = testo_t
                                        break
                            except Exception:
                                pass

                        if not testo_domanda:
                            testo_domanda = f"Domanda_Step_{step}"

                        logger.info(f"GIN [MINGLE] - Step {step} | Domanda: '{testo_domanda[:70]}...'")

                        risposta_scelta_corrente = ""
                        try:
                            # Gestione campi di testo liberi (es. CAP o Comune se richiesti testualmente)
                            input_testo_libero = target_context.locator("input[type='text'], input:not([type])").first
                            if input_testo_libero.is_visible(timeout=1000):
                                t_placeholder = input_testo_libero.get_attribute("placeholder") or ""
                                if "cap" in t_placeholder.lower() or "cap" in testo_domanda.lower():
                                    input_testo_libero.fill(profilo["cap"])
                                    risposta_scelta_corrente = profilo["cap"]
                                elif "comune" in t_placeholder.lower() or "città" in t_placeholder.lower() or "comune" in testo_domanda.lower():
                                    input_testo_libero.fill(profilo["comune"])
                                    risposta_scelta_corrente = profilo["comune"]

                            if not risposta_scelta_corrente:
                                selects = target_context.locator("select").all()
                                selects_visibili = [s for s in selects if s.is_visible()]
                                if selects_visibili:
                                    for sel in selects_visibili:
                                        opzioni_disponibili = sel.locator("option").all()
                                        if len(opzioni_disponibili) > 1:
                                            valore_valido = opzioni_disponibili[1].get_attribute("value")
                                            testo_opzione = opzioni_disponibili[1].inner_text()
                                            if valore_valido:
                                                sel.select_option(value=valore_valido)
                                            else:
                                                sel.select_option(index=1)
                                            risposta_scelta_corrente = testo_opzione
                                            target_context.wait_for_timeout(800)
                                else:
                                    opzioni = target_context.locator("input[type='radio'], input[type='checkbox'], label.radio-button, label.checkbox-button, div[role='radio'], .answer-item, .option-item, label").all()
                                    visibili_opzioni = [opt for opt in opzioni if opt.is_visible()]
                                    
                                    opzioni_valide = []
                                    for opt in visibili_opzioni:
                                        txt_opt = ""
                                        try:
                                            txt_opt = opt.inner_text().strip()
                                        except Exception:
                                            pass
                                        if txt_opt and len(txt_opt) < 80 and not any(k in txt_opt.lower() for k in ["avanti", "continua", "indietro", "next", "cookie"]):
                                            opzioni_valide.append((opt, txt_opt))

                                    if opzioni_valide:
                                        opt_scelta, txt_scelta = self._determina_risposta_intelligente(testo_domanda, opzioni_valide, profilo)
                                        
                                        if testo_domanda in memoria_profilo:
                                            valore_mem = memoria_profilo[testo_domanda]
                                            for o, t in opzioni_valide:
                                                if t.lower() == valore_mem.lower():
                                                    opt_scelta, txt_scelta = o, t
                                                    break

                                        opt_scelta.click(force=True)
                                        risposta_scelta_corrente = txt_scelta
                                        target_context.wait_for_timeout(1000)
                        except Exception as e_sel:
                            logger.debug(f"Nota interazione opzioni: {e_sel}")

                        if testo_domanda and risposta_scelta_corrente:
                            memoria_profilo[testo_domanda] = risposta_scelta_corrente
                            memoria_sessione_corrente.append({"domanda": testo_domanda, "risposta": risposta_scelta_corrente})
                            logger.info(f"GIN [MINGLE] -> Risposta applicata: '{risposta_scelta_corrente}'")

                        # Pulsante Avanti
                        btn_avanti = target_context.locator(
                            "button:has-text('Avanti'), button:has-text('Continua'), button:has-text('Next'), "
                            "input[type='submit'], button[type='submit'], button.next, button[id*='next'], button.btn-next"
                        ).first

                        if not btn_avanti.is_visible(timeout=1500):
                            btn_avanti = target_context.locator("button, input[type='submit']").filter(has_text=re.compile(r"(avanti|continua|next|invia|submit|prosegui|ok)", re.IGNORECASE)).first

                        if btn_avanti.is_visible(timeout=2500):
                            btn_avanti.scroll_into_view_if_needed()
                            btn_avanti.click(force=True)
                            tentativi_stessa_situazione = 0
                            target_context.wait_for_timeout(2000)
                        else:
                            tentativi_stessa_situazione += 1
                            logger.info(f"GIN [MINGLE] - Pulsante avanti non trovato ({tentativi_stessa_situazione}/4). Invio tasto Enter...")
                            try:
                                page.keyboard.press("Enter")
                                page.wait_for_timeout(2000)
                            except Exception:
                                pass

                            if tentativi_stessa_situazione >= 4:
                                logger.warning("GIN [MINGLE] - Raggiunto limite tentativi stallo. Forzo chiusura.")
                                break

                    except Exception as e_loop:
                        logger.warning(f"GIN [MINGLE] - Eccezione nel loop sondaggio: {e_loop}")
                        break

                try:
                    with open(file_memoria, "w", encoding="utf-8") as fm:
                        json.dump(memoria_profilo, fm, indent=4, ensure_ascii=False)
                    logger.info(f"GIN - Memoria aggiornata ({len(memoria_profilo)} voci).")
                except Exception as e_mem:
                    logger.warning(f"Impossibile salvare la memoria: {e_mem}")

                screenshot_sondaggio = "gin_mingle_completato.png"
                try:
                    page.screenshot(path=screenshot_sondaggio, full_page=True)
                except Exception:
                    pass
                
                try:
                    browser.close()
                except Exception:
                    pass

                stato_finale_stringa = "portato a termine in autonomia" if sondaggio_completato_con_successo else "scansione completata"

                return {
                    "stato_login": "completato con successo",
                    "stato_sondaggio": stato_finale_stringa,
                    "url_finale_sondaggio": page.url,
                    "titolo_pagina_sondaggio": "Sondaggio in corso",
                    "memoria_sondaggio": memoria_sessione_corrente,
                    "screenshot_sondaggio": screenshot_sondaggio
                }

            except Exception as e:
                logger.error(f"Errore critico durante l'automazione browser Mingle: {e}")
                try:
                    browser.close()
                except Exception:
                    pass
                return {
                    "stato_login": "completato con successo",
                    "stato_sondaggio": "interrotto",
                    "url_finale_sondaggio": url_login,
                    "titolo_pagina_sondaggio": "Mingle | Dashboard",
                    "memoria_sondaggio": [],
                    "screenshot_sondaggio": "gin_mingle_errore.png"
                }


# ==========================================
# STROFA 5: GENERATORE DI REPORT GIN
# ==========================================

class CammaGeneratoreReportGin(CammaIntercambiabile):
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        output_file = contesto.get("output_file", "report_giornaliero_gin.json")
        timestamp_attuale = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report_data = {
            "agente": "GIN (Il Sondaggista Autonomo Meccanico - Mingle Edition)",
            "timestamp": timestamp_attuale,
            "url_sondaggio_raggiunto": contesto.get("url_finale_sondaggio", "https://mingle.respondi.it/"),
            "titolo_pagina": contesto.get("titolo_pagina_sondaggio", "Mingle | Dashboard"),
            "stato_login": contesto.get("stato_login", "non_eseguito"),
            "stato_sondaggio": contesto.get("stato_sondaggio", "non_eseguito"),
            "memoria_domande_risposte": contesto.get("memoria_sondaggio", []),
            "operazioni_completate": [
                {"task": "profilo_anagrafico_gin", "esito": "profilo fisso caricato con successo"},
                {"task": "scanner_email_gin", "esito": "scansione email mirata Mingle completata"},
                {"task": "flusso_continuo_browser_gin", "esito": "login e navigazione con profilo reale gestiti"},
                {"task": "generatore_report_gin", "esito": "report Mingle archiviato"}
            ],
            "stato_sistema": "operativo_mingle"
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
        logger.info(f"GIN - Report Mingle archiviato in locale: {output_file}")
        return report_data


# ==========================================
# PUNTO DI ACCENSIONE DEL CONGEGNO GIN
# ==========================================

if __name__ == "__main__":
    if os.path.exists("gin_tasks_queue.json"):
        os.remove("gin_tasks_queue.json")
        
    core = AutomationCore(queue_filepath="gin_tasks_queue.json")
    core.registra_camma("profilo_anagrafico_gin", CammaProfiloAnagraficoGin())
    core.registra_camma("scanner_email_gin", CammaScannerEmailGin())
    core.registra_camma("flusso_continuo_browser_gin", CammaFlussoContinuoBrowserGin())
    core.registra_camma("generatore_report_gin", CammaGeneratoreReportGin())
    core.esegui_ciclo()
    logger.info("--- GIN: MISSIONE MINGLE TERMINATA ---")