# FL Dataset Generation Paper Idea


## Abstract
## Introduction
## Motivation
## Background
## Approach
## Experiment Design
## Results
## Findings
## Conclusion


## Q1: Impact of the Number of buggy versions per line
* Question: How does the **number of buggy versions per line** affect the acc@5 performance of MLP model?
* Experiment plan:
    * Train MLP models using FL datasets with varying numbers of buggy versions per line: **1, 5, 10, 15**.
    * Compare the acc@5 performance of MLP model across these training datasets.

## Q2: Role of Coincidetally Correct Testcaases (CCT).
* Question: How does including CCTs in the training dataset affect the acc@5 performance of MLP model.
* Experiment plan:
    * Construct one FL dataset utilizing CCTs and another without CCTs.
    * Train MLP models with both datasets and compare their acc@5 performance.


## Q3: Optimal Number of mutants to generate on a line
* Question: What is the sufficient **number of mutants to generate on each line** to construct an effective MBFL feature dataset?
    * Effectiveness Criteria:
        * accuracy: Achieves acc@5 above 70% at the function level.
        * time efficiency: The MBFL dataset can be generated within **N hours**.
* Experiment plan:
    * Generate FL datasets by creating **5, 10, 15, and 20 mutants per line** for lines executed by failing TCs.
    * Train MLP models with these datasets and cmopare their acc@5 performance and dataset generation time durations.

## Q4: Number of randomly selected lines
* Question: What is the sufficient **number of randomly selected lines** to construct an effective MBFL feature dataset?
    * Effectiveness Criteria:
        * accuracy: Achieves acc@5 above 70% at the function level.
        * time efficiency: The MBFL dataset can be generated within **N hours**.
* Experiment plan:
    * Construct FL datasets by randomly selecting **25%, 50%, and 75%** of liens executed by failing TCs.
    * Train MLP models with these datasets and evaluate their acc@5 performance.


## Q5: Performance of MLP on Real-World Bugs
* Question: How effective is MLP’s **acc@5 performance on real-world bugs** when trained only with mutant-based FL features?
* Experiment plan:
    * Train the MLP using an FL dataset consisting onlly of mutant buggy versions.
    * Evaluate its acc@5 performance on real-world buggy versions.


## Q6: Heuristic Application: Removing buggy versions without F2P on buggy line
* Question: Does applying the heuristics of removing buggy versions with no F2P on buggy line in their MBFL features imrpove acc@5 performance?
* Heuristic: Exclude buggy versions from the training dataset if MBFL features of the buggy line contains no F2P.
* Experiment Plan:
    * Train an MLP model using FL dataset with the heurstic applied.
    * Evaluate the model's acc@5 performance on the excluded buggy verisons.


## Q7: Target File Selection: High vs. Low Line Coverage
* Question: How does selecting target files based on their line coverage affect MLP's accuracy performance?
    * High Line Coverage: Files with line coverage above 70%.
    * Low Line Coverage: Files with line coverage below 70%.
* Exeriment Plan:
    * Construct two FL datsaet: one from files with high line coverage and another from files with low line coverage.
    * Train MLP models with these datasets and compair their accuracy performance.


## Q8: Line selection Methods: Random vs. SBFL Rank
* Question: Which line selection method provides better MBFL accuracy performance?
    * Random Selection: Select N lines randomly from those executed by failing TCs.
    * SBFL-Based Selection: Select the top N lines ranked highest by SBFL metric.
* Experiment Plan:
    * Generate two FL datasets, one using each method.
    * Train MLLP models with both datasets and compair their acc@5 performance.


last updated Nov 25, 2024
