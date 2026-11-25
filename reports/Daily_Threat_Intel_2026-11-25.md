# Daily Threat Intel Report
**Date:** November 25, 2026

🟠 **Threat Score:** 73/100
*(Auditable Metrics - Threat Capability: 6/10 | Event Frequency: 8/10 | Business Impact: 8/10)*

**Executive Summary - Incidents:**
1. Inception Extortion Group Hijacks Financial Sector Cloud Accounts via Large-Scale SSO Vishing Campaign (November 2026)
2. Unsecured Radware Internal API Exposes Customer Cloud Access Keys and Security Configuration (November 2026)
3. AI-Assisted Campaign Compromises Check Point Security Management Servers Across 22 Global Organizations (November 2026)
4. Broadcom Patches Critical Authentication Bypass Flaw (CVE-2026-123903) in VMware vCenter Server Exploited as Zero-Day (November 2026)

---

*(Auditable Metrics - Threat Capability: 6/10 | Event Frequency: 8/10 | Business Impact: 8/10)*

## Inception Extortion Group Hijacks Financial Sector Cloud Accounts via Large-Scale SSO Vishing Campaign (November 2026)

**Incident Metadata:**
- **Primary Category:** CLOUD
- **News Nature:** New Attack
- **Timeline:** Incident Date: August 2026 – November 2026 | Source Publication Date: November 25, 2026
- **Impacted Country:** Global (United States, United Kingdom, Australia)
- **Geolocation / Cloud Region:** Multi-region Cloud Enterprise Environments
- **List of Companies Impacted:** Financial services, healthcare, and legal services institutions (tracked by Palo Alto Networks Unit 42 and Okta)

Palo Alto Networks Unit 42 and Okta Threat Intelligence disclosed a large-scale vishing campaign conducted by the "Inception" threat group (O-UNC-053), targeting financial services firms to hijack Single Sign-On (SSO) credentials and compromise corporate cloud environments in November 2026.¹ ²

**Overview**
The newly identified extortion cluster, linked to former affiliates of the ShinyHunters ecosystem, has aggressively targeted corporate credentials across financial, legal, and healthcare institutions since August 2026. By impersonating IT helpdesk staff over voice phone calls (vishing), threat actors manipulate employees into entering their Single Sign-On (SSO) credentials and approving Multi-Factor Authentication (MFA) prompts. Once inside the cloud infrastructure, the group exfiltrates corporate data and attempts extortion under their new leak site branding, INCEPTION.² ³

**The Breach Mechanism**
- **Voice Phishing (Vishing) Social Engineering**: Threat actors contact enterprise employees via telephone, posing as internal IT administrators or service desk representatives to request credential verification or password resets.
- **Single Sign-On (SSO) Interception**: Attackers direct victims to reverse-proxy phishing portals designed to capture enterprise identity provider credentials and intercept real-time push notifications or one-time passcodes (OTP).
- **Cloud Infrastructure Hijacking**: Armed with valid SSO sessions, the threat actors access corporate cloud platforms (e.g., Okta-managed SaaS applications, cloud storage repositories), executing lateral movement and unauthorized data exfiltration.

**Impact and Consequences**
- **Financial Data Theft and Extortion**: Sensitive corporate communications and regulated financial records were exfiltrated, followed by extortion demands threatening public disclosure.
- **Bypassing Identity Perimeter Controls**: Bypassing traditional MFA via social engineering severely degrades trust boundaries within identity management systems across target organizations.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Establish mandatory out-of-band verification procedures for all helpdesk credential resets and MFA device re-registrations.
- **II. Identity & Access Management (Containment):** Mandate FIDO2/WebAuthn hardware security keys to eliminate vulnerability to real-time proxy and vishing attacks.
- **III. Infrastructure Intelligence (Detection):** Implement behavioral monitoring on Identity Provider (IdP) logs to flag concurrent user sessions initiated from anomalous IP ranges or unmanaged devices.
- **IV. Operational Resilience:** Conduct immediate auditing of cloud service accounts and cross-tenant trust configurations following any suspected identity compromise.
- **V. Simulation environment:** Deploy simulated voice phishing scenarios targeting high-privilege staff to measure and improve organizational resilience against voice-based social engineering.

**Conclusion**
Identity infrastructure remains a primary threat vector; relying solely on push-based MFA leaves organizations vulnerable to sophisticated social engineering unless phishing-resistant authentication mechanisms are strictly enforced.

**Further Reading**
- Palo Alto Networks Unit 42 Advisory on Vishing Campaigns

