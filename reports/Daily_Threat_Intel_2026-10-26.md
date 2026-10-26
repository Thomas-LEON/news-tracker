# Daily Threat Intel Report
**Date:** October 26, 2026

🟢 **Threat Score:** 49/100
*(Auditable Metrics - Threat Capability: 5/10 | Event Frequency: 5/10 | Business Impact: 5/10)*

**Executive Summary - Incidents:**
1. Incident Title: Microsoft 365 AitM Token-Replay Campaign Targeting 79 Organizations (July 14 – September 22, 2026)
2. Incident Title: Gheist Automated Campaign Compromises GitHub Enterprise Secrets via Actions Logs (October 2026)
3. Incident Title: AI Coding Agents Hijacked via Malicious AGENTS.md File (October 2026)
4. Incident Title: Active In-The-Wild Exploitation of Critical PHP2Shell RCE Flaws (October 2026)
5. Incident Title: Unpatched Tailscale SSH Flaws Enable Cross-Server Root Escalation (October 2026)

---

*(Auditable Metrics - Threat Capability: 5/10 | Event Frequency: 5/10 | Business Impact: 5/10)*

## Incident Title: Microsoft 365 AitM Token-Replay Campaign Targeting 79 Organizations (July 14 – September 22, 2026)

**Incident Metadata:**
- **Primary Category:** CLOUD
- **News Nature:** New attack
- **Timeline:** Incident Date: July 14 – September 22, 2026 | Source Publication Date: October 26, 2026
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** Global / Microsoft 365 Cloud
- **List of Companies Impacted:** Microsoft (platform), 79 undisclosed corporate organizations

Cybersecurity firm Huntress disclosed an Adversary-in-the-Middle (AitM) campaign targeting Microsoft 365 users between July 14 and September 22, 2026. Threat actors compromised 97 user accounts across 79 organizations by stealing and replaying authentication session tokens ¹.

**Overview**
Between July 14 and September 22, 2026, security researchers observed 497 successful unauthorized sign-in events across Microsoft 365 tenant environments. Threat actors utilized AitM relay infrastructure to capture legitimate authentication sessions and subsequently replayed the stolen OAuth tokens to compromise corporate email accounts across 79 distinct organizations ¹.

**The Breach Mechanism**
- **AitM Proxy Relay:** Attackers positioned an AitM proxy server between target users and legitimate Microsoft 365 authentication endpoints, capturing multi-factor authentication (MFA) tokens during sign-in attempts ¹.
- **Session Token Replay:** Stolen session tokens were extracted and replayed from unauthorized infrastructure, bypassing standard SSO and MFA protections to maintain persistent mailbox access ¹.

**Impact and Consequences**
- **Widespread Tenant Access:** Confirmed breach of 97 enterprise accounts spanning 79 separate customer organizations ¹.
- **Unauthorized Data Access:** Unrestricted visibility into corporate email systems, exposing sensitive operational communications and financial workflows ¹.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Enforce strict Conditional Access Policies requiring compliant, domain-joined corporate devices for token usage.
- **II. Identity & Access Management (Containment):** Mandate FIDO2-compliant phish-resistant authentication mechanisms (e.g., security keys) to render AitM proxies ineffective.
- **III. Infrastructure Intelligence (Detection):** Implement behavioral monitoring to flag impossible travel events, unexpected user agent changes, and anomalous token reuse across unverified IP addresses.
- **IV. Operational Resilience:** Establish automated token revocation procedures to invalidate active user sessions immediately upon detection of anomalous authentication events.
- **V. Simulation environment:** Conduct AitM phishing simulations within staging environments to test organizational resistance against modern proxy-based authentication attacks.

**Conclusion**
AitM token-replay techniques highlight the limitations of traditional push-based MFA, underscoring the immediate requirement for phish-resistant identity controls across cloud ecosystems.

**Further Reading**
https://thehackernews.com/2026/10/microsoft-365-token-replay-attacks.html

