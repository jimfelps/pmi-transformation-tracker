# PMI Transformation Tracker

An end-to-end finance and data engineering project examining how quickly Philip Morris International is transforming from a traditional cigarette company into a smoke-free nicotine company.

The project combines SEC financial data, company operating disclosures, Python-based data transformation, a dimensional SQLite model, an analytical layer, automated validation, and a Streamlit dashboard.

## Executive Overview

Philip Morris International is undergoing a fundamental change in its business model. Traditional cigarettes remain a major source of revenue and profit, while heated tobacco, oral nicotine, and e-vapor products are becoming increasingly important to the company's growth.

The PMI Transformation Tracker was built to answer a simple question:

> **How quickly is Philip Morris transforming from a cigarette company into a smoke-free nicotine company?**

Rather than approaching the question as a stock-price or valuation dashboard, the project focuses on the operating economics of the transformation.

It tracks the shift through:

- revenue and shipment mix
- smoke-free product growth
- combustible tobacco performance
- segment revenue, gross profit, and gross margin
- reported drivers of revenue and gross-profit growth
- company-level financial outcomes

The result is an analytical product designed to connect company strategy with the underlying financial and operating data.

## The Business Question

A company's transformation cannot be measured with a single percentage.

PMI can simultaneously have a declining or mature cigarette business, a rapidly expanding smoke-free portfolio, pricing power in combustibles, improving margins, and differences between operating performance and earnings per share.

The project therefore breaks the transformation into several related questions:

**How much of the business is already smoke-free?**

Smoke-free products can be measured both by their share of shipment volume and their share of company revenue. Comparing those measures helps show how economically significant the smoke-free portfolio has become relative to its physical volume.

**What is driving growth in the legacy business versus the emerging business?**

Revenue growth alone cannot distinguish between businesses growing through additional product volume and businesses relying primarily on pricing. PMI's reported growth bridges make it possible to examine those mechanisms separately.

**What is happening inside the smoke-free portfolio?**

Heated tobacco, oral smoke-free products, and e-vapor products have very different scale and growth profiles. Treating smoke-free products as a single category hides those differences.

**Is the transformation improving the economics of the company?**

Revenue growth is only part of the story. Segment gross profit, gross margin, operating income, operating margin, and ultimately earnings per share provide increasingly demanding tests of whether the transformation is translating into financial performance.

## What the Analysis Shows

As of 2026-Q2, smoke-free products represented approximately **41.5% of PMI revenue** while accounting for approximately **23.5% of equivalent-unit shipment volume**. The difference illustrates the economic importance smoke-free products have already achieved within the company, although shipment units and revenue should not be interpreted as directly comparable measures of profitability.

The analysis also identifies two different growth mechanisms within PMI's international businesses.

**International Smoke-Free** is primarily a volume- and mix-driven growth business. In 2026-Q2, smoke-free product revenue increased approximately **11.6%** year over year while shipment volume increased approximately **7.6%**.

**International Combustibles** continues to generate revenue growth despite much slower cigarette volume growth. In 2026-Q2, combustible product revenue increased approximately **9.5%** while cigarette volume increased approximately **1.1%**. PMI's reported revenue bridge provides additional evidence of the mechanism: pricing contributed substantially to International Combustibles revenue growth while volume/mix was a negative contributor.

Within smoke-free products, scale and growth rate also tell different stories. Heated tobacco remains much larger by shipment volume, while e-vapor grew from a much smaller base.

At the company level, 2026-Q2 revenue increased approximately **10.4%** and operating income increased approximately **22.0%**, with operating margin improving approximately **3.9 percentage points**. GAAP diluted EPS, however, declined approximately **7.7%** year over year.

That divergence creates one of the project's next analytical questions: **why is stronger operating performance not flowing directly through to GAAP diluted EPS?**

## How the Project Evolved

The final dashboard was not designed upfront. Its structure emerged through a series of questions raised by the data.

### 1. Start with the transformation question

The initial idea was relatively simple: measure how quickly PMI was shifting from cigarettes toward smoke-free products.

