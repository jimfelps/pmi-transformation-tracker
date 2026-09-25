from pathlib import Path

import pandas as pd
import streamlit as st
import altair as alt


# --------------------------------------------------
# Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="PMI Transformation Tracker",
    page_icon="📊",
    layout="wide",
)



DATA_DIR = Path("data/analysis")

SUMMARY_FILE = (
    DATA_DIR
    / "transformation_summary.csv"
)

DRIVERS_FILE = (
    DATA_DIR
    / "growth_drivers.csv"
)

PRODUCT_FILE = (
    DATA_DIR
    / "product_performance.csv"
)


# --------------------------------------------------
# Data
# --------------------------------------------------

@st.cache_data
def load_data():
    summary = pd.read_csv(
        SUMMARY_FILE
    )

    drivers = pd.read_csv(
        DRIVERS_FILE
    )

    products = pd.read_csv(
        PRODUCT_FILE
    )

    return summary, drivers, products


summary, drivers, products = load_data()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.caption(
    "INDEPENDENT COMPANY ANALYSIS"
)

st.title(
    "PMI Transformation Tracker"
)

st.markdown(
    """
    ## How quickly is Philip Morris transforming
    from a cigarette company into a smoke-free
    nicotine company?
    """
)

st.markdown(
    """
    Tracking the shift through product mix,
    shipment growth, segment economics, and the
    underlying drivers of revenue and gross profit.
    """
)


# --------------------------------------------------
# Latest period
# --------------------------------------------------

latest = (
    summary
    .sort_values("period_label")
    .iloc[-1]
)

latest_period = latest["period_label"]

st.caption(
    f"Latest reporting period: {latest_period}  •  "
    "Sources: PMI SEC filings and investor disclosures"
)


# --------------------------------------------------
# Transformation
# --------------------------------------------------

st.header("The Transformation")

st.markdown(
    """
    Smoke-free products already represent a much
    larger share of PMI revenue than their share
    of equivalent-unit shipment volume.
    """
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Smoke-Free Revenue Mix",
        f"{latest['smoke_free_revenue_mix']:.1%}",
    )

with col2:
    st.metric(
        "Smoke-Free Shipment Mix",
        f"{latest['smoke_free_shipment_mix']:.1%}",
    )

with col3:
    mix_premium_pp = (
        latest[
            "smoke_free_revenue_mix_premium"
        ]
        * 100
    )

    st.metric(
        "Revenue Mix Premium",
        f"{mix_premium_pp:.1f} pp",
    )


# --------------------------------------------------
# Transformation trend
# --------------------------------------------------

st.subheader(
    "Smoke-Free Mix Over Time"
)

mix_chart = (
    summary[
        [
            "period_label",
            "smoke_free_revenue_mix",
            "smoke_free_shipment_mix",
        ]
    ]
    .set_index("period_label")
    * 100
)

mix_chart = mix_chart.rename(
    columns={
        "smoke_free_revenue_mix":
            "Revenue Mix",
        "smoke_free_shipment_mix":
            "Shipment Mix",
    }
)

st.line_chart(
    mix_chart,
    y=[
        "Revenue Mix",
        "Shipment Mix",
    ],
    x_label="Quarter",
    y_label="Percent",
)


# --------------------------------------------------
# Initial interpretation
# --------------------------------------------------

st.info(
    """
    Smoke-free products account for roughly
    41–43% of PMI revenue while representing
    roughly 22–25% of equivalent-unit shipment
    volume in the periods shown.

    The gap is economically significant, but
    shipment units and revenue are not directly
    comparable measures of profitability.
    """
)

# --------------------------------------------------
# Two economic engines
# --------------------------------------------------

st.divider()

st.header("Two Economic Engines")

st.markdown(
    """
    PMI's transformation is being powered by two
    businesses with very different growth profiles.

    **International Smoke-Free** is growing primarily
    through expansion in volume and mix, while
    **International Combustibles** continues to
    generate growth despite mature cigarette volumes.
    """
)