**Footnotes**
[1] https://thehackernews.com/2026/10/microsoft-365-token-replay-attacks.html

---

## Incident Title: Gheist Automated Campaign Compromises GitHub Enterprise Secrets via Actions Logs (October 2026)

**Incident Metadata:**
- **Primary Category:** SUPPLY CHAIN
- **News Nature:** New attack
- **Timeline:** Incident Date: October 2026 | Source Publication Date: October 26, 2026
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** GitHub Cloud / GitHub Enterprise
- **List of Companies Impacted:** GitHub (platform), GitHub Enterprise customer environments

Cloud security firm Wiz uncovered an automated attack campaign named "Gheist" in October 2026 that leverages stolen GitHub tokens to exfiltrate private repository secrets via GitHub Actions logs ¹.

**Overview**
In October 2026, cloud security vendor Wiz reported on an automated threat campaign designated as "Gheist". Attackers leveraged previously stolen GitHub tokens to inject malicious workflows into private software repositories and GitHub Enterprise environments. The injected steps force the repository to print sensitive secrets directly into GitHub Actions execution logs, which the threat actors download before deleting the execution history to erase evidence ¹.

**The Breach Mechanism**
- **Malicious Workflow Injection:** Attackers use compromised GitHub access tokens to commit modified workflow files to private repositories ¹.
- **Secrets Extraction & Log Cleansing:** The workflows execute code that outputs repository secrets directly to build execution logs. Attackers automatically fetch the logs and immediately delete the workflow run history to avoid detection ¹.

**Impact and Consequences**
- **Exfiltration of Enterprise Credentials:** Severe exposure of sensitive API keys, cloud access tokens, and credentials embedded within software build pipelines ¹.
- **Secondary Supply Chain Risks:** Exfiltrated credentials grant adversaries secondary access to linked cloud infrastructure and production database environments ¹.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Enforce strict Personal Access Token (PAT) policies with mandatory expiration limits and granular scope restrictions.
- **II. Identity & Access Management (Containment):** Implement source IP restriction allowlists for API access across GitHub Enterprise tenants.
- **III. Infrastructure Intelligence (Detection):** Deploy automated log audit tools to alert on unexpected workflow file changes and immediate workflow run deletions.
- **IV. Operational Resilience:** Integrate automated secret scanning with instant secret revocation triggers upon detection of plain-text credentials in build outputs.
- **V. Simulation environment:** Maintain isolated CI/CD test pipelines to evaluate workflow security policies before deploying updates to enterprise repositories.

**Conclusion**
Automated secret extraction from build logs illustrates the critical need to enforce minimal token scopes and continuous audit logging across modern software supply chains.

**Further Reading**
https://thehackernews.com/2026/10/gheist-uses-stolen-github-tokens-to.html

**Footnotes**
[1] https://thehackernews.com/2026/10/gheist-uses-stolen-github-tokens-to.html

---

## Incident Title: AI Coding Agents Hijacked via Malicious AGENTS.md File (October 2026)

**Incident Metadata:**
- **Primary Category:** AI
- **News Nature:** New attack
- **Timeline:** Incident Date: October 2026 | Source Publication Date: October 25–26, 2026
- **Impacted Country:** Global / Unknown
- **Geolocation / Cloud Region:** Enterprise Developer Workstations
- **List of Companies Impacted:** Forever Security (Discoverer), Undisclosed Enterprise Customer

Security firm Forever Security detected an attack in October 2026 where a malicious instruction file (`AGENTS.md`) located in a developer's Downloads folder attempted to manipulate an autonomous AI coding agent into installing a rogue npm package ¹, ².

**Overview**
In October 2026, security firm Forever Security intercepted an active threat attempt on an enterprise workstation. A malicious `AGENTS.md` markdown file located in a developer's local Downloads folder contained context-hijacking instructions designed to force an autonomous AI coding agent into downloading and installing a known-malicious npm package. The security controls stopped the agent prior to code execution ¹, ².