That immediately suggested two useful measures:

- smoke-free share of shipment volume
- smoke-free share of net revenue

But collecting those measures revealed the first important modeling issue: PMI's operating disclosures do not map cleanly to a single standardized financial taxonomy.

Traditional SEC XBRL data works well for measures such as company revenue, operating income, and diluted EPS. Product shipments, smoke-free revenue, segment economics, and management's growth bridges require additional information from PMI's filing disclosures.

The project therefore evolved from a straightforward financial-data exercise into a multi-source data pipeline.

### 2. Separate products from reportable segments

A second challenge emerged while exploring PMI's reporting structure.

Product categories and financial segments initially appear similar, but they answer different questions.

Product-level measures describe categories such as:

- cigarettes
- heated tobacco units
- oral smoke-free products
- e-vapor
- total smoke-free products

PMI's reportable segments instead reflect how management organizes and evaluates the business. Beginning in 2026, those segments include International Smoke-Free, International Combustibles, and the U.S.

This distinction matters because the U.S. segment contains smoke-free activity. Total company smoke-free revenue therefore cannot simply be treated as International Smoke-Free segment revenue.

Rather than forcing the two classifications into one hierarchy, the analytical model preserves **product** and **segment** as separate dimensions.

### 3. Revenue versus volume raised a new question

Once product revenue and shipment data were brought together, a pattern became visible.

Combustible revenue was growing substantially faster than cigarette shipment volume.

That observation suggested a hypothesis:

> **Pricing may be doing much more of the work in the combustible business than physical volume growth.**

The existing dataset could identify the spread, but it could not explain it.

That became a new data requirement.

PMI's reported revenue and gross-profit bridges were added to the model, separating reported changes into drivers such as:

- currency
- acquisitions and divestitures
- price
- volume / mix / other
- cost effects where applicable

The resulting analysis supported the original hypothesis. International Combustibles relied heavily on positive pricing contribution while volume/mix created an offsetting headwind.

International Smoke-Free showed a different mechanism, with substantially more of its growth coming from volume/mix.

The dashboard's “Two Economic Engines” narrative emerged from this analysis rather than being imposed on the data beforehand.

### 4. Smoke-free growth needed to be decomposed

Treating smoke-free products as a single category created another analytical limitation.

Heated tobacco, oral smoke-free products, and e-vapor products operate at very different scales and were growing at different rates.

The product-performance model was therefore expanded to calculate both:

- year-over-year growth rates
- absolute changes in equivalent-unit shipments

This prevents a small but rapidly growing category from appearing economically larger than a slower-growing category with much greater scale.

The result is a more complete view of what is actually driving PMI's smoke-free expansion.

### 5. Segment economics added another test

Growth alone does not establish whether a transformation is improving the economics of a business.

The analysis was extended to include segment revenue, gross profit, and gross margin using PMI's recast segment disclosures.

This made it possible to examine whether International Smoke-Free was simply growing or also producing attractive gross-profit economics as it scaled.

It also reinforced an important modeling principle used throughout the project: when PMI changed its reportable segment structure, historical comparisons needed to use management's recast historical data rather than combining periods reported under incompatible segment definitions.

### 6. The analysis generated the next data requirement

The final stage of V1 moved back to company-level financial results.

PMI's 2026-Q2 results showed strong revenue growth, operating-income growth, and operating-margin improvement. GAAP diluted EPS moved in the opposite direction.

The existing model can identify that divergence but cannot responsibly explain it because the current financial model stops primarily at operating income.

Rather than infer a cause that the modeled data cannot support, the divergence becomes a question for the next phase of the project.

Answering it will require extending the model below operating income to incorporate items such as interest expense, taxes, non-operating items, and other drivers of earnings per share.

This illustrates the development pattern behind the project:

> **Observation → hypothesis → additional data requirement → model extension → analysis**

The dashboard is therefore not intended to be a finished collection of every potentially useful PMI metric. It is an evolving analytical model in which new data is added when it helps answer a specific business question.

