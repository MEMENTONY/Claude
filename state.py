# state.py - auto-extracted from streamlit_app.py (behavior-preserving)
import json
import html
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from config import *

def _json_safe(v):
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, dict):
        return {str(k): _json_safe(val) for k, val in v.items()}
    if isinstance(v, (list, tuple)):
        return [_json_safe(x) for x in v]
    return v

def local_state_payload():
    data = {k: _json_safe(st.session_state.get(k)) for k in PERSIST_KEYS if k in st.session_state}
    data["_saved_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return data

def load_local_state():
    if st.session_state.get("_local_state_loaded"):
        return
    st.session_state["_local_state_loaded"] = True
    if not os.path.exists(LOCAL_STATE_PATH):
        st.session_state["_local_state_status"] = "empty"
        return
    try:
        with open(LOCAL_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            st.session_state["_local_state_status"] = "invalid"
            return
        for k in PERSIST_KEYS:
            if k in data:
                st.session_state[k] = data[k]
        st.session_state["_local_state_status"] = "loaded"
        st.session_state["_local_state_saved_at"] = data.get("_saved_at", "")
    except Exception as e:
        st.session_state["_local_state_status"] = f"load_error: {e}"

def save_local_state():
    try:
        data = local_state_payload()
        tmp_path = LOCAL_STATE_PATH + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, LOCAL_STATE_PATH)
        st.session_state["_local_state_status"] = "saved"
        st.session_state["_local_state_saved_at"] = data.get("_saved_at", "")
    except Exception as e:
        st.session_state["_local_state_status"] = f"save_error: {e}"

__all__ = [
    '_json_safe',
    'load_local_state',
    'local_state_payload',
    'save_local_state',
]
