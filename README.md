# Empirical Package for _An Industry Survey on Refactoring Towards Microservices: From Literature to Practice_

This replication package contains the empirical materials from a survey investigating industry practices in migrating monolithic systems to microservices architectures. It includes the survey instrument, raw and cleaned datasets, a comprehensive analysis notebook with findings on refactoring processes, tooling adoption, and evaluation approaches, and a robustness-analysis script.


## Scope of the Study

To assess how the process of refactoring to microservices is undertaken, the tools used, and the evaluation methods employed in industry, we conducted an online survey via *Google Forms* (estimated completion time: *30 minutes*). We received 66 responses, of which 65 were valid and analyzed (1 invalid response was excluded during data preparation). The study addresses three research questions:

* RQ1. What is the refactoring process that professionals follow? 
* RQ2. What tools do professionals use? 
* RQ3. How do professionals evaluate the result of the decomposition?

## Package Content

* `survey_instrument.pdf`
    - The complete survey instrument as presented to respondents via Google Forms.
* `survey_responses_raw.csv`
    - Raw results retrieved from Google Forms (66 responses, including the invalid one).
* `survey_responses_cleaned.csv`
    - Cleaned results after data preparation (65 valid responses). This is the file used by the notebook.
* `analysis.ipynb`
    - Jupyter Notebook with the descriptive analysis of the data collected, including all charts and statistics reported in the paper.
* `robustness_analysis.py`
    - Python script with the robustness analysis: 95% Wilson confidence intervals for the main proportions, exploratory subgroup association analyses (Fisher's exact tests with Benjamini-Hochberg correction), and the sensitivity analysis (excluding Brazil-based respondents and Finance-domain projects). Reproduces the tables in the paper's appendix.
* `acm_empirical_standards_checklist.pdf` 
    - Checklist of the ACM Empirical Standards "Questionnaire Surveys."

## How to Run

### Descriptive analysis (`analysis.ipynb`)

The notebook is designed to run on **Google Colab**. To reproduce the analysis:

1. Open `analysis.ipynb` in [Google Colab](https://colab.research.google.com/).
2. Upload the cleaned CSV file (`survey_responses_cleaned.csv`) to Colab's `/content/` directory, or mount your Google Drive and adjust the path in the data-loading cell accordingly.
3. Run all cells sequentially.

**Dependencies** (pre-installed in Colab): `pandas`, `matplotlib`, `numpy`, `wordcloud`, `IPython`.

### Robustness analysis (`robustness_analysis.py`)

The script uses only the Python standard library. From the package directory (with `survey_responses_cleaned.csv` present), run:

```
python3 robustness_analysis.py
```

It prints the confidence intervals, subgroup association tests, and sensitivity tables to standard output.

## Data Dictionary

The CSV columns follow the survey's section numbering (`1.x` through `7.x`):

| Prefix | Survey Section | Description |
|--------|----------------|-------------|
| 1.x | Experience and Background | Work areas, title, country, years of experience, number of projects, domain areas, system scale |
| 2.x | Strategies and Processes | Guidance sources, migration planning, data source likelihood, service boundary criteria |
| 3.x | Tools | Tool assistance (yes/no), specific tools used, desired tool support, tool characteristics |
| 4.x | Splitting the Monolith | Likert-scale agreement on the importance of 7 monolith-splitting techniques |
| 5.x | Decomposing the Database | Likert-scale agreement on the importance of 9 database decomposition techniques |
| 6.x | Challenges | Migration challenges faced |
| 7.x | Evaluation | Quality attributes assessed, evaluation environments, evaluation inputs |

The notebook uses the **cleaned CSV** (`survey_responses_cleaned.csv`) as its data source.

## Data Preparation

The cleaned CSV was produced from the raw Google Forms export through the following (mostly manual) steps:

1. **Exclusion of invalid response**: 1 out of 66 responses was identified as invalid and removed, resulting in 65 valid responses.
2. **Translation**: Portuguese-language entries were translated to English (e.g., `Cursos` → `Courses`).
3. **Column header standardization**: Column names were cleaned and standardized to follow the `Section.Question` numbering scheme.


## Summary Of The Findings

* Practitioners plan the migration mostly to be interspersed with the product evolution
* They mainly focus on web resources and other practitioners' experiences to guide their migration.
* Software documentation and development process data are
used as data sources to decide how to decompose the monolith into microservices.
* They mainly focus on decomposing by business
capability or subdomain.
* Strangler Fig, UI Composition, Parallel Run, Branch by Abstraction, and Change code dependency to service call are the
most used techniques to split the monolith.
* When decomposing the database,
Change Data Ownership is clearly more used than the other techniques.
* Challenges faced during the migration process are database migration and data store splitting, consistency, and ensuring reliability.
* A large share of practitioners does not use any tools to assist their migration.
* They find
that tools for deciding service boundaries, regression testing, microservice API design and refactoring code are needed. 
* Refactoring tools should be easy to use, provide multiple decomposition alternatives and provide visualization.
* Most of the respondents, when asked how they usually evaluate the result of the decomposition, mentioned that they did not do it, it was not worth the effort, or only sometimes, and some specifically said it is based on intuition.
* Maintainability, Performance and Scalability are the quality attributes most assessed.
* The assessment is performed in multiple environments, mostly during development and using more functional tests than production input or simulation.

## Citation

If you use this replication package, please cite the associated paper:

> R. Peixoto, F. F. Correia, T Rosa, N. Ali, J. Fritzsch, C. Pautasso, E. Guerra, J. Bogner, A. Goldman, T. B. Sousa, "An Industry Survey on Refactoring Towards Microservices: From Literature to Practice, 2026 (to appear)



