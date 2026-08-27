from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Support Copilot", layout="wide")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from support_copilot.brief import generate_brief
from support_copilot.config import get_settings
from support_copilot.data_store import load_accounts
from support_copilot.triage import triage

get_settings.cache_clear()

st.title("Support Copilot")
st.caption("Ticket triage for support engineers · account briefs for TAMs. Synthetic demo data only.")

triage_tab, brief_tab = st.tabs(["Ticket triage", "TAM account brief"])

with triage_tab:
    st.subheader("Incoming ticket")
    subject = st.text_input("Subject")
    body = st.text_area("Body", height=180)
    stream = st.checkbox("Stream model output")
    if st.button("Triage ticket", type="primary"):
        if not subject.strip() and not body.strip():
            st.warning("Enter a subject or body.")
        else:
            stream_box = st.empty()
            buf: list[str] = []

            def on_token(token: str) -> None:
                buf.append(token)
                stream_box.code("".join(buf), language="json")

            with st.spinner("Triaging…"):
                result = triage(
                    {"subject": subject, "body": body},
                    on_token=on_token if stream else None,
                )
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Product", result.product)
            c2.metric("Category", result.category)
            c3.metric("Urgency", result.urgency)
            c4.metric("Team", result.responder_team)
            if result.product_area:
                st.write(f"**Product area:** {result.product_area}")
            st.write("**Why this routing**")
            st.write(result.reasoning)
            st.write("**Draft first response**")
            st.info(result.first_response)
            st.write("**Knowledge base**")
            if not result.knowledge_matches:
                st.write("No matching article.")
            for match in result.knowledge_matches:
                with st.expander(f"{match.heading} · {match.path}"):
                    st.write(match.snippet)

with brief_tab:
    st.subheader("Account")
    accounts = load_accounts()
    labels = [f"{item['account_id']} · {item['company']} · {item['health_status']}" for item in accounts]
    choice = st.selectbox("Choose an account", labels)
    account_id = choice.split(" · ", 1)[0]
    if st.button("Generate brief", type="primary"):
        with st.spinner("Writing brief…"):
            brief = generate_brief(account_id)
        st.write(f"**{brief.company}** (`{brief.account_id}`)")
        st.write("**Executive summary**")
        st.write(brief.executive_summary)
        st.write("**Open risks**")
        if not brief.open_risks:
            st.write("No quote-backed risk flags.")
        for flag in brief.open_risks:
            st.markdown(f"- **{flag.label}** ({flag.source}): _{flag.quote}_")
        st.write("**Talking points**")
        for point in brief.talking_points:
            st.markdown(f"- {point}")