## Data Architecture

The project separates data collection, transformation, storage, analysis, and presentation into distinct layers.

```text
SEC Company Facts API        PMI SEC Filings
         │                         │
         └──────────┬──────────────┘
                    ▼
              Raw Source Data
                    │
                    ▼
           Python Transformation
                    │
                    ▼
           Dimensional SQLite Model
                    │
                    ▼
              Analytical Layer
                    │
                    ▼
        Presentation-Ready Exports
                    │
                    ▼
            Streamlit Dashboard
```

The dashboard does not contain source-specific transformation logic and does not query raw filing data. By the time data reaches Streamlit, source semantics have already been normalized and the required analytical measures have been calculated.

That creates a cleaner boundary between **data engineering**, **analysis**, and **presentation**.

## Analytical Model

The core SQLite model uses a normalized observation structure centered on a fact table with supporting dimensions.

Key dimensions include:

- **Period** — fiscal year and quarter
- **Metric** — revenue, operating income, EPS, shipment volume, gross profit, margin measures, and growth bridges
- **Product** — cigarettes, heated tobacco, oral smoke-free, e-vapor, and broader product groupings
- **Segment** — International Smoke-Free, International Combustibles, U.S., and total company
- **Driver** — price, currency, volume/mix/other, acquisitions/divestitures, cost, and total change

This allows observations with different grains to coexist without forcing unrelated business concepts into the same hierarchy.

For example:

```text
2026-Q2 | shipment_volume | htu
2026-Q2 | revenue         | smoke_free
2026-Q2 | gross_margin    | international_smoke_free
2026-Q2 | revenue_change  | international_combustibles | price
```

The model also stores source and derivation metadata at the observation level so reported values can be distinguished from calculated values.

## Key Design Decisions

Several modeling decisions became important as the project evolved.

### Keep products and segments separate

Product categories describe **what PMI sells**.

Reportable segments describe **how management organizes and evaluates the business**.

Those concepts overlap but are not interchangeable. Modeling them as separate dimensions prevents misleading comparisons and allows the same analytical model to support both product and segment questions.

### Preserve reported values before calculating ratios

Where possible, reported financial values are retained before analytical ratios are calculated.

For example, gross margin is derived from reported gross profit and revenue rather than reconstructed unnecessarily from independently rounded components.

This reduces avoidable reconciliation differences.

### Derive Q4 when necessary

Some annual disclosures provide full-year results alongside Q1, Q2, and Q3 without a separately reported fourth-quarter value.

In those cases:

```text
Q4 = Full Year - Q1 - Q2 - Q3
```

Derived observations are identified as such rather than being presented internally as directly reported source values.

### Use recast history for segment comparisons

PMI changed its reportable segment structure effective in 2026.

Historical segment comparisons therefore use comparative periods recast by PMI into the new structure. This avoids comparing current segments with historical organizational definitions that no longer represent the same economic perimeter.

### Keep presentation logic out of the dashboard

The Streamlit application reads presentation-ready analytical exports rather than raw or partially transformed source data.

That means calculations such as year-over-year growth, revenue mix, shipment mix, margin changes, and growth-driver normalization happen upstream.

Streamlit's primary responsibility is presentation.

## Data Quality & Validation

Data quality checks are built into multiple stages of the project.

The pipeline validates:

- uniqueness of analytical keys
- expected reporting periods
- valid percentage ranges
- presence of required product categories
- consistency of presentation-layer datasets
- reconciliation of reported growth bridges

PMI's reported revenue and gross-profit bridges provide a particularly useful accounting-style validation.

For each bridge:

```text
Total Change ≈ Sum of Reported Drivers
```

Because source disclosures are rounded, small differences are permitted. V1 requires each modeled bridge to reconcile within **$2 million** of the reported total change.

A dedicated V1 QA script also validates the final analytical exports consumed by the dashboard. This provides a release check after the full transformation and analytical pipeline has run.

The goal is not merely to produce plausible-looking charts. It is to maintain a traceable path from public disclosure to analytical output.

