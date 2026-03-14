import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv
import datetime

load_dotenv()

API_KEY     = os.environ.get("PANDADOC_API_KEY")
TEMPLATE_ID = os.environ.get("PANDADOC_TEMPLATE_ID")

HEADERS = {
    "Authorization": f"API-Key {API_KEY}",
    "Content-Type": "application/json",
}

# ── VALEURS FIXES ──
CREANCIER_NOM      = "Sendinblue SAS"
CREANCIER_ADRESSE  = "17 rue Salneuve, 75017 Paris"
SIGNATAIRE_PRENOM  = "Amal"
SIGNATAIRE_NOM     = "Habacha"
SIGNATAIRE_QUALITE = "Sales Admin Manager"
SIGNATAIRE_EMAIL   = "amal.habacha@brevo.com"
FAIT_A             = "Paris"

# ── MISE EN PAGE ──
st.set_page_config(page_title="Déclaration de Créances", page_icon="📄", layout="centered")

st.title("📄 Déclaration de Créances")
st.markdown("Ce formulaire vous guide pas à pas pour remplir la déclaration de créances. Les champs marqués d'un **\\*** sont obligatoires.")
st.markdown("---")

# ── SECTION 1 : CRÉANCIER (automatique) ──
st.markdown("### 1. Créancier")
st.info(f"✅ Rempli automatiquement : **{CREANCIER_NOM}** — {CREANCIER_ADRESSE}")

# ── SECTION 2 : MANDATAIRE ──
st.markdown("### 2. Mandataire du créancier")
st.caption("👉 Le mandataire est la personne ou le cabinet qui représente le créancier (ex: un avocat). Si vous n'avez pas de mandataire, laissez ces champs vides.")

mandataire_nom        = st.text_input("Nom du mandataire", placeholder="ex: Cabinet Dupont Avocats")
mandataire_qualite    = st.text_input("Qualité du mandataire", placeholder="ex: Avocat au Barreau de Paris")
mandataire_adresse    = st.text_area("Adresse du mandataire", placeholder="ex: 1 avenue de l'Opéra, 75001 Paris", height=80)
mandataire_references = st.text_input("Références du mandataire", placeholder="ex: Dossier n° 2026-042")

# ── SECTION 3 : DÉBITEUR ──
st.markdown("### 3. Débiteur")
st.caption("👉 Le débiteur est la société ou la personne qui vous doit de l'argent et qui fait l'objet d'une procédure collective (redressement, liquidation...).")

debiteur_nom     = st.text_input("Nom / Dénomination sociale *", placeholder="ex: Société XYZ SAS")
debiteur_adresse = st.text_area("Adresse / Siège social *", placeholder="ex: 12 rue de la Paix, 75001 Paris", height=80)
debiteur_rcs     = st.text_input("N° RCS ou RM", placeholder="ex: RCS Paris 123 456 789")

# ── SECTION 4 : PROCÉDURE ──
st.markdown("### 4. Procédure")
st.caption("👉 Indiquez la nature de la procédure judiciaire ouverte contre le débiteur ainsi que la date du jugement d'ouverture. Ces informations figurent sur le courrier reçu du tribunal.")

nature_jugement = st.selectbox(
    "Nature du jugement *",
    ["Redressement judiciaire", "Liquidation judiciaire", "Sauvegarde", "Sauvegarde accélérée"]
)
date_jugement = st.date_input("Date du jugement *", value=datetime.date.today(), format="DD/MM/YYYY")

# ── SECTION 5 : CRÉANCE DÉCLARÉE ──
st.markdown("### 5. Créance déclarée")
st.caption("👉 Indiquez les montants que le débiteur vous doit. La créance chirographaire est une créance ordinaire sans garantie. La créance privilégiée bénéficie d'une garantie (ex: nantissement, privilège fournisseur).")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Créance chirographaire (sans garantie)**")
    chiro_echu      = st.number_input("Montant échu (€)", min_value=0.0, step=0.01, format="%.2f", key="ce", help="Montant déjà dû à ce jour")
    chiro_a_echoir  = st.number_input("Montant à échoir (€)", min_value=0.0, step=0.01, format="%.2f", key="ca", help="Montant qui sera dû dans le futur")
    chiro_total     = chiro_echu + chiro_a_echoir
    st.metric("Total chirographaire", f"{chiro_total:,.2f} €")

with col2:
    st.markdown("**Créance privilégiée (avec garantie)**")
    priv_echu       = st.number_input("Montant échu (€)", min_value=0.0, step=0.01, format="%.2f", key="pe", help="Montant déjà dû à ce jour")
    priv_a_echoir   = st.number_input("Montant à échoir (€)", min_value=0.0, step=0.01, format="%.2f", key="pa", help="Montant qui sera dû dans le futur")
    priv_total      = priv_echu + priv_a_echoir
    st.metric("Total privilégié", f"{priv_total:,.2f} €")

