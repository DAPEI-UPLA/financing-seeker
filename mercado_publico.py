

import os, json, time, re, random, unicodedata
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime, timezone, timedelta
import requests
from dotenv import load_dotenv, find_dotenv

# ========= CONFIG =========
# Palabras clave (se buscan en Nombre + Descripcion)
KWS: List[str] = ["Cursos", "Capacitaciones"]
MATCH_MODE: str = "OR"       # "OR" = cualquiera; "AND" = todas
WHOLE_WORD: bool = False     # True = palabra completa; False = parcial

DEFAULT_ESTADO: Optional[str] = "activas"  # o None si usarás fecha fija
DEFAULT_FECHA: Optional[str] = None        # ddmmaaaa (ej: "04112025")
OUT_JSON: str = "resultado.json"

# Robustez
RATE_LIMIT_MIN_DELAY = 0.5      # seg mínimos entre requests
MAX_RETRIES = 5                 # reintentos por request
CIRCUIT_5XX_THRESHOLD = 6       # pausa si acumulas 6 respuestas 5xx seguidas
CIRCUIT_COOLDOWN_SECS = 60      # duración de la pausa (segundos)
VERBOSE = True
# ==========================

def log(msg: str):
    if VERBOSE:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] {msg}", flush=True)

# Zona horaria Chile (ajuste simple para nov/2025)
CL_TZ = timezone(timedelta(hours=-3))
def hoy_ddmmaaaa() -> str:
    return datetime.now(CL_TZ).strftime("%d%m%Y")

# Carga .env
ENV_PATH = Path(__file__).resolve().parent / ".env"
loaded = False
if ENV_PATH.exists():
    loaded = load_dotenv(dotenv_path=ENV_PATH); log(f".env: {ENV_PATH} -> {'OK' if loaded else 'NO'}")
if not loaded:
    alt = find_dotenv()
    if alt:
        load_dotenv(alt); log(f".env (find): {alt}")
    else:
        log("No se encontró .env; intentaré variables de entorno del sistema.")

TICKET = os.getenv("MP_TICKET")
if not TICKET:
    raise RuntimeError("Falta MP_TICKET (ponlo en .env o en variable de entorno)")

BASE = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (mp-scraper/robusto/1.0; +mailto:tu-email@ejemplo.com)"}
VALID_ESTADOS = {"publicada","cerrada","desierta","adjudicada","revocada","suspendida","activas"}

# --- Control de rate & circuit ---
_last_call_ts = 0.0
_consecutive_5xx = 0

def _rate_limit_sleep():
    global _last_call_ts
    now = time.perf_counter()
    wait = RATE_LIMIT_MIN_DELAY - (now - _last_call_ts)
    if wait > 0:
        time.sleep(wait)
    _last_call_ts = time.perf_counter()

def _maybe_circuit_break():
    global _consecutive_5xx
    if _consecutive_5xx >= CIRCUIT_5XX_THRESHOLD:
        log(f"⚠️ Circuit breaker: {_consecutive_5xx} respuestas 5xx seguidas. Pausando {CIRCUIT_COOLDOWN_SECS}s…")
        time.sleep(CIRCUIT_COOLDOWN_SECS)
        _consecutive_5xx = 0

def _request_with_retries(params: Dict) -> Dict:
    """Hace GET con backoff, maneja 500/429 y respeta rate limit y circuit breaker."""
    global _consecutive_5xx
    last_url = None
    for attempt in range(MAX_RETRIES):
        _maybe_circuit_break()
        try:
            _rate_limit_sleep()
            if attempt == 0:
                log(f"GET params: {params}")
            else:
                log(f"Reintento {attempt}/{MAX_RETRIES-1} params: {params}")

            r = requests.get(BASE, params=params, headers=HEADERS, timeout=60)
            last_url = r.url
            log(f"→ URL: {last_url}")
            r.raise_for_status()
            _consecutive_5xx = 0
            log("Respuesta OK ✅")
            return r.json()

        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            if status and status >= 500:
                _consecutive_5xx += 1
                delay = (2**attempt) + random.uniform(0, 0.5)
                log(f"HTTP {status} | backoff {delay:.2f}s (5xx seguidas: {_consecutive_5xx})")
                time.sleep(delay)
                continue
            if status == 429:
                delay = (2**attempt) + random.uniform(0, 0.5)
                log(f"HTTP 429 (rate limit) | esperando {delay:.2f}s…")
                time.sleep(delay)
                continue
            # 4xx duro distinto de 429: corta
            raise

        except requests.RequestException as e:
            delay = (2**attempt) + random.uniform(0, 0.5)
            log(f"{e.__class__.__name__}: {e} | backoff {delay:.2f}s…")
            time.sleep(delay)

    raise RuntimeError("No se pudo completar la solicitud tras reintentos.")

def build_params(estado: Optional[str], fecha_ddmmaaaa: Optional[str]) -> Dict:
    p = {"ticket": TICKET}
    if estado:
        e = estado.lower()
        if e not in VALID_ESTADOS:
            raise ValueError(f"Estado inválido: {estado}")
        p["estado"] = e
    if fecha_ddmmaaaa:
        if len(fecha_ddmmaaaa) != 8 or not fecha_ddmmaaaa.isdigit():
            raise ValueError("La fecha debe ser ddmmaaaa")
        p["fecha"] = fecha_ddmmaaaa
    return p

