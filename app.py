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

EARNINGS_BRIDGE_FILE = (
    DATA_DIR
    / "earnings_bridge.csv"
)

EPS_RECONCILIATION_FILE = (
    DATA_DIR
    / "eps_reconciliation.csv"
)

EPS_ADJUSTMENT_HISTORY_FILE = (
    DATA_DIR
    / "eps_adjustment_history.csv"
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

    earnings_bridge = pd.read_csv(
        EARNINGS_BRIDGE_FILE
    )

    eps_reconciliation = pd.read_csv(
        EPS_RECONCILIATION_FILE
    )

    eps_adjustment_history = pd.read_csv(
        EPS_ADJUSTMENT_HISTORY_FILE
    )

    return (
        summary,
        drivers,
        products,
        earnings_bridge,
        eps_reconciliation,
        eps_adjustment_history,
    )

(
    summary,
    drivers,
    products,
    earnings_bridge,
    eps_reconciliation,
    eps_adjustment_history,
) = load_data()


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

# --------------------------------------------------
# EPS disconnect
# --------------------------------------------------

st.divider()

st.header("The EPS Disconnect")

st.markdown(
    """
    PMI's operating performance strengthened sharply
    in 2026-Q2, but reported diluted EPS moved in the
    opposite direction.

    Following earnings below operating income explains
    how both can be true.
    """
)

disconnect_col1, disconnect_col2 = st.columns(2)

with disconnect_col1:
    st.metric(
        "Operating Income Growth",
        f"{latest['company_operating_income_growth']:.1%}",
    )

with disconnect_col2:
    st.metric(
        "Reported Diluted EPS Growth",
        f"{latest['company_eps_growth']:.1%}",
    )

st.info(
    """
    **The question**

    How can operating income increase more than 20%
    while reported diluted EPS declines?
    """
)

# --------------------------------------------------
# Earnings bridge
# --------------------------------------------------

st.subheader(
    "Where Did the Operating Improvement Go?"
)

st.markdown(
    """
    Following earnings below operating income shows
    how PMI's strong operating improvement was offset
    before reaching shareholders.

    The bridge below shows each component's contribution
    to the year-over-year change in PMI-attributable
    earnings from 2025-Q2 to 2026-Q2.
    """
)

bridge_order = [
    "Operating Income",
    "Net Interest",
    "Non-Service Benefits",
    "Income Taxes",
    "Equity Investments",
    "RBH Impairment",
    "Noncontrolling Interest",
]

bridge_chart = (
    alt.Chart(earnings_bridge)
    .mark_bar()
    .encode(
        x=alt.X(
            "value_millions:Q",
            title="Impact on Year-over-Year Earnings Change ($ millions)",
        ),
        y=alt.Y(
            "component:N",
            title=None,
            sort=bridge_order,
            axis=alt.Axis(
                labelLimit=220,
            ),
        ),
        color=alt.condition(
            alt.datum.value_millions >= 0,
            alt.value("#2E7D32"),
            alt.value("#C62828"),
        ),
        tooltip=[
            alt.Tooltip(
                "component:N",
                title="Component",
            ),
            alt.Tooltip(
                "value_millions:Q",
                title="Impact ($M)",
                format="+,.0f",
            ),
        ],
    )
    .properties(
        height=320,
    )
)

bridge_labels_positive = (
    alt.Chart(
        earnings_bridge[
            earnings_bridge["value_millions"] >= 0
        ]
    )
    .mark_text(
        align="left",
        baseline="middle",
        dx=6,
    )
    .encode(
        x="value_millions:Q",
        y=alt.Y(
            "component:N",
            sort=bridge_order,
        ),
        text=alt.Text(
            "value_millions:Q",
            format="+,.0f",
        ),
    )
)

bridge_labels_negative = (
    alt.Chart(
        earnings_bridge[
            earnings_bridge["value_millions"] < 0
        ]
    )
    .mark_text(
        align="right",
        baseline="middle",
        dx=-6,
    )
    .encode(
        x="value_millions:Q",
        y=alt.Y(
            "component:N",
            sort=bridge_order,
        ),
        text=alt.Text(
            "value_millions:Q",
            format="+,.0f",
        ),
    )
)

bridge_zero_line = (
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

st.altair_chart(
    bridge_chart
    + bridge_zero_line
    + bridge_labels_positive
    + bridge_labels_negative,
    use_container_width=True,
)

bridge_total = (
    earnings_bridge["bridge_value"].sum()
)

st.success(
    """
**Strong operations were more than offset below operating income.**

Operating income improved by \\$818 million, but higher income taxes, weaker equity-investment results, the \\$511 million RBH impairment, and higher noncontrolling interests more than absorbed the gain.

Together, the bridge components reconcile to a **\\$222 million decline** in PMI-attributable earnings.
"""
)

# --------------------------------------------------
# Reported vs. adjusted EPS
# --------------------------------------------------

st.subheader(
    "Reported EPS vs. Adjusted EPS"
)

st.markdown(
    """
    The earnings bridge explains why GAAP earnings fell.
    PMI also reports an adjusted EPS measure that removes
    items management identifies as affecting comparability.

    That distinction materially changes the year-over-year
    picture in 2026-Q2.
    """
)

eps_comparison = eps_reconciliation[
    (
        (eps_reconciliation["year"] == 2025)
        & (eps_reconciliation["quarter"] == "Q2")
    )
    | (
        (eps_reconciliation["year"] == 2026)
        & (eps_reconciliation["quarter"] == "Q2")
    )
].copy()

eps_2025 = eps_comparison[
    eps_comparison["year"] == 2025
].iloc[0]

eps_2026 = eps_comparison[
    eps_comparison["year"] == 2026
].iloc[0]

reported_growth = (
    eps_2026["diluted_eps"]
    / eps_2025["diluted_eps"]
    - 1
)

adjusted_growth = (
    eps_2026["adjusted_eps"]
    / eps_2025["adjusted_eps"]
    - 1
)

reported_col, adjusted_col = st.columns(2)

with reported_col:
    st.markdown("### Reported EPS")

    st.metric(
        "2026-Q2",
        f"${eps_2026['diluted_eps']:.2f}",
        delta=f"{reported_growth:.1%} YoY",
    )

    st.caption(
        f"2025-Q2: ${eps_2025['diluted_eps']:.2f}"
    )

with adjusted_col:
    st.markdown("### Adjusted EPS")

    st.metric(
        "2026-Q2",
        f"${eps_2026['adjusted_eps']:.2f}",
        delta=f"{adjusted_growth:.1%} YoY",
    )

    st.caption(
        f"2025-Q2: ${eps_2025['adjusted_eps']:.2f}"
    )

st.subheader(
    "What Gets Adjusted?"
)

st.markdown(
    """
    PMI's adjusted EPS does not simply remove the RBH
    impairment. The reconciliation includes several
    adjustments, some positive and some negative.
    """
)

q2_2026_adjustments = (
    eps_adjustment_history[
        (eps_adjustment_history["year"] == 2026)
        & (eps_adjustment_history["quarter"] == "Q2")
    ]
    .copy()
)

adjustment_labels = {
    "Amortization of intangibles":
        "Amortization of Intangibles",
    "Fair value adjustment for equity security investments":
        "Investment Fair Value",
    "Swedish Match financing tax impact":
        "Swedish Match Financing Tax",
    "RBH equity investment impairment":
        "RBH Impairment",
    "Egypt sales tax settlement adjustment":
        "Egypt Sales Tax Settlement",
}

q2_2026_adjustments["adjustment_label"] = (
    q2_2026_adjustments["adjustment"]
    .map(adjustment_labels)
)

adjustment_order = [
    "Amortization of Intangibles",
    "Investment Fair Value",
    "Swedish Match Financing Tax",
    "RBH Impairment",
    "Egypt Sales Tax Settlement",
]

adjustment_chart = (
    alt.Chart(q2_2026_adjustments)
    .mark_bar()
    .encode(
        x=alt.X(
            "eps_impact:Q",
            title="Adjustment to Reported EPS ($ per share)",
        ),
        y=alt.Y(
            "adjustment_label:N",
            title=None,
            sort=adjustment_order,
            axis=alt.Axis(
                labelLimit=220,
            ),
        ),
        color=alt.condition(
            alt.datum.eps_impact >= 0,
            alt.value("#2E7D32"),
            alt.value("#C62828"),
        ),
        tooltip=[
            alt.Tooltip(
                "adjustment_label:N",
                title="Adjustment",
            ),
            alt.Tooltip(
                "eps_impact:Q",
                title="EPS Impact",
                format="+.2f",
            ),
        ],
    )
    .properties(
        height=250,
    )
)

st.altair_chart(
    adjustment_chart,
    use_container_width=True,
)

q2_adjustment_total = (
    q2_2026_adjustments["eps_impact"].sum()
)

st.info(
    f"""
Reported diluted EPS of **\\${eps_2026['diluted_eps']:.2f}**
plus **\\${q2_adjustment_total:.2f}** of net adjustments
reconciles to PMI's **\\${eps_2026['adjusted_eps']:.2f}
adjusted diluted EPS**.
"""
)

# --------------------------------------------------
# Adjustment history
# --------------------------------------------------

st.subheader(
    "How Unusual Are the Adjustments?"
)

st.markdown(
    """
    A single-quarter reconciliation cannot show whether
    an adjustment is genuinely unusual or part of a
    recurring difference between reported and adjusted EPS.

    Looking across the full period reveals both patterns.
    """
)

category_summary = (
    eps_adjustment_history[
        [
            "category",
            "quarters_present",
            "quarter_frequency",
            "cumulative_eps_impact",
        ]
    ]
    .drop_duplicates()
    .copy()
)

category_labels = {
    "amortization": "Amortization",
    "investment_valuation": "Investment Valuation",
    "tax_financing": "Financing Tax",
    "tax": "Other Tax",
    "impairment": "Impairments",
    "restructuring": "Restructuring",
    "divestiture": "Divestiture",
    "impairment_exit": "Impairment / Exit",
    "investment_other": "Other Investment",
    "litigation": "Litigation",
}

category_summary["category_label"] = (
    category_summary["category"]
    .map(category_labels)
)

category_summary = category_summary.sort_values(
    [
        "quarters_present",
        "cumulative_eps_impact",
    ],
    ascending=[
        False,
        False,
    ],
)

frequency_chart = (
    alt.Chart(category_summary)
    .mark_bar()
    .encode(
        x=alt.X(
            "quarters_present:Q",
            title="Quarters Present (out of 10)",
            scale=alt.Scale(
                domain=[0, 10],
            ),
        ),
        y=alt.Y(
            "category_label:N",
            title=None,
            sort="-x",
            axis=alt.Axis(
                labelLimit=180,
            ),
        ),
        tooltip=[
            alt.Tooltip(
                "category_label:N",
                title="Category",
            ),
            alt.Tooltip(
                "quarters_present:Q",
                title="Quarters Present",
            ),
            alt.Tooltip(
                "quarter_frequency:Q",
                title="Frequency",
                format=".0%",
            ),
            alt.Tooltip(
                "cumulative_eps_impact:Q",
                title="Cumulative EPS Impact",
                format="+.2f",
            ),
        ],
    )
    .properties(
        height=340,
    )
)

st.altair_chart(
    frequency_chart,
    use_container_width=True,
)

st.markdown(
    """
    ### Recurring Does Not Mean Economically Identical

    Frequency reveals that several adjustments recur
    regularly, but their behavior differs substantially.
    """
)

pattern_col1, pattern_col2, pattern_col3 = st.columns(3)

with pattern_col1:
    st.markdown(
        """
        **Persistent normalization**

        **Amortization** appears in all 10 quarters and
        consistently increases adjusted EPS.

        This is a recurring difference between PMI's
        reported and adjusted earnings measures rather
        than an isolated event.
        """
    )

with pattern_col2:
    st.markdown(
        """
        **Recurring volatility**

        **Investment valuation** also appears in all
        10 quarters, but its EPS impact moves in both
        directions.

        The adjustment removes volatility rather than
        consistently increasing adjusted earnings.
        """
    )

with pattern_col3:
    st.markdown(
        """
        **Episodic events**

        Impairments, restructuring, litigation, and
        divestiture-related items occur less consistently
        and can create unusually large effects in
        individual quarters.

        The RBH impairment is the clearest example.
        """
    )

st.info(
    """
**Reported and adjusted EPS answer different questions.**

GAAP EPS captures the full accounting result attributable
to shareholders, including the $511 million RBH impairment
that affected 2026-Q2.

PMI's adjusted EPS removes that impairment, but it also
normalizes items that recur frequently, including
amortization and investment-valuation effects.

The operating improvement is therefore real, and so is the
reported earnings decline. Understanding PMI's performance
requires seeing both rather than treating either measure as
the complete story.
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
    with operating and management disclosures from
    Philip Morris International's public filings and
    earnings materials.

    **Primary sources**

    - SEC Company Facts / XBRL for standardized company
      financial measures such as revenue, operating income,
      interest, taxes, net income, and diluted EPS.
    - PMI quarterly and annual SEC filings for product
      shipments, smoke-free revenue, segment economics,
      growth-driver disclosures, and other reported
      financial items.
    - PMI earnings releases for management's reported-to-
      adjusted EPS reconciliations and the individual
      adjustments underlying non-GAAP diluted EPS.

    **Analytical approach**

    Source data is collected and normalized in Python,
    stored or structured according to the needs of the
    source, and transformed into presentation-ready
    analytical datasets before reaching this dashboard.

    GAAP financial measures and management-adjusted
    measures are preserved separately so the analysis
    can compare them without treating either as a
    substitute for the other.
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

        **EPS reconciliation**  
        The earnings bridge follows PMI's reported financial
        statement structure below operating income rather than
        forcing the data into a generic income-statement model.
        Modeled components reconcile to PMI-attributable net
        earnings for the periods analyzed.

        **Reported vs. adjusted EPS**  
        Reported diluted EPS is a GAAP measure. Adjusted diluted
        EPS and its individual adjustments are management-defined
        non-GAAP measures reported by PMI. The dashboard preserves
        both measures separately and does not treat adjusted EPS
        as a replacement for the reported result.

        **Adjustment frequency**  
        Historical adjustment frequency measures how many of the
        10 quarters analyzed contain each adjustment category.
        Frequency alone does not establish whether an item is
        economically recurring, unusual, or appropriate to exclude.
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
    The project now connects PMI's operating transformation
    through to shareholder earnings. The underlying model
    is designed to support additional analytical questions
    as the project evolves.
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