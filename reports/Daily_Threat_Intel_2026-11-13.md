# Daily Threat Intel Report
**Date:** November 13, 2026

🟠 **Threat Score:** 73/100
*(Auditable Metrics - Threat Capability: 6/10 | Event Frequency: 8/10 | Business Impact: 8/10)*

**Executive Summary - Incidents:**
1. Incident Title : North Korean APT38 FaceStealer Campaign Targeting Financial and Crypto Sectors (November 13, 2026)
2. Incident Title : Exploitation of PHP2Shell and Gaia OS Zero-Day in Check Point Security Gateways (November 13, 2026)

---

*(Auditable Metrics - Threat Capability: 6/10 | Event Frequency: 8/10 | Business Impact: 8/10)*

---

## Incident Title : North Korean APT38 FaceStealer Campaign Targeting Financial and Crypto Sectors (November 13, 2026)

**Incident Metadata:**
- **Primary Category:** DATA LEAK
- **News Nature:** Post-mortem / Law Enforcement Action
- **Timeline:** [Incident Date: Last 18 months | Source Publication Date: 2026-11-13]
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** Unknown
- **List of Companies Impacted:** Binance (funds stolen), various Web3 and crypto firms

The FBI has confirmed that North Korean threat actors (APT38) utilized a sophisticated social engineering scheme codenamed "FaceStealer" to conduct fraudulent video calls, resulting in the theft of over $400 million in cryptocurrency. The attackers leveraged stolen webcam footage of previous victims to deceive employees at financial and crypto institutions.

**Overview**
The campaign, active for the past 18 months, involved the use of deepfake-style video manipulation and stolen identity assets to bypass standard verification processes during recruitment and business meetings. The U.S. government has seized infrastructure associated with this scheme, which also targeted Binance, leading to significant financial losses.

**The Breach Mechanism**
- **FaceStealer Social Engineering:** Attackers used high-quality stolen webcam clips of real individuals to impersonate legitimate job seekers or partners during video calls.
- **Credential and Asset Theft:** By establishing trust through these fraudulent calls, the actors gained access to internal systems and crypto-wallets, facilitating the unauthorized transfer of funds.

**Impact and Consequences**
- **Financial Loss:** Over $400 million in cryptocurrency stolen from various entities, including Binance.
- **Operational Compromise:** The use of fabricated personas allowed attackers to reach the onboarding stage at multiple organizations, exposing sensitive data such as Social Security numbers.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Implement mandatory "live-action" verification protocols for all remote hiring and high-value financial transactions.
- **II. Identity & Access Management (Containment):** Enforce hardware-based MFA and prohibit the use of session tokens that can be phished via device code flows.
- **III. Infrastructure Intelligence (Detection):** Deploy AI-based behavioral analysis to detect anomalies in video call patterns and identity verification workflows.
- **IV. Operational Resilience:** Conduct regular audits of third-party hiring platforms and data sharing practices to prevent unauthorized access to PII.
- **V. Simulation environment:** Run red-team exercises simulating deepfake-based social engineering to train staff on identifying synthetic media.

**Conclusion**
The FaceStealer campaign highlights the critical risk posed by AI-enhanced social engineering in the financial sector. Organizations must move beyond traditional identity verification to include robust, real-time authentication measures.

**Further Reading**
[FBI Warning on FaceStealer Scheme](https://thehackernews.com/2026/11/fbi-says-north-korean-hackers-stole.html)

**Footnotes**
[1. https://thehackernews.com/2026/11/fbi-says-north-korean-hackers-stole.html]
[2. https://cyberscoop.com/us-seizes-north-korea-hacking-infrastructure-binance/]

---

## Incident Title : Exploitation of PHP2Shell and Gaia OS Zero-Day in Check Point Security Gateways (November 13, 2026)

**Incident Metadata:**
- **Primary Category:** CLOUD
- **News Nature:** New Attack
- **Timeline:** [Incident Date: October 30, 2026 | Source Publication Date: 2026-11-13]
- **Impacted Country:** Israel (primary), Global
- **Geolocation / Cloud Region:** On-premise and Cloud Gateways
- **List of Companies Impacted:** Check Point customers

Unknown threat actors have been actively exploiting a combination of PHP2Shell vulnerabilities and a previously unreported local privilege escalation flaw in Gaia OS to compromise Check Point Security Gateways.

**Overview**
The attack, which began on October 30, 2026, allows unauthenticated attackers to gain root access to security gateways. Once inside, the attackers deployed a backdoor named TSGA and data-wiping malware targeting VMware ESXi hosts.

**The Breach Mechanism**
- **Initial Access:** Exploitation of PHP2Shell vulnerabilities in unpatched Check Point Security Gateways.
- **Privilege Escalation:** Use of a zero-day flaw in Gaia OS to elevate privileges to root, establishing persistence.

**Impact and Consequences**
- **System Integrity:** Deployment of the TSGA backdoor and destructive data-wiping malware on ESXi infrastructure.
- **Security Infrastructure Compromise:** The gateways, intended to protect the network, were turned into entry points for further lateral movement.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Immediate application of emergency hotfixes provided by Check Point.
- **II. Identity & Access Management (Containment):** Restrict administrative access to gateways to known, secure management subnets only.
- **III. Infrastructure Intelligence (Detection):** Monitor for unauthorized file modifications on ESXi hosts and unusual outbound traffic from security appliances.
- **IV. Operational Resilience:** Ensure offline backups of all critical virtual machine configurations are maintained.
- **V. Simulation environment:** Test the impact of gateway compromise on internal network segmentation.

**Conclusion**
The compromise of security appliances underscores the danger of unpatched edge infrastructure. Rapid patching and strict access control are essential to prevent the weaponization of security tools.

**Further Reading**
[Check Point Security Advisory](https://www.bleepingcomputer.com/news/security/check-point-gateways-hacked-via-php2shell-to-deploy-vmware-esxi-wiper/)

**Footnotes**
[1. https://www.bleepingcomputer.com/news/security/check-point-gateways-hacked-via-php2shell-to-deploy-vmware-esxi-wiper/]
[2. https://www.securityweek.com/php2shell-exploited-in-destructive-check-point-gateway-attacks/]