st.subheader(f"Performance in {latest_period}")


# --------------------------------------------------
# International Smoke-Free
# --------------------------------------------------

st.markdown("### International Smoke-Free")

sfp_col1, sfp_col2, sfp_col3 = st.columns(3)

with sfp_col1:
    st.metric(
        "Revenue Growth",
        f"{latest['intl_sfp_revenue_growth']:.1%}",
    )

with sfp_col2:
    st.metric(
        "Gross Profit Growth",
        f"{latest['intl_sfp_gross_profit_growth']:.1%}",
    )

with sfp_col3:
    st.metric(
        "Gross Margin",
        f"{latest['intl_sfp_gross_margin']:.1%}",
        delta=(
            f"{latest['intl_sfp_gross_margin_change_pp']:.1f} pp"
        ),
    )


# --------------------------------------------------
# International Combustibles
# --------------------------------------------------

st.markdown("### International Combustibles")

comb_col1, comb_col2, comb_col3 = st.columns(3)

with comb_col1:
    st.metric(
        "Revenue Growth",
        f"{latest['intl_comb_revenue_growth']:.1%}",
    )

with comb_col2:
    st.metric(
        "Gross Profit Growth",
        f"{latest['intl_comb_gross_profit_growth']:.1%}",
    )

with comb_col3:
    st.metric(
        "Gross Margin",
        f"{latest['intl_comb_gross_margin']:.1%}",
        delta=(
            f"{latest['intl_comb_gross_margin_change_pp']:.1f} pp"
        ),
    )

# --------------------------------------------------
# Growth mechanism
# --------------------------------------------------

st.subheader("Different Paths to Growth")

growth_col1, growth_col2 = st.columns(2)

with growth_col1:
    st.markdown("#### Smoke-Free")

    st.metric(
        "Product Revenue Growth",
        f"{latest['smoke_free_revenue_growth']:.1%}",
    )

    st.metric(
        "Shipment Volume Growth",
        f"{latest['smoke_free_volume_growth']:.1%}",
    )

with growth_col2:
    st.markdown("#### Combustibles")

    st.metric(
        "Product Revenue Growth",
        f"{latest['combustible_revenue_growth']:.1%}",
    )

    st.metric(
        "Cigarette Volume Growth",
        f"{latest['cigarette_volume_growth']:.1%}",
    )

st.info(
    """
    The contrast is important: smoke-free revenue
    growth is accompanied by substantial shipment
    growth, while combustible revenue is growing
    much faster than cigarette volume.

    The growth-driver analysis below helps explain
    the difference.
    """
)

# --------------------------------------------------
# Growth drivers
# --------------------------------------------------

st.subheader("What Is Driving the Growth?")

st.markdown(
    """
    PMI's reported growth bridges show a very
    different economic mechanism inside each
    international business.

    Values below show the contribution to
    year-over-year revenue change in millions
    of U.S. dollars.
    """
)


latest_drivers = drivers[
    (drivers["period_label"] == latest_period)
    & (drivers["metric_name"] == "revenue_change")
    & (
        drivers["driver_name"].isin(
            [
                "currency",
                "acquisitions_divestitures",
                "price",
                "volume_mix_other",
            ]
        )
    )
].copy()


driver_labels = {
    "currency": "Currency",
    "acquisitions_divestitures":
        "Acquisitions / Divestitures",
    "price": "Price",
    "volume_mix_other": "Volume / Mix / Other",
}

