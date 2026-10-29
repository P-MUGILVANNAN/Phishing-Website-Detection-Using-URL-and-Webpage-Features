# Research Limitations & Operational Constraints

## 1. Automated Detection Disclaimer
PhishGuard AI provides automated probabilistic assessments based on extracted machine learning features. **No model is 100% accurate, and no website classification can be guaranteed safe or benign.** Machine learning scores must serve as automated advisory indicators within a broader defense-in-depth security architecture.

## 2. Dynamic & Cloaked Content Limitations
- Phishing sites frequently employ IP cloaking, geolocation filtering, CAPTCHA challenges, or user-agent sniffing to serve benign content to security scanners.
- Because the built-in safe fetcher strictly disables JavaScript execution to prevent client-side exploits and SSRF re-binding, dynamic Single-Page Applications (SPAs) that render DOM elements via client JavaScript may present limited HTML structure during page inspection.
- When page retrieval is blocked or incomplete, PhishGuard AI automatically relies on URL-only lexical analysis and records explicit missing-feature indicators.

## 3. Adversarial Evasion & Homoglyph Attacks
- Sophisticated threat actors may use high-entropy legitimate domain services (e.g. cloud storage or form builders) to host phishing forms on reputable parent domains.
- While the feature pipeline explicitly captures subdomain depth, brand-in-subdomain tokens, and foreign form action targets, compromised legitimate web infrastructure remains a persistent challenge for lexical classifiers.

## 4. Retraining & Temporal Drift
Attacker lures and newly registered TLD trends evolve continuously. Real-world deployments require periodic retraining with newly collected feeds using the verified domain-grouped protocol to prevent model decay.

