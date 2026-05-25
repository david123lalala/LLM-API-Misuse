# Our work

SmartFix: Detecting and Repairing Project-Level Misuse of Java Cryptography APIs with LLMs

# Abstract

Java crypto APIs are essential for ensuring confidentiality, data integrity, authentication, and authorization in software, yet their misuse remains challenging due to inherent complexity and evolving security standards. Traditional rule-based approaches rely on predefined patterns but often suffer from high false positive rates, whereas LLMs demonstrate strong code understanding but remain underexplored for project-level crypto reliability assurance. To address this, we conduct a pilot study and identify two key challenges: insufficient activation of domain-specific crypto API knowledge and inadequate project-level contextual awareness. In response, we propose SmartFix, a reliability-grounded framework integrating expert-validated API knowledge construction, context-aware static analysis, and iterative self-correction for project-level crypto API misuse detection and repair. Experimental results on the ApacheCryptoAPI-Bench show that SmartFix significantly outperforms state-of-the-art rule-based and LLM-based baselines. Ablation studies confirm the statistical significance of each component’s contribution. Additionally, we report 9 previously unreported crypto API misuses validated via a controlled user study, paving the way for more reliable and efficient crypto practices in software systems.



# Framework

![alt text](framework.png)


# Result

## Overall Performance
![alt text](overall_performance.png)

## Comparison with rule-based approaches
![alt text](comparison-1.png)

## Comparison with LLM-based approaches
![alt text](comparison-2.png)

## Ablation Study
![alt text](ablation_study.png)


# Code

## CryptoAPI_Agent.py
This file implements the CryptoAPI Agent that detects and repairs crypto API misuse through iterative LLM-based self-reflection.

## Crypto_API_Knowledge_base/extract_knowledge.py  
This file can construct the crypto API knowledge database.

## extract_call_chain.py
This file performs static analysis on Java files to extract function call relationships.

## extract_code_slice.py
This file can extract code slices of crypto APIs.

## judge_API.py
This file identifies Java files that contain crypto APIs.

## pre_baseline.py
This file can run the baseline experiment.