**The Breach Mechanism**
- **Indirect Prompt Injection:** Adversaries placed a rogue `AGENTS.md` instruction file into a local workspace directory that the AI coding agent automatically indexed ¹, ².
- **Automated Package Execution Request:** The malicious context instructed the AI agent to bypass standard verification checks and execute a terminal command installing a malicious package from the npm registry ¹, ².

**Impact and Consequences**
- **Developer Endpoint Risk:** Potential full local system takeover resulting from arbitrary execution of malicious dependency code ¹.
- **Software Supply Chain Contamination:** Poisoned AI development sessions risk introducing malicious code directly into production enterprise software builds ¹.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Mandate policies restricting AI coding agents from reading context or executing commands outside designated project repositories.
- **II. Identity & Access Management (Containment):** Run AI agent runtimes under containerized, unprivileged user accounts with restricted system permissions.
- **III. Infrastructure Intelligence (Detection):** Monitor workstation process creation for unverified package installation commands originating from AI helper tools.
- **IV. Operational Resilience:** Enforce Human-in-the-Loop (HITL) approval requirements for all external dependency additions or script executions generated by AI agents.
- **V. Simulation environment:** Establish test sandboxes to perform indirect prompt injection resiliency tests on all deployed developer AI tools.

**Conclusion**
As organizations deploy autonomous AI development agents, context-poisoning vulnerabilities require strict architectural boundaries between AI agent memory contexts and local host file systems.

**Further Reading**
https://thehackernews.com/2026/10/malicious-file-in-downloads-folder.html

**Footnotes**
[1] https://thehackernews.com/2026/10/malicious-file-in-downloads-folder.html
[2] https://www.bleepingcomputer.com/news/security/ai-coding-agents-hijacked-using-agentsmd-file-in-downloads-folder/

---

## Incident Title: Active In-The-Wild Exploitation of Critical PHP2Shell RCE Flaws (October 2026)

**Incident Metadata:**
- **Primary Category:** VULNERABILITY
- **News Nature:** New attack
- **Timeline:** Incident Date: October 2026 | Source Publication Date: October 25–26, 2026
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** Global Enterprise Networks
- **List of Companies Impacted:** Vulnerable PHP deployments

Security researchers confirmed active in-the-wild exploitation of two critical Remote Code Execution (RCE) flaws in PHP, known as PHP2Shell (CVE-2026-109618 and CVE-2026-109619), targeting vulnerable server environments in October 2026 ¹, ².

**Overview**
Reports published on October 25–26, 2026, confirmed active exploitation attempts against two critical RCE vulnerabilities, collectively tracked as PHP2Shell (CVE-2026-109618 and CVE-2026-109619) ², ³. Security monitoring entities observed global scanning activity and attack execution against vulnerable PHP applications. Palo Alto Networks Unit 42 updated its assessment to retract an earlier link between these PHP2Shell flaws and post-compromise activity at a European government agency ¹.

**The Breach Mechanism**
- **Unauthenticated Shell Execution:** Exploitation of input validation flaws in susceptible PHP application parsing mechanisms, allowing threat actors to drop web shells ¹, ².
- **Automated Exploitation Scanning:** Global reconnaissance infrastructure scanning internet-facing ranges to automatically identify vulnerable PHP endpoints and execute remote commands ¹.

**Impact and Consequences**
- **Unrestricted System Compromise:** Successful RCE grants threat actors full underlying system privileges on target web hosting servers ², ³.
- **Widespread Web Infrastructure Exposure:** Confirmed scanning and exploitation activity directed at enterprise and public web server deployments globally ¹, ².

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Deploy official vendor patches and follow official PHP mitigation guidance immediately across all internet-facing web assets ³.
- **II. Identity & Access Management (Containment):** Restrict web server process privileges to enforce minimal host system access.
- **III. Infrastructure Intelligence (Detection):** Update Web Application Firewall (WAF) signature sets to block PHP2Shell exploitation vectors and monitor web server logs for unauthorized process execution.
- **IV. Operational Resilience:** Isolate web application tiers within segregated network segments to prevent lateral movement to core backend infrastructure.
- **V. Simulation environment:** Perform vulnerability scanning and patch validation in staging server environments prior to production rollout.

