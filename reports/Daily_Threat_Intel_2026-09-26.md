# Daily Threat Intel Report
**Date:** September 26, 2026

🟠 **Threat Score:** 73/100
*(Auditable Metrics - Threat Capability: 6/10 | Event Frequency: 8/10 | Business Impact: 8/10)*

**Executive Summary - Incidents:**
1. Incident Title: Bitget Cryptocurrency Exchange Backend Compromise and $351.6M Theft (September 24, 2026)
2. Incident Title: Salesforce Agentforce 'SalesBleed' Vulnerabilities and Zero-Click Data Exfiltration (September 25, 2026)

---

*(Auditable Metrics - Threat Capability: 6/10 | Event Frequency: 8/10 | Business Impact: 8/10)*

---

## Incident Title: Bitget Cryptocurrency Exchange Backend Compromise and $351.6M Theft (September 24, 2026)

**Incident Metadata:**
- **Primary Category:** CRYPTO THEFT
- **News Nature:** New Attack
- **Timeline:** [Incident Date: September 24, 2026 | Source Publication Date: September 25, 2026]
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** Unknown
- **List of Companies Impacted:** Bitget

Bitget, a major cryptocurrency exchange, confirmed a significant security breach on September 24, 2026, resulting in the unauthorized transfer of $351.6 million from its hot and warm wallets.

**Overview**
On September 24, 2026, at 18:31 UTC, Bitget security systems detected unauthorized transfers. The incident involved a backend compromise that allowed threat actors to access hot and warm wallets. Suspected North Korean threat actors are believed to be behind the operation, which represents one of the largest crypto thefts of the year.

**The Breach Mechanism**
- **Backend Compromise:** Attackers gained unauthorized access to the exchange's backend infrastructure, bypassing security controls protecting hot and warm wallet keys.
- **Unauthorized Transfers:** Once access was established, the threat actors executed automated transfers of assets to external addresses.

**Impact and Consequences**
- **Financial Loss:** A total of $351.6 million in assets was stolen from the platform.
- **Operational Disruption:** The exchange was forced to identify and freeze specific wallet addresses to mitigate further losses, impacting platform liquidity and user trust.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Implement strict multi-signature requirements for all wallet transactions, ensuring no single backend compromise can authorize large-scale transfers.
- **II. Identity & Access Management (Containment):** Enforce hardware-based MFA for all administrative access to backend wallet management systems.
- **III. Infrastructure Intelligence (Detection):** Deploy real-time anomaly detection for wallet outflow patterns, triggering automatic circuit breakers upon detection of unauthorized volume.
- **IV. Operational Resilience:** Maintain a high ratio of cold storage assets to minimize the impact of hot wallet compromises.
- **V. Simulation environment:** Conduct regular red-team exercises simulating backend infrastructure compromise to test incident response and asset freezing capabilities.

**Conclusion**
This incident highlights the extreme risk posed by sophisticated threat actors targeting the financial infrastructure of crypto exchanges. The scale of the theft underscores the necessity of robust, multi-layered security for hot wallet management.

**Further Reading**
[1. https://www.securityweek.com/north-korea-suspected-in-351-million-bitget-crypto-heist/]
[2. https://techcrunch.com/2026/09/25/north-korean-hackers-suspected-in-351m-crypto-theft-the-largest-so-far-this-year/]

---

## Incident Title: Salesforce Agentforce 'SalesBleed' Vulnerabilities and Zero-Click Data Exfiltration (September 25, 2026)

**Incident Metadata:**
- **Primary Category:** AI
- **News Nature:** New Attack
- **Timeline:** [Incident Date: September 2026 | Source Publication Date: September 25, 2026]
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** Unknown
- **List of Companies Impacted:** Salesforce

A set of vulnerabilities collectively dubbed 'SalesBleed' in Salesforce's Agentforce platform allowed attackers to hijack trusted AI agents, leading to zero-click data exfiltration and phishing attacks.

**Overview**
Researchers identified three vulnerabilities in Salesforce Agentforce that enabled attackers to manipulate AI agents. By leveraging prompt injection and DNS exfiltration, attackers could smuggle arbitrary instructions across applications, effectively bypassing security boundaries within the CRM environment.

**The Breach Mechanism**
- **Prompt Injection:** Attackers injected malicious instructions into the AI agent's context, forcing it to perform unauthorized actions.
- **DNS Exfiltration:** The agents were manipulated to exfiltrate sensitive CRM data via DNS queries, bypassing standard network egress filtering.

**Impact and Consequences**
- **Data Exfiltration:** Unauthorized access to sensitive CRM data, posing a significant risk to customer privacy and regulatory compliance.
- **Phishing Escalation:** Hijacked agents were used to launch highly credible phishing attacks within trusted internal communication channels like Slack.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Implement strict input validation and sanitization for all data processed by AI agents.
- **II. Identity & Access Management (Containment):** Apply the principle of least privilege to AI agent identities, restricting their ability to access external communication channels.
- **III. Infrastructure Intelligence (Detection):** Monitor AI agent behavior for anomalous patterns, such as unexpected DNS requests or unauthorized cross-app communication.
- **IV. Operational Resilience:** Establish a kill-switch mechanism to immediately disable AI agents exhibiting suspicious behavior.
- **V. Simulation environment:** Perform regular adversarial testing (red-teaming) specifically targeting prompt injection and agentic workflow manipulation.

**Conclusion**
The 'SalesBleed' incident demonstrates that AI agents, while powerful, introduce new attack vectors that require specialized security controls beyond traditional application security.

**Further Reading**
[1. https://www.securityweek.com/salesbleed-flaws-in-salesforce-agentforce-enabled-zero-click-data-exfiltration/]
[2. https://www.infosecurity-magazine.com/news/vulnerabilities-salesforce-ai/]