latest_drivers["driver_label"] = (
    latest_drivers["driver_name"]
    .map(driver_labels)
)


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def make_driver_chart(data, segment_name):

    chart_data = data[
        data["segment_name"] == segment_name
    ].copy()

    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X(
                "value_millions:Q",
                title="Contribution to Revenue Change ($ millions)",
            ),
            y=alt.Y(
                "driver_label:N",
                title=None,
                sort=[
                    "Price",
                    "Volume / Mix / Other",
                    "Currency",
                    "Acquisitions / Divestitures",
                ],
                axis=alt.Axis(
                    labelLimit=190,
                ),
            ),
            color=alt.condition(
                alt.datum.value_millions >= 0,
                alt.value("#2E7D32"),
                alt.value("#C62828"),
            ),
            tooltip=[
                alt.Tooltip(
                    "driver_label:N",
                    title="Driver",
                ),
                alt.Tooltip(
                    "value_millions:Q",
                    title="$ millions",
                    format=",.0f",
                ),
            ],
        )
        .properties(
            height=250,
        )
    )

    labels = (
        alt.Chart(chart_data)
        .mark_text(
            align="left",
            baseline="middle",
            dx=5,
        )
        .encode(
            x=alt.X(
                "value_millions:Q",
            ),
            y=alt.Y(
                "driver_label:N",
                sort=[
                    "Price",
                    "Volume / Mix / Other",
                    "Currency",
                    "Acquisitions / Divestitures",
                ],
            ),
            text=alt.Text(
                "value_millions:Q",
                format="+,.0f",
            ),
        )
    )

    zero_line = (
        alt.Chart(
            pd.DataFrame({"x": [0]})
        )
        .mark_rule(
            color="#888888",
            strokeWidth=1,
        )
        .encode(
            x="x:Q"
        )
    )

    return chart + zero_line + labels

driver_col1, driver_col2 = st.columns(2)


with driver_col1:

    st.markdown(
        "#### International Smoke-Free"
    )

    sfp_driver_chart = make_driver_chart(
        latest_drivers,
        "international_smoke_free",
    )

    st.altair_chart(
        sfp_driver_chart,
        use_container_width=True,
    )


with driver_col2:

    st.markdown(
        "#### International Combustibles"
    )

    comb_driver_chart = make_driver_chart(
        latest_drivers,
        "international_combustibles",
    )

    st.altair_chart(
        comb_driver_chart,
        use_container_width=True,
    )

st.success(
    """
    **Two engines, two growth mechanisms.**

    International Smoke-Free growth is primarily
    volume/mix driven. International Combustibles
    relies much more heavily on pricing, which is
    offsetting volume/mix pressure.
    """
)

# --------------------------------------------------
# Smoke-free product engine
# --------------------------------------------------

st.divider()

st.header("Inside the Smoke-Free Engine")

st.markdown(
    """
    Smoke-free growth is not a single product story.
    PMI's portfolio spans heated tobacco, oral
    smoke-free products, and e-vapor products.
    """
)

# Prepare latest-period product data
latest_products = products[
    products["period_label"] == latest_period
].copy()

product_labels = {
    "htu": "Heated Tobacco",
    "oral_sfp": "Oral Smoke-Free",
    "e_vapor": "E-Vapor",
}

latest_products["product_label"] = (
    latest_products["product_name"]
    .map(product_labels)
)


# --------------------------------------------------
# Shipment volume chart
# --------------------------------------------------

st.subheader(
    f"Smoke-Free Shipment Volume — {latest_period}"
)

volume_chart = (
    alt.Chart(latest_products)
    .mark_bar()
    .encode(
        x=alt.X(
            "shipment_volume:Q",
            title="Shipment Volume (billions of equivalent units)",
            scale=alt.Scale(
                domain=[0, 48],
            ),
        ),
        y=alt.Y(
            "product_label:N",
            title=None,
            sort="-x",
            axis=alt.Axis(
                labelLimit=180,
            ),
        ),
        tooltip=[
            alt.Tooltip(
                "product_label:N",
                title="Product",
            ),
            alt.Tooltip(
                "shipment_volume:Q",
                title="Volume (B)",
                format=".1f",
            ),
        ],
    )
    .properties(
        height=220,
    )
)

volume_labels = (
    alt.Chart(latest_products)
    .mark_text(
        align="left",
        baseline="middle",
        dx=6,
    )
    .encode(
        x=alt.X(
            "shipment_volume:Q",
            scale=alt.Scale(
                domain=[0, 48],
            ),
        ),
        y=alt.Y(
            "product_label:N",
            sort="-x",
        ),
        text=alt.Text(
            "shipment_volume:Q",
            format=".1f",
        ),
    )
)