**Conclusion**
The rapid transition of PHP2Shell into active operational exploitation underscores the urgency of maintaining rigorous application patching cycles for core open-source web stacks.

**Further Reading**
https://www.bleepingcomputer.com/news/security/php2shell-security-flaws-now-sucessfully-exploited-in-the-wild/

**Footnotes**
[1] https://thehackernews.com/2026/10/php2shell-exploitation-hits-government.html
[2] https://www.bleepingcomputer.com/news/security/php2shell-security-flaws-now-sucessfully-exploited-in-the-wild/
[3] https://www.infosecurity-magazine.com/news/php-publishes-mitigation-advice/

---

## Incident Title: Unpatched Tailscale SSH Flaws Enable Cross-Server Root Escalation (October 2026)

**Incident Metadata:**
- **Primary Category:** INFRASTRUCTURE
- **News Nature:** New attack
- **Timeline:** Incident Date: October 2026 | Source Publication Date: October 25, 2026
- **Impacted Country:** Global
- **Geolocation / Cloud Region:** Tailscale Virtual Private Overlay Networks
- **List of Companies Impacted:** Tailscale (software vendor), enterprise Tailscale SSH installations

Security research published on October 25, 2026, revealed unpatched security flaws in Tailscale SSH that allow a compromised node to gain root privilege access to remote reachable servers ¹.

**Overview**
In October 2026, details were published regarding an unpatched attack vector in environments running Tailscale SSH. If an attacker gains control of a single endpoint that is permitted by network access rules to connect to a target server, and Tailscale SSH port forwarding is enabled, the attacker can leverage design flaws to escalate privileges to root on adjacent network servers ¹.

**The Breach Mechanism**
- **Port Forwarding Abuse:** Attackers exploit enabled Tailscale SSH port-forwarding permissions on a breached endpoint to bypass secondary access verification controls ¹.
- **Lateral Privilege Escalation:** Leveraging network access control rules granted to the initially compromised host to gain unauthorized root-level command execution on targeted secondary servers ¹.

**Impact and Consequences**
- **Cross-Server Root Compromise:** Potential escalation from a single compromised low-tier endpoint to root access across critical server infrastructure ¹.
- **Zero-Trust Network Perimeter Bypass:** Weakened boundary assurances within overlay networks, enabling lateral movement ¹.

**Proposed Control: Mitigating Threats**
To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
- **I. Governance & Containment (Prevention):** Disable SSH port forwarding features within Tailscale SSH configurations unless explicitly required for verified operational tasks.
- **II. Identity & Access Management (Containment):** Audit and tighten Tailscale Access Control Lists (ACLs) to strictly limit inter-device connection paths.
- **III. Infrastructure Intelligence (Detection):** Monitor Tailscale SSH logs for unexpected port forwarding attempts and unauthorized administrative commands.
- **IV. Operational Resilience:** Micro-segment critical production server nodes into distinct ACL groups to prevent shared network path traversal.
- **V. Simulation environment:** Validate Tailscale network ACL policies in lab environments to verify that port forwarding cannot cross security boundaries.

**Conclusion**
System management tools must enforce rigid access boundaries, as unmitigated administrative capabilities can turn localized endpoint breaches into widespread infrastructure compromises.

**Further Reading**
https://thehackernews.com/2026/10/unpatched-tailscale-ssh-flaws-could-let.html

**Footnotes**
[1] https://thehackernews.com/2026/10/unpatched-tailscale-ssh-flaws-could-let.html