## Dashboard

The Streamlit dashboard is organized around the analytical story rather than the structure of the underlying data.

### The Transformation

Compares smoke-free revenue mix with equivalent-unit shipment mix to show how PMI's business composition is changing.

### Two Economic Engines

Contrasts International Smoke-Free and International Combustibles across revenue growth, gross-profit growth, gross margin, product revenue, and shipment volume.

### Growth Drivers

Uses PMI's reported revenue bridges to separate growth into price, volume/mix/other, currency, and acquisition/divestiture effects.

This helps distinguish the different mechanisms supporting growth in the smoke-free and combustible businesses.

### Inside the Smoke-Free Engine

Breaks smoke-free shipment volume into heated tobacco, oral smoke-free, and e-vapor products and compares both scale and year-over-year growth.

### Financial Outcome

Connects the operating transformation back to company-level revenue, operating income, operating margin, and diluted EPS.

The divergence between improving operating results and declining GAAP diluted EPS in 2026-Q2 becomes a question for a future phase rather than an unsupported conclusion in V1.

## Project Roadmap

V1 establishes the core transformation model, but several analytical questions remain open.

### Guidance vs. Actuals

Capture management guidance over time and compare subsequent performance with the expectations communicated to investors.

### The EPS Disconnect

Extend the financial model below operating income to investigate the divergence between operating performance and GAAP diluted EPS.

### PMI vs. Altria

Compare two companies with shared origins but increasingly different geographic footprints and smoke-free strategies.

### Geographic Adoption

Track smoke-free adoption across important markets, including HTU users, shipment growth, market share, and geographic expansion where disclosures permit.

### U.S. Smoke-Free Expansion

Follow the development of PMI's U.S. smoke-free business, including ZYN and the developing IQOS rollout.

The roadmap is intentionally driven by analytical questions rather than by adding features for their own sake.

## Running the Project Locally

### Requirements

- Python 3
- pip
- Git

### Setup

Clone the repository:

```bash
git clone <repository-url>
cd pmi-transformation-tracker
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Launch the dashboard:

```powershell
streamlit run app.py
```

### V1 Quality Check

The final analytical exports can be validated with:

```powershell
python src\qa_v1.py
```

A successful run ends with:

```text
V1 QA PASSED
```

## Repository Structure

```text
pmi-transformation-tracker/
│
├── app.py
├── requirements.txt
├── README.md
│
├── .streamlit/
│   └── config.toml
│
├── data/
│   ├── pmi_tracker.db
│   ├── raw/
│   ├── processed/
│   └── analysis/
│
├── src/
│   ├── sec_collector.py
│   ├── pmi_filing_collector.py
│   ├── transform_financials.py
│   ├── transform_shipments.py
│   ├── transform_revenue.py
│   ├── transform_segments.py
│   ├── transform_bridges.py
│   ├── database.py
│   ├── analysis.py
│   ├── export_analysis.py
│   └── qa_v1.py
│
└── tests/
```

### Data layers

**`data/raw/`**  
Original downloaded source material. Raw source files are excluded from version control.

**`data/processed/`**  
Structured intermediate datasets produced by the transformation layer.

**`data/analysis/`**  
Presentation-ready analytical datasets consumed by Streamlit.

**`data/pmi_tracker.db`**  
SQLite analytical database containing the normalized dimensional model.

**`src/`**  
Collection, transformation, modeling, analysis, export, and QA logic.

**`app.py`**  
Presentation layer. The application consumes analytical exports rather than implementing source-data transformations itself.

## Sources

Primary public sources include:

- Philip Morris International quarterly and annual SEC filings
- SEC Company Facts / XBRL data
- Philip Morris International earnings and investor-relations materials
- PMI's recast historical segment disclosures

The public dashboard includes direct links to the primary source libraries used by the project.

## Disclaimer

This is an independent analytical and educational project based on publicly available information.

It is not affiliated with or endorsed by Philip Morris International and should not be interpreted as investment advice.