st.altair_chart(
    volume_chart + volume_labels,
    use_container_width=True,
)


# --------------------------------------------------
# Growth chart
# --------------------------------------------------

st.subheader("Year-over-Year Product Growth")

growth_chart = (
    alt.Chart(latest_products)
    .mark_bar()
    .encode(
        x=alt.X(
            "volume_yoy_pct:Q",
            title="Year-over-Year Volume Growth",
            axis=alt.Axis(
                format=".0%",
            ),
            scale=alt.Scale(
                domain=[-0.08, 0.52],
            ),
        ),
        y=alt.Y(
            "product_label:N",
            title=None,
            sort="-x",
            axis=alt.Axis(
                labelLimit=180,
            ),
        ),
        color=alt.condition(
            alt.datum.volume_yoy_pct >= 0,
            alt.value("#2E7D32"),
            alt.value("#C62828"),
        ),
        tooltip=[
            alt.Tooltip(
                "product_label:N",
                title="Product",
            ),
            alt.Tooltip(
                "volume_yoy_pct:Q",
                title="YoY Growth",
                format=".1%",
            ),
            alt.Tooltip(
                "volume_change:Q",
                title="Volume Change (B)",
                format="+.1f",
            ),
        ],
    )
    .properties(
        height=220,
    )
)

growth_labels_positive = (
    alt.Chart(
        latest_products[
            latest_products["volume_yoy_pct"] >= 0
        ]
    )
    .mark_text(
        align="left",
        baseline="middle",
        dx=6,
    )
    .encode(
        x=alt.X(
            "volume_yoy_pct:Q",
            scale=alt.Scale(
                domain=[-0.08, 0.52],
            ),
        ),
        y=alt.Y(
            "product_label:N",
            sort="-x",
        ),
        text=alt.Text(
            "volume_yoy_pct:Q",
            format="+.1%",
        ),
    )
)

growth_labels_negative = (
    alt.Chart(
        latest_products[
            latest_products["volume_yoy_pct"] < 0
        ]
    )
    .mark_text(
        align="right",
        baseline="middle",
        dx=-6,
    )
    .encode(
        x=alt.X(
            "volume_yoy_pct:Q",
            scale=alt.Scale(
                domain=[-0.08, 0.52],
            ),
        ),
        y=alt.Y(
            "product_label:N",
            sort="-x",
        ),
        text=alt.Text(
            "volume_yoy_pct:Q",
            format="+.1%",
        ),
    )
)

st.altair_chart(
    growth_chart
    + growth_labels_positive
    + growth_labels_negative,
    use_container_width=True,
)

# --------------------------------------------------
# Financial outcome
# --------------------------------------------------

st.divider()

st.header("Financial Outcome")

st.markdown(
    """
    The transformation is occurring alongside strong
    company-level operating performance. But the
    improvement is not flowing uniformly through
    every financial measure.
    """
)

st.subheader(f"Company Performance — {latest_period}")

fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)

with fin_col1:
    st.metric(
        "Revenue Growth",
        f"{latest['company_revenue_growth']:.1%}",
    )

with fin_col2:
    st.metric(
        "Operating Income Growth",
        f"{latest['company_operating_income_growth']:.1%}",
    )

with fin_col3:
    st.metric(
        "Operating Margin Change",
        f"{latest['company_operating_margin_change_pp']:.1f} pp",
    )

with fin_col4:
    st.metric(
        "Diluted EPS Growth",
        f"{latest['company_eps_growth']:.1%}",
    )


# IMPORTANT:
# This is outside all four column blocks.

st.info(
    """
    **A question for the next phase**

    PMI's operating performance is strengthening,
    but that improvement is not flowing directly
    through to GAAP diluted EPS.

    Explaining that divergence requires extending
    the model below operating income to examine
    interest expense, taxes, non-operating items,
    and other drivers of earnings per share.
    """
)