**Footnotes**
[1] https://thehackernews.com/2026/11/com-affiliated-hackers-hijack-cloud.html
[2] https://thehackernews.com/2026/11/okta-links-shinyhunters-associated.html
[3] https://www.bleepingcomputer.com/news/security/new-inception-extortion-gang-launches-large-scale-vishing-campaign/

---

## Unsecured Radware Internal API Exposes Customer Cloud Access Keys and Security Configuration (November 2026)

**Incident Metadata:**
- **Primary Category:** DATA LEAK
- **News Nature:** Post-mortem
- **Timeline:** Incident Date: November 2026 | Source Publication Date: November 24, 2026
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** Global Cloud Web Application Firewall (WAF) Infrastructure
- **List of Companies Impacted:** Radware, Enterprise Cloud WAF Customers

Cybersecurity vendor Radware disclosed a security breach on November 24, 2026, revealing that an unauthenticated Cloud Web Application Firewall (WAF) management API exposed customer cloud access keys and account details online.¹

**Overview**
Attackers discovered and accessed a publicly exposed internal management API associated with Radware's Cloud WAF service. The security incident allowed unauthorized actors to extract customer metadata, including account details and secret cloud access keys used to integrate and manage cloud web security policies. Because Cloud WAF keys often hold administrative privileges within customer cloud environments, this exposure presents direct third-party supply chain risks to enterprise security boundaries.¹

**The Breach Mechanism**
- **Exposed Management API**: An internal Cloud WAF management API endpoint was inadvertently exposed to the public internet without proper authentication enforcement.
- **Credential and Access Key Harvesting**: Threat actors queried the exposed API endpoints to extract sensitive data, including customer account identifiers and cloud access keys.

**Impact and Consequences**
- **Third-Party Supply Chain Exposure**: Threat actors obtained valid API credentials capable of accessing customer cloud environments or modifying cloud perimeter security controls.
- **Risk of Security Policy Tampering**: Exposed management keys could allow unauthorized modification of WAF filtering rules, enabling attackers to bypass web application defenses.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Deploy External Attack Surface Management (EASM) tools to scan and identify unauthenticated internal APIs exposed to the public internet.
- **II. Identity & Access Management (Containment):** Rotate all cloud access keys and API tokens shared with third-party security management platforms and enforce strict least-privilege scoping.
- **III. Infrastructure Intelligence (Detection):** Enable real-time API monitoring and anomaly detection to identify unauthorized queries against administrative endpoints.
- **IV. Operational Resilience:** Enforce network microsegmentation and strict firewall rules restricting access to internal service management APIs.
- **V. Simulation environment:** Conduct red team exercises simulating compromised third-party cloud keys to test containment timelines.

**Conclusion**
Third-party security integration points represent critical structural risks; administrative management interfaces must be protected by strict authentication and continuous exposure monitoring.

**Further Reading**
- Radware Security Disclosure Statement

**Footnotes**
[1] https://www.bleepingcomputer.com/news/security/radware-discloses-breach-exposing-customer-cloud-access-keys/

---

## AI-Assisted Campaign Compromises Check Point Security Management Servers Across 22 Global Organizations (November 2026)

**Incident Metadata:**
- **Primary Category:** AI
- **News Nature:** New Attack
- **Timeline:** Incident Date: November 2026 | Source Publication Date: November 24, 2026
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** Distributed Enterprise Networks
- **List of Companies Impacted:** Check Point Software Technologies (vendor), 22 impacted organizations across Financial Services, Energy, and Government sectors

Cybersecurity researchers reported on November 24, 2026, that a threat cluster (tracked as GreyNoise GT13) used AI-driven offensive tooling to compromise 24 Check Point Security Management servers across 22 global entities, including financial services organizations.¹ ²

**Overview**
Threat actors deployed automated, AI-assisted reconnaissance and exploitation frameworks operating across nearly 100 IP addresses to target internet-facing Check Point Security Management servers. The automated campaign weaponized vulnerabilities to establish persistence on network management infrastructure across critical sectors. The application of AI offensive tools facilitated rapid payload customization and evasion, escalating operational risks to corporate network security.² ³

**The Breach Mechanism**
- **AI-Driven Offensive Automation**: Attackers deployed AI-assisted scanning and exploit generation tools to identify and target vulnerable Check Point management interfaces concurrently.
- **Vulnerability Chaining**: The campaign exploited multiple security flaws in Check Point Security Management software to achieve administrative remote code execution.
- **Perimeter Security Hijacking**: By compromising central security management platforms, attackers gained direct visibility into network topology and firewall configuration controls.