montant_total = chiro_total + priv_total
st.success(f"💰 **Montant total de la créance : {montant_total:,.2f} €**")

# ── SECTION 6 : SIGNATURE ──
st.markdown("### 6. Signature")
st.caption("👉 Indiquez la date à laquelle vous déclarez cette créance. Le lieu et le signataire sont fixes.")

date_signature = st.date_input("Date de signature *", value=datetime.date.today(), format="DD/MM/YYYY")
st.info(f"✅ Fait à **{FAIT_A}**, signé par **{SIGNATAIRE_PRENOM} {SIGNATAIRE_NOM}** ({SIGNATAIRE_QUALITE})")

# ── VALIDATION ──
st.markdown("---")
champs_obligatoires_manquants = not debiteur_nom.strip() or not debiteur_adresse.strip()

if champs_obligatoires_manquants:
    st.warning("⚠️ Veuillez remplir au minimum le nom et l'adresse du débiteur.")

envoyer = st.button("📤 Générer et envoyer pour signature", disabled=champs_obligatoires_manquants, use_container_width=True)

if envoyer:
    def fmt(v): return f"{v:,.2f} EUR".replace(",", " ").replace(".", ",")

    payload = {
        "name": f"Declaration de creances - {debiteur_nom} - {date_signature.strftime('%d/%m/%Y')}",
        "template_uuid": TEMPLATE_ID,
        "recipients": [
            {
                "email":      SIGNATAIRE_EMAIL,
                "first_name": SIGNATAIRE_PRENOM,
                "last_name":  SIGNATAIRE_NOM,
                "role":       "Manager"
            }
        ],
        "tokens": [
            {"name": "Creancier.Nom",              "value": CREANCIER_NOM},
            {"name": "Creancier.Adresse",           "value": CREANCIER_ADRESSE},
            {"name": "Mandataire.Nom",              "value": mandataire_nom},
            {"name": "Mandataire.Qualite",          "value": mandataire_qualite},
            {"name": "Mandataire.Adresse",          "value": mandataire_adresse.replace("\n", " ")},
            {"name": "Mandataire.References",       "value": mandataire_references},
            {"name": "Debiteur.Nom",                "value": debiteur_nom},
            {"name": "Debiteur.Adresse",            "value": debiteur_adresse.replace("\n", " ")},
            {"name": "Debiteur.RCS",                "value": debiteur_rcs},
            {"name": "Procedure.Nature",            "value": nature_jugement},
            {"name": "Procedure.DateJugement",      "value": date_jugement.strftime("%d/%m/%Y")},
            {"name": "Creance.ChiroEchu",           "value": fmt(chiro_echu)},
            {"name": "Creance.ChiroAEchoir",        "value": fmt(chiro_a_echoir)},
            {"name": "Creance.ChiroTotal",          "value": fmt(chiro_total)},
            {"name": "Creance.PrivEchu",            "value": fmt(priv_echu)},
            {"name": "Creance.PrivAEchoir",         "value": fmt(priv_a_echoir)},
            {"name": "Creance.PrivTotal",           "value": fmt(priv_total)},
            {"name": "Creance.MontantTotal",        "value": fmt(montant_total)},
            {"name": "Creance.PhraseFinaleMontant", "value": fmt(montant_total)},
            {"name": "Signature.FaitA",             "value": FAIT_A},
            {"name": "Signature.Date",              "value": date_signature.strftime("%d/%m/%Y")},
            {"name": "Signataire.NomComplet",       "value": f"{SIGNATAIRE_PRENOM} {SIGNATAIRE_NOM}"},
            {"name": "Signataire.Qualite",          "value": SIGNATAIRE_QUALITE},
        ]
    }

    with st.spinner("⏳ Création et envoi du document en cours..."):
        try:
            r = requests.post(
                "https://api.pandadoc.com/public/v1/documents",
                headers=HEADERS, json=payload
            )
            r.raise_for_status()
            doc_id = r.json()["id"]

            for _ in range(30):
                s = requests.get(
                    f"https://api.pandadoc.com/public/v1/documents/{doc_id}",
                    headers=HEADERS
                )
                if s.json().get("status") == "document.draft":
                    break
                time.sleep(2)

            requests.post(
                f"https://api.pandadoc.com/public/v1/documents/{doc_id}/send",
                headers=HEADERS,
                json={
                    "subject": "Action requise — Déclaration de créances à signer",
                    "message": "Veuillez trouver ci-joint la déclaration de créances à signer."
                }
            )

            st.success(f"✅ Document envoyé à {SIGNATAIRE_EMAIL} pour signature !")
            st.markdown(f"🔗 [Voir dans PandaDoc](https://app.pandadoc.com/a/#/documents/{doc_id})")

        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")