# --------------------------------------------------
# Sources and methodology
# --------------------------------------------------

st.divider()

st.header("Sources & Methodology")

st.markdown(
    """
    This project combines standardized financial data
    with operating disclosures from Philip Morris
    International's public filings.

    **Primary sources**

    - SEC Company Facts / XBRL for standardized company 
      financial measures such as revenue, operating income, 
      and diluted EPS.
    - PMI quarterly and annual SEC filings for product
      shipments, smoke-free revenue, segment economics,
      and growth-driver disclosures.

    **Analytical approach**

    Source data is collected and normalized in Python,
    stored in a dimensional SQLite model, and transformed
    into presentation-ready analytical datasets before
    reaching this dashboard.
    """
)

st.markdown("### Source Documents")

st.markdown(
    """
    The analysis is built from public company disclosures
    and regulatory filings. Key source libraries:

    - [PMI Earnings & Quarterly Materials](https://www.pmi.com/investor-relations/reports-filings)
    - [PMI Investor Relations](https://www.pmi.com/investor-relations/overview)
    - [PMI SEC Filings — EDGAR](https://www.sec.gov/edgar/browse/?CIK=0001413329)
    """
)

with st.expander("Important methodology notes"):

    st.markdown(
        """
        **Equivalent-unit shipments**  
        PMI reports smoke-free shipment categories using
        equivalent units. These provide a standardized
        volume measure across product categories, but
        should not be interpreted as economically
        identical units.

        **Product vs. segment reporting**  
        Product-level measures and reportable-segment
        measures represent different analytical
        dimensions. For example, total PMI smoke-free
        revenue is not equivalent to International
        Smoke-Free segment revenue because the U.S.
        segment contains smoke-free activity.

        **Quarterly derivations**  
        Where standalone fourth-quarter values are not
        directly reported, Q4 is derived from the
        full-year value less Q1, Q2, and Q3.

        **Recast segment data**  
        PMI changed its reportable segment structure
        effective in 2026. Comparative 2025 segment
        information used here reflects historical periods
        recast into the new reporting structure.

        **Rounding**  
        PMI reports several operating measures in rounded
        units. As a result, calculated component totals
        and growth contributions may differ slightly from
        reported totals.

        **Growth-driver bridges**  
        Revenue and gross-profit growth drivers are
        normalized from PMI's reported bridge disclosures.
        Driver contributions can exceed 100% of net change
        when positive factors are offset by negative ones.
        """
    )

    st.caption(
    """
    Independent analysis based on publicly available
    company disclosures. This project is not affiliated
    with or endorsed by Philip Morris International.
    """
    )

# --------------------------------------------------
# Project roadmap
# --------------------------------------------------

st.divider()

st.header("Where This Project Goes Next")

st.markdown(
    """
    V1 focuses on the economics of PMI's transformation.
    The underlying data model was designed to support
    additional analytical questions as the project evolves.
    """
)

roadmap_col1, roadmap_col2 = st.columns(2)

with roadmap_col1:

    st.markdown(
        """
        ### Guidance vs. Actuals

        Capture management guidance over time and compare
        subsequent results with the expectations management
        communicated to investors.

        ### The EPS Disconnect

        Extend the financial model below operating income
        to explain the divergence between operating
        performance and GAAP diluted EPS.

        ### PMI vs. Altria

        Compare two businesses with shared origins but
        increasingly different geographic footprints and
        smoke-free strategies.
        """
    )


with roadmap_col2:

    st.markdown(
        """
        ### Geographic Adoption

        Track smoke-free adoption across important markets,
        including HTU users, shipment growth, market share,
        and geographic expansion where disclosures allow.

        ### U.S. Smoke-Free Expansion

        Follow the development of PMI's U.S. smoke-free
        business, including ZYN and the developing IQOS
        rollout.
        """
    )

    st.caption(
    "Built as an evolving finance + data engineering research project."
    )