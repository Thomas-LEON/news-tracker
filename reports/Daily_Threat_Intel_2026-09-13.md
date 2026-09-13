# Daily Threat Intel Report
**Date:** September 13, 2026

🟠 **Threat Score:** 59/100
*(Auditable Metrics - Threat Capability: 5/10 | Event Frequency: 6/10 | Business Impact: 7/10)*

**Executive Summary - Incidents:**
1. Titre de l'incident : Revolut Customer Data Breach via Fraudulent Government Requests (September 12, 2026)
2. Titre de l'incident : Microsoft Cloud Account Hijacking via Passkey Phishing Campaigns (August 3-5, 2026)

---

*(Auditable Metrics - Threat Capability: 5/10 | Event Frequency: 6/10 | Business Impact: 7/10)*

---

## Titre de l'incident : Revolut Customer Data Breach via Fraudulent Government Requests (September 12, 2026)

**Incident Metadata:**
- **Primary Category:** DATA LEAK
- **News Nature:** Nouvelle attaque
- **Timeline:** [Incident Date: September 12, 2026 | Source Publication Date: September 12, 2026]
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** Unknown
- **List of Companies Impacted:** Revolut

Revolut has officially confirmed a data breach affecting its customer base, resulting from threat actors successfully masquerading as government agencies to solicit sensitive information. This incident highlights a critical failure in the verification process for external data requests.

**Overview**
On September 12, 2026, the financial technology firm Revolut disclosed that unauthorized parties gained access to customer data. The breach was facilitated by sophisticated social engineering tactics where attackers impersonated government officials to bypass internal security protocols and obtain regulated customer information.

**The Breach Mechanism**
- **Social Engineering Impersonation:** Attackers utilized highly convincing fraudulent requests, mimicking official government communication channels to deceive internal staff.
- **Verification Protocol Bypass:** The threat actors exploited weaknesses in the validation workflow, allowing them to extract data under the guise of legitimate regulatory or legal inquiries.

**Impact and Consequences**
- **Regulatory Non-Compliance:** Potential exposure to GDPR and financial regulatory penalties due to the unauthorized disclosure of sensitive customer data.
- **Reputational Damage:** Loss of customer trust in the platform's ability to secure personal financial information against social engineering threats.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Implement a mandatory "Out-of-Band" verification process for all incoming government or regulatory data requests.
- **II. Identity & Access Management (Containment):** Restrict access to sensitive customer databases to a limited number of authorized personnel with multi-party approval requirements.
- **III. Infrastructure Intelligence (Detection):** Deploy AI-driven communication analysis tools to detect anomalies in the tone, metadata, and origin of incoming official requests.
- **IV. Operational Resilience:** Conduct mandatory social engineering awareness training specifically focused on "Authority Impersonation" for all staff handling external data requests.
- **V. Simulation environment:** Perform regular Red Team exercises simulating "Fake Legal Request" scenarios to test the robustness of the verification workflow.

**Conclusion**
This incident underscores that even robust technical security can be undermined by human-centric social engineering. Financial institutions must treat external data requests with the same level of scrutiny as direct cyber-attacks.

**Further Reading**
[TechCrunch - Revolut confirms customer data breach](https://techcrunch.com/2026/09/12/revolut-confirms-customer-data-breach-through-fake-government-requests/)

**Footnotes**
[1. https://techcrunch.com/2026/09/12/revolut-confirms-customer-data-breach-through-fake-government-requests/]

---

## Titre de l'incident : Microsoft Cloud Account Hijacking via Passkey Phishing Campaigns (August 3-5, 2026)

**Incident Metadata:**
- **Primary Category:** CLOUD
- **News Nature:** Nouvelle attaque
- **Timeline:** [Incident Date: August 3-5, 2026 | Source Publication Date: September 13, 2026]
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** Microsoft Cloud Infrastructure
- **List of Companies Impacted:** Microsoft

Microsoft has disclosed two major phishing campaigns active between August 3 and 5, 2026, which leveraged passkey-themed social engineering to compromise cloud environments and facilitate financial fraud.

**Overview**
Threat actors targeted Microsoft cloud accounts by sending over a million scam emails. By masquerading as high-level executives (CEOs), the attackers successfully tricked users into interacting with malicious passkey prompts, leading to account hijacking and subsequent data exfiltration.

**The Breach Mechanism**
- **Passkey-Themed Social Engineering:** Attackers utilized the transition to passwordless authentication to confuse users, prompting them to authorize fraudulent passkey requests.
- **Third-Party Infrastructure Abuse:** The campaign leveraged external email delivery services to bypass traditional spam filters and reach corporate inboxes.

**Impact and Consequences**
- **Cloud Environment Compromise:** Unauthorized access to corporate cloud environments, potentially leading to lateral movement and further data exfiltration.
- **Financial Fraud:** The hijacked accounts were used to propagate further financial scam messages, leveraging the trust associated with compromised corporate identities.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Enforce strict Conditional Access policies that require FIDO2-compliant hardware keys for all administrative and high-privilege cloud accounts.
- **II. Identity & Access Management (Containment):** Implement "Number Matching" for all MFA prompts to prevent accidental approval of fraudulent requests.
- **III. Infrastructure Intelligence (Detection):** Monitor for anomalous login patterns originating from unusual geographic locations or non-standard user agents.
- **IV. Operational Resilience:** Update incident response playbooks to include automated account suspension for identities showing signs of mass-phishing propagation.
- **V. Simulation environment:** Conduct phishing simulations specifically targeting the "Passkey/MFA Fatigue" vector to educate employees on modern authentication threats.

**Conclusion**
The shift to passwordless authentication requires a corresponding shift in user education. Attackers are now weaponizing the very tools designed to secure accounts.

**Further Reading**
[The Hacker News - Attackers Use Passkey Phishing](https://thehackernews.com/2026/09/attackers-use-passkey-phishing-to.html)

**Footnotes**
[1. https://thehackernews.com/2026/09/attackers-use-passkey-phishing-to.html]