def fetch_listado(params: Dict) -> Dict:
    """Trae el listado; si 'activas' falla, cae a 'fecha=hoy'."""
    try:
        t0 = time.perf_counter()
        data = _request_with_retries(params)
        log(f"Listado OK en {time.perf_counter()-t0:.2f}s")
        return data
    except requests.HTTPError:
        if params.get("estado") == "activas":
            alt = dict(params)
            alt.pop("estado", None)
            alt["fecha"] = hoy_ddmmaaaa()
            log(f"Fallback: activas→fecha={alt['fecha']}")
            t0 = time.perf_counter()
            data = _request_with_retries(alt)
            log(f"Listado (fallback) OK en {time.perf_counter()-t0:.2f}s")
            return data
        raise

def normalize_items(resp_json: Dict) -> List[Dict]:
    """Aplana la estructura del listado a una lista de dicts consistente."""
    data: List[Dict] = []
    if not isinstance(resp_json, dict):
        return data
    listado = resp_json.get("Listado") or resp_json.get("listado") or resp_json
    items = listado.get("Licitaciones") if isinstance(listado, dict) else None
    if not items and isinstance(listado, list):
        items = listado
    if not items:
        one = resp_json.get("Licitacion") or resp_json.get("licitacion")
        if one:
            items = [one]
    if not items:
        return data

    for it in items:
        data.append({
            "CodigoExterno": it.get("CodigoExterno"),
            "Estado": it.get("Estado"),
            "Nombre": it.get("Nombre"),
            "Descripcion": it.get("Descripcion"),
            "FechaPublicacion": it.get("FechaPublicacion"),
            "FechaCierre": it.get("FechaCierre"),
            "Comprador": (it.get("Comprador") or {}).get("NombreOrganismo"),
            "CodigoOrganismo": (it.get("Comprador") or {}).get("CodigoOrganismo"),
            "CodigoEstado": it.get("CodigoEstado"),
            "Tipo": it.get("Tipo"),
            "Etapas": it.get("Etapas"),
            "UrlPublica": it.get("UrlPublica") or it.get("UrlBases"),
        })
    return data

def dedupe_by_codigo(items: List[Dict]) -> List[Dict]:
    seen, out = set(), []
    for it in items:
        code = it.get("CodigoExterno")
        if code and code not in seen:
            seen.add(code)
            out.append(it)
    return out

# --- Keywords ---
def _norm(s: Optional[str]) -> str:
    if not s: return ""
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")

def keyword_match(texto: str, kws: List[str], mode="OR", whole_word=False) -> Dict:
    if not kws: return {"matched": True, "hits": []}
    tex = _norm(texto); hits, flags = [], []
    for kw in kws:
        t = _norm(kw)
        ok = (re.search(r"\b"+re.escape(t)+r"\b", tex) is not None) if whole_word else (t in tex)
        hits.append(kw if ok else None); flags.append(ok)
    return {"matched": all(flags) if mode.upper()=="AND" else any(flags),
            "hits":[h for h in hits if h]}

def filtrar_keywords(items: List[Dict], kws: List[str], mode="OR", whole_word=False) -> List[Dict]:
    if not kws: return items
    out = []
    for it in items:
        texto = f"{it.get('Nombre','')} {it.get('Descripcion','')}".strip()
        res = keyword_match(texto, kws, mode, whole_word)
        if res["matched"]:
            it2 = dict(it)
            it2["Coincidencias"] = res["hits"]
            out.append(it2)
    return out

# --- Guardado JSON ---
def save_json(rows: List[Dict], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    log(f"JSON guardado: {path} ({len(rows)} registros)")

# --- Flujo principal ---
def buscar_licitaciones_json(estado: Optional[str], fecha_ddmmaaaa: Optional[str],
                             kws: List[str], mode: str, whole_word: bool, out_json: str) -> List[Dict]:
    params = build_params(estado, fecha_ddmmaaaa)
    log(f"Consulta: estado={estado} fecha={fecha_ddmmaaaa or '(no)'}")
    resp = fetch_listado(params)

    t0 = time.perf_counter()
    items = normalize_items(resp)
    items = dedupe_by_codigo(items)
    log(f"Descargados (dedup): {len(items)} en {time.perf_counter()-t0:.2f}s")

    if kws:
        t1 = time.perf_counter()
        items = filtrar_keywords(items, kws, mode, whole_word)
        log(f"Tras filtro keywords: {len(items)} en {time.perf_counter()-t1:.2f}s")

    save_json(items, out_json)
    return items

if __name__ == "__main__":
    log("=== Inicio ===")
    res = buscar_licitaciones_json(
        estado=DEFAULT_ESTADO,
        fecha_ddmmaaaa=DEFAULT_FECHA,
        kws=KWS,
        mode=MATCH_MODE,
        whole_word=WHOLE_WORD,
        out_json=OUT_JSON
    )
    preview = min(5, len(res))
    if preview:
        log(f"Preview {preview}:")
        for i in range(preview):
            it = res[i]
            nom = (it.get("Nombre") or "")[:120]
            hits = ", ".join(it.get("Coincidencias", [])) if it.get("Coincidencias") else "-"
            print(f"  - [{i+1}] {it.get('CodigoExterno')} | {nom}{'…' if len((it.get('Nombre') or ''))>120 else ''} | hits: {hits}")
    else:
        log("Sin coincidencias.")
    log("=== Fin ===")
