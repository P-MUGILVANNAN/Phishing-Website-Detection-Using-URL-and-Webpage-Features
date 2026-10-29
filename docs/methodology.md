# Research Methodology: Evaluating Generalization on Unseen Domains

## 1. The Domain Memorization Fallacy

In traditional phishing detection literature, researchers frequently perform random train/test splits over collections of URLs. However, phishing campaigns often generate multiple URLs under the same registered domain:

$$\text{e.g. } \texttt{paypal-update.xyz/login}, \texttt{paypal-update.xyz/verify}, \texttt{paypal-update.xyz/account}$$

If a random split places $\texttt{paypal-update.xyz/login}$ in the training partition and $\texttt{paypal-update.xyz/verify}$ in the test partition, the model can simply memorize registered domain tokens rather than learning generalized malicious URL syntax. This results in **artificially inflated benchmark accuracy** that rapidly collapses when the model encounters an active phishing campaign hosted on a previously unseen domain.

## 2. Evaluation Protocol A: Domain-Grouped Partitioning

PhishGuard AI addresses this vulnerability by implementing **Protocol A**:
1. Every URL is parsed into its Public Suffix List-aware registered domain:
   $$D = \text{PSL}(H)$$
2. Partitions are formed strictly grouped by registered domain $D$:
   $$\mathcal{D}_{\text{train}} \cap \mathcal{D}_{\text{val}} = \emptyset, \quad \mathcal{D}_{\text{train}} \cap \mathcal{D}_{\text{test}} = \emptyset, \quad \mathcal{D}_{\text{val}} \cap \mathcal{D}_{\text{test}} = \emptyset$$
3. Evaluation metrics are measured exclusively on test samples whose registered domains were completely absent from model training.

## 3. Generalization Gap Formulation

To measure the vulnerability of a model to domain memorization, PhishGuard AI defines the **Generalization Gap ($\Delta F_1$)**:

$$\Delta F_1 = F_1^{(\text{Random Split})} - F_1^{(\text{Domain-Grouped Split})}$$

- When $\Delta F_1 \approx 0$, the model's predictive performance is driven by genuine structural, lexical, and NLP risk indicators that transfer seamlessly to new attacker infrastructure.
- A high $\Delta F_1$ indicates that the model relies heavily on domain memorization and will suffer high false-negative rates in real-world deployment.

## 4. Multi-Modal Feature Vector Architecture

The feature representation comprises 52 indicators spanning:
- **Lexical Dimensions (32 features)**: URL length, entropy, digit ratios, delimiter counts, suspicious punctuation patterns, brand tokens in subdomains, and raw IP flags.
- **Webpage & NLP Dimensions (20 features)**: Title lengths, form counts, password inputs, external form action targets, brand impersonation counts, and credential urgency keyword frequencies.