**Impact and Consequences**
- **Financial and Critical Infrastructure Risk**: Intrusion into central management servers opens internal corporate network segments to lateral movement and data exfiltration.
- **Evasion of Traditional Security Monitoring**: Automated AI orchestration enabled rapid execution cycles that reduced operational response windows for SOC analysts.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Restrict access to administrative security consoles strictly to internal management networks or secure zero-trust access tunnels.
- **II. Identity & Access Management (Containment):** Require multi-factor authentication and strict IP whitelisting for all network security administrative interfaces.
- **III. Infrastructure Intelligence (Detection):** Ingest telemetry from security management servers into SIEM solutions to detect anomalous outbound connections or unauthorized process executions.
- **IV. Operational Resilience:** Apply vendor patches immediately upon release and audit management interface logs against published indicators of compromise (IoCs).
- **V. Simulation environment:** Replicate automated AI exploit payloads in staging environments to baseline security control detection efficacy.

**Conclusion**
Centralized security management platforms represent high-value targets; exposing management planes directly to the internet exposes critical enterprise infrastructure to automated AI exploitation tools.

**Further Reading**
- GreyNoise Threat Intelligence Analysis on GT13

**Footnotes**
[1] https://thehackernews.com/2026/11/hackers-compromise-24-check-point.html
[2] https://www.bleepingcomputer.com/news/security/hackers-compromise-check-point-servers-in-22-organizations/
[3] https://www.securityweek.com/check-point-security-management-servers-hacked-in-ai-assisted-campaign/

---

## Broadcom Patches Critical Authentication Bypass Flaw (CVE-2026-123903) in VMware vCenter Server Exploited as Zero-Day (November 2026)

**Incident Metadata:**
- **Primary Category:** INFRASTRUCTURE
- **News Nature:** Patch Update
- **Timeline:** Incident Date: November 2026 | Source Publication Date: November 24, 2026
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** Enterprise On-Premises & Hybrid Virtualization Infrastructure
- **List of Companies Impacted:** Broadcom, VMware vCenter Server enterprise users

Broadcom issued emergency security patches on November 24, 2026, addressing a critical authentication bypass vulnerability (CVE-2026-123903, CVSS 9.8) in VMware vCenter Server that experienced active zero-day exploitation.¹ ²

**Overview**
The critical flaw resides in VMware vCenter Server. An unauthenticated attacker with network access can exploit the flaw to bypass authentication mechanisms and acquire administrative control over the virtualization management domain. Given the widespread reliance on VMware virtualization across enterprise infrastructure, unpatched instances allow attackers to execute arbitrary code, access virtual machine workloads, or disrupt enterprise operations.¹

**The Breach Mechanism**
- **Authentication Bypass Flaw**: Flaws in session handling allow specially crafted network requests to bypass identity verification protocols.
- **Unauthenticated Administrative Access**: Remote network attackers exploit the authentication bypass to obtain hypervisor administrative privileges without presenting valid credentials.

**Impact and Consequences**
- **Full Hypervisor Domain Compromise**: Administrative control of vCenter allows attackers to manipulate host clusters, virtual machine storage, and guest operating systems.
- **High Risk of Virtualization Ransomware**: Hypervisor-level access allows threat actors to deploy domain-wide ransomware or extract offline database disks directly while bypassing guest OS security controls.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Apply Broadcom security updates for VMware vCenter Server across all production and backup environments immediately.
- **II. Identity & Access Management (Containment):** Isolate vCenter administrative access within dedicated out-of-band management VLANs isolated from corporate user subnets.
- **III. Infrastructure Intelligence (Detection):** Monitor vCenter authentication logs for anomalous session creation events originating from unexpected internal IP addresses.
- **IV. Operational Resilience:** Ensure hypervisor configuration backups are stored offline and encrypted to guarantee recovery capabilities against hypervisor compromise.
- **V. Simulation environment:** Test emergency patch deployment procedures and hypervisor restoration workflows within isolated lab environments.

**Conclusion**
Hypervisor management systems represent Tier-0 critical assets; unauthenticated remote vulnerabilities require network isolation and high-priority patch remediation.

**Further Reading**
- Broadcom Security Advisory for VMware vCenter Server

**Footnotes**
[1] https://thehackernews.com/2026/11/vmware-vcenter-hit-by-another-critical.html
[2] https://www.securityweek.com/vmware-updates-patch-critical-esx-vcenter-vulnerabilities/