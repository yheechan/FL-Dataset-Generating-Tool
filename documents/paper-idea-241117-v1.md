# FL Dataset Generation Paper Idea


## Q1: Number of mutants to generate on a line
* Question: What is the sufficient **number of mutants to generate on each line** to construct an effective MBFL feature dataset? (i.e., the dataset acheives acc@5 at function level above 70%)
* Expected Answer: On average utilizing 8 mutants reveals a fixing mutant on the buggy line.

## Q2: Number of randomly selected lines
* Question: How does the **number of randomly selected lines** effect the acc@5 performance of MLP?
* Expected Answer: Increasing the number of randomly selected lines improves acc@5 performance of MLP but increases the time cost of FL dataset generation process.

## Q3: Number of buggy versions per line
* Question: How does the **number of buggy versions per line** effect the acc@5 performance of MLP?
* Experiment: Compare MLP that is trained with only 1 buggy version on a line and that is trained with multiple buggy versions on a line.

## Q4: Utilization of CCT
* Question: How does the acc@5 performance of MLP differ when the training dataset is constructed with and without the **utilization of CCTs** (Coincidentally Correct Testcases)?
* Expected Answer: Not only does the exclusion of CCTs improve SBFL accuracy, it also improves the accuracy of MBFL too.

## Q5: MLP's acc@5 performance on real-worl-bugs
* Question: How effective is MLP’s acc@5 performance on real world bugs when trained only with FL features of mutant bugs.
* Answer: MLP model trained with only FL feature dataset of mutant-buggy versions shows acceptable acc@5 performance on real-world bugs.


## Background: What DeepFl Misses in their paper
* The paper DeepFL doesn't include any detailed information about their method of making SBFL MBFL featured dataset for training MLP. (e.g., # of mutants used on a line, # of targetted line for MBFL feature extraction, etc.)
