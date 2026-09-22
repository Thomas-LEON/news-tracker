# Methodology: Threat Intelligence Scoring Framework

## 1. Executive Summary

To counter information overload and prioritize critical cyber incidents, our automated Threat Intelligence pipeline utilizes a quantitative scoring model. This methodology is loosely inspired by the **CRQ (Cyber Risk Quantification)** and **FAIR (Factor Analysis of Information Risk)** frameworks. 

Rather than relying on arbitrary severity labels (Low, Medium, High), the system calculates a determinist **Threat Score out of 100**, based on three auditable metrics independently evaluated by the AI engine.

> [!IMPORTANT]
> **Point of Attention: The Role of AI in Scoring**
> The extraction and initial evaluation of the three core metrics (TC, EF, BI) are performed autonomously by a Large Language Model (Google Gemini). While the final mathematical score is deterministic and hardcoded in Python, the qualitative assessment of *how sophisticated* an attack is relies on the AI's reasoning. This is why the metrics are displayed transparently in every report: to allow human analysts to audit, challenge, and adjust the AI's assessment if necessary.

## 2. The Three Auditable Metrics

For each daily briefing, the AI engine evaluates the most critical incident of the past 24 hours against three specific criteria. Each criterion is scored on a scale from 1 to 10.

### A. Threat Capability (TC)
Measures the sophistication, resources, and execution capability of the threat actor.
- **1-3:** Known and patched vulnerabilities / Basic automated attacks (e.g., generic scanning, mass phishing).
- **4-7:** Sophisticated attacks requiring human action (e.g., highly targeted social engineering leading to a confirmed breach, complex exploit chains).
- **8-10:** Critical, actively exploited Zero-Days, Zero-click vulnerabilities, or Nation-State level attacks.

### B. Event Frequency (EF)
Measures the relevance and probability of the threat targeting our specific sector (Banking/Finance) or our core technological stack (Cloud/AI).
- **1-3:** Does not target the financial sector or enterprise IT environments (e.g., gaming company breach, local hospital ransomware).
- **4-7:** Opportunistic global campaigns (e.g., widespread ransomware or supply chain attacks where our organization *could* be collateral damage).
- **8-10:** Direct targeting of the financial sector or critical enterprise Cloud/AI infrastructure.

### C. Business Impact (BI)
Measures the potential financial, operational, and regulatory damage if the attack were to succeed against our infrastructure.
- **1-3:** Negligible impact, minor service disruption with no data loss.
- **4-7:** Prolonged downtime, non-critical data exfiltration, or contained lateral movement.
- **8-10:** Systemic global risk, massive financial data theft, severe operational paralysis, or critical regulatory exposure (GDPR / DORA).

## 3. Mandatory Escalation Rule: Financial Sector

To ensure our defensive posture aligns with our core business, the engine enforces a strict mathematical floor for any incident involving a direct breach of a financial institution (banks, fintechs, payment processors, etc.). 

If a financial entity suffers a confirmed breach involving customer data, the AI **must** enforce the following minimums:
- **Event Frequency (EF) ≥ 8** (The financial sector is the direct target).
- **Business Impact (BI) ≥ 8** (Financial data theft automatically triggers major GDPR/DORA regulatory exposure).
- **Threat Capability (TC) ≥ 5** (Successfully breaching a modern financial institution requires above-average capability).

*Note: This guarantees a minimum Threat Score of 69/100 for any peer-organization breach.*

## 4. Mathematical Calculation & Alert Levels

The three metrics are extracted by the Python pipeline, which mathematically calculates the final Threat Score using a deterministic formula to cap the value at 100.

**Formula:**
`Threat Score = MIN( INT((TC + EF + BI) * 3.33) , 100 )`

The final score defines the daily alert level:
- 🟢 **0 - 50 (Green):** Normal daily background noise. Standard vigilance.
- 🟠 **51 - 75 (Orange):** Elevated threat landscape. Relevant campaigns or peer breaches detected. Review proposed mitigating controls.
- 🔴 **76 - 100 (Red):** Critical / Systemic threat. Immediate review by the SOC/CERT is required. (e.g., Actively exploited zero-day in core infrastructure).

## 5. Auditability

Because the AI model outputs the raw `TC`, `EF`, and `BI` values before the Python script calculates the final score, every Threat Score is fully auditable. The pipeline intentionally prints the breakdown (e.g., `Threat Capability: 5/10 | Event Frequency: 8/10 | Business Impact: 8/10`) to allow CTI analysts to challenge or manually adjust the AI's assessment if necessary.
