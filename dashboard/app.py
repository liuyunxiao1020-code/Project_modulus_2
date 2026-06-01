import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = "my-project-learning-496207"
DATASET    = "ecommerce_marts"
KEY_FILE   = "/home/liuyx/Project/Project_modulus_2/credentials/gcp-key.json"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE
client = bigquery.Client(project=PROJECT_ID)

def query(sql):
    return client.query(sql).to_dataframe()

def load_summary():
    return query(f"""
        SELECT
            COUNT(DISTINCT order_id)       AS total_orders,
            COUNT(DISTINCT customer_key)   AS total_customers,
            COUNT(DISTINCT seller_key)     AS total_sellers,
            ROUND(SUM(item_price), 2)      AS total_revenue,
            ROUND(AVG(item_price), 2)      AS avg_order_value,
            ROUND(AVG(review_score), 2)    AS avg_review_score
        FROM `{PROJECT_ID}.{DATASET}.fact_orders`
    """)

def load_monthly_sales():
    return query(f"""
        SELECT
            FORMAT_DATE('%Y-%m', purchased_at) AS month,
            COUNT(DISTINCT order_id)           AS total_orders,
            ROUND(SUM(item_price), 2)          AS total_revenue
        FROM `{PROJECT_ID}.{DATASET}.fact_orders`
        WHERE purchased_at IS NOT NULL
        GROUP BY month ORDER BY month
    """)

def load_top_categories():
    return query(f"""
        SELECT
            p.category_english,
            COUNT(DISTINCT f.order_id)     AS total_orders,
            ROUND(SUM(f.item_price), 2)    AS total_revenue
        FROM `{PROJECT_ID}.{DATASET}.fact_orders` f
        LEFT JOIN `{PROJECT_ID}.{DATASET}.dim_products` p
            ON f.product_key = p.product_key
        WHERE p.category_english IS NOT NULL
        GROUP BY p.category_english
        ORDER BY total_revenue DESC LIMIT 10
    """)

def load_region_revenue():
    return query(f"""
        SELECT
            s.region,
            ROUND(SUM(f.item_price), 2)    AS total_revenue,
            COUNT(DISTINCT f.order_id)     AS total_orders,
            COUNT(DISTINCT s.seller_key)   AS total_sellers
        FROM `{PROJECT_ID}.{DATASET}.fact_orders` f
        LEFT JOIN `{PROJECT_ID}.{DATASET}.dim_sellers` s
            ON f.seller_key = s.seller_key
        WHERE s.region IS NOT NULL
        GROUP BY s.region ORDER BY total_revenue DESC
    """)

def load_order_status():
    return query(f"""
        SELECT order_status, COUNT(DISTINCT order_id) AS count
        FROM `{PROJECT_ID}.{DATASET}.fact_orders`
        GROUP BY order_status ORDER BY count DESC
    """)

def load_rfm():
    return query(f"""
        WITH max_date AS (
            SELECT MAX(DATE(purchased_at)) AS ref_date
            FROM `{PROJECT_ID}.{DATASET}.fact_orders`
        ),
        rfm AS (
            SELECT
                f.customer_key,
                DATE_DIFF(m.ref_date, DATE(MAX(f.purchased_at)), DAY) AS recency_days,
                COUNT(DISTINCT f.order_id)                             AS frequency,
                ROUND(SUM(f.item_price), 2)                           AS monetary
            FROM `{PROJECT_ID}.{DATASET}.fact_orders` f
            CROSS JOIN max_date m
            GROUP BY f.customer_key, m.ref_date
        )
        SELECT
            CASE
                WHEN recency_days <= 90  AND frequency >= 3 THEN 'Champions'
                WHEN recency_days <= 180 AND frequency >= 2 THEN 'Loyal Customers'
                WHEN recency_days <= 270                    THEN 'Potential Loyalists'
                WHEN recency_days <= 365                    THEN 'At Risk'
                ELSE 'Lost'
            END AS segment,
            COUNT(*)               AS customer_count,
            ROUND(AVG(monetary),2) AS avg_spend
        FROM rfm
        GROUP BY segment ORDER BY customer_count DESC
    """)

print("Loading data from BigQuery...")
summary        = load_summary()
monthly_sales  = load_monthly_sales()
top_categories = load_top_categories()
region_revenue = load_region_revenue()
order_status   = load_order_status()
rfm_segments   = load_rfm()
print("Data loaded successfully!")

# ── Colors ────────────────────────────────────────────────────────────
COLORS = {
    "bg":      "#0f1117",
    "card":    "#1a1d2e",
    "border":  "#2a2d3e",
    "accent1": "#4f8ef7",
    "accent2": "#00d4aa",
    "accent3": "#f7934f",
    "accent4": "#b24ff7",
    "text":    "#e8eaf6",
    "subtext": "#8b90a0",
}

# Only truly shared properties — no margin or legend here
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], family="DM Sans, sans-serif"),
)

# ── KPI card ─────────────────────────────────────────────────────────
def kpi_card(title, value, subtitle, color, icon):
    return dbc.Col(
        html.Div([
            html.Div(icon, style={
                "fontSize": "24px", "marginBottom": "12px",
                "background": "rgba(255,255,255,0.05)",
                "border": "1px solid rgba(255,255,255,0.1)",
                "borderRadius": "12px", "padding": "10px",
                "display": "inline-block",
            }),
            html.Div(value, style={
                "fontSize": "26px", "fontWeight": "700",
                "color": color, "letterSpacing": "-0.5px",
                "lineHeight": "1", "marginBottom": "4px",
            }),
            html.Div(title, style={
                "fontSize": "13px", "fontWeight": "600",
                "color": COLORS["text"], "marginBottom": "2px",
            }),
            html.Div(subtitle, style={
                "fontSize": "11px", "color": COLORS["subtext"],
            }),
        ], style={
            "background": COLORS["card"],
            "border": f"1px solid {COLORS['border']}",
            "borderRadius": "16px", "padding": "20px", "height": "100%",
        }),
        xs=12, sm=6, md=4, lg=2,
    )

# ── Charts ────────────────────────────────────────────────────────────
def make_revenue_chart():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_sales["month"],
        y=monthly_sales["total_revenue"],
        mode="lines+markers",
        name="Revenue",
        line=dict(color=COLORS["accent1"], width=2.5),
        marker=dict(size=5),
        fill="tozeroy",
        fillcolor="rgba(79, 142, 247, 0.1)",
    ))
    fig.add_trace(go.Bar(
        x=monthly_sales["month"],
        y=monthly_sales["total_orders"],
        name="Orders",
        yaxis="y2",
        marker_color="rgba(0, 212, 170, 0.35)",
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        title="Monthly Revenue & Order Volume",
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(title="Revenue (BRL)", gridcolor=COLORS["border"]),
        yaxis2=dict(title="Orders", overlaying="y", side="right",
                    gridcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor=COLORS["border"]),
    )
    fig.update_layout(legend=dict(
        orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)"
    ))
    return fig

def make_category_chart():
    fig = px.bar(
        top_categories,
        x="total_revenue", y="category_english", orientation="h",
        color="total_orders",
        color_continuous_scale=[[0, COLORS["accent1"]], [1, COLORS["accent2"]]],
        labels={"total_revenue": "Revenue (BRL)",
                "category_english": "", "total_orders": "Orders"},
        title="Top 10 Product Categories by Revenue",
    )
    fig.update_layout(
        **CHART_LAYOUT,
        height=360,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        coloraxis_colorbar=dict(title="Orders"),
    )
    fig.update_traces(marker_line_width=0)
    return fig

def make_region_chart():
    fig = px.pie(
        region_revenue, names="region", values="total_revenue", hole=0.6,
        color_discrete_sequence=[
            COLORS["accent1"], COLORS["accent2"],
            COLORS["accent3"], COLORS["accent4"], "#f74f6e"
        ],
        title="Revenue by Seller Region",
    )
    fig.update_layout(
        **CHART_LAYOUT,
        height=320,
        margin=dict(l=20, r=120, t=40, b=20),
    )
    fig.update_layout(legend=dict(
        orientation="v",
        x=1.05, y=0.5,
        xanchor="left", yanchor="middle",
        font=dict(size=12),
        bgcolor="rgba(0,0,0,0)",
    ))
    fig.update_traces(
        textinfo="percent",
        textposition="inside",
        textfont=dict(size=13, color="white"),
        pull=[0, 0, 0.05, 0.08, 0.1],
        hovertemplate="<b>%{label}</b><br>Revenue: R$%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )
    return fig

def make_status_chart():
    fig = px.bar(
        order_status, x="order_status", y="count",
        color="order_status",
        color_discrete_sequence=[
            COLORS["accent2"], COLORS["accent1"], COLORS["accent3"],
            COLORS["accent4"], "#f74f6e", "#f7e44f", "#4ff7b2"
        ],
        title="Orders by Status",
        labels={"order_status": "", "count": "Count (log scale)"},
        text=order_status["count"].apply(lambda x: f"{x:,}"),
    )
    fig.update_layout(
        **CHART_LAYOUT,
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(
            gridcolor=COLORS["border"],
            type="log",           # log scale so small bars are visible
            tickformat=",",
        ),
    )
    fig.update_traces(
        marker_line_width=0,
        textposition="outside",
        textfont=dict(color=COLORS["text"], size=10),
    )
    return fig

def make_rfm_chart():
    fig = px.bar(
        rfm_segments, x="segment", y="customer_count",
        color="avg_spend",
        color_continuous_scale=[[0, COLORS["accent1"]], [1, COLORS["accent3"]]],
        title="Customer Segments (RFM Analysis)",
        labels={"segment": "Segment", "customer_count": "Customers",
                "avg_spend": "Avg Spend (BRL)"},
        text="customer_count",
    )
    fig.update_layout(
        **CHART_LAYOUT,
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor=COLORS["border"]),
        coloraxis_colorbar=dict(title="Avg Spend"),
    )
    fig.update_traces(
        marker_line_width=0,
        textposition="outside",
        textfont=dict(color=COLORS["text"]),
    )
    return fig

# ── KPI values ────────────────────────────────────────────────────────
s               = summary.iloc[0]
total_revenue   = f"R${s['total_revenue']:,.0f}"
total_orders    = f"{s['total_orders']:,}"
total_customers = f"{s['total_customers']:,}"
total_sellers   = f"{s['total_sellers']:,}"
avg_order_val   = f"R${s['avg_order_value']:,.2f}"
avg_review      = f"{s['avg_review_score']:.1f} / 5"

# ── App ───────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap"
    ],
    title="Olist Analytics Dashboard"
)

app.layout = html.Div([

    # ── Header ────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div([
                html.Span("◈", style={"color": COLORS["accent1"],
                          "fontSize": "28px", "marginRight": "12px"}),
                html.Span("OLIST", style={
                    "fontFamily": "Space Mono, monospace",
                    "fontWeight": "700", "fontSize": "20px",
                    "color": COLORS["text"], "letterSpacing": "4px",
                }),
                html.Span(" ANALYTICS", style={
                    "fontFamily": "Space Mono, monospace",
                    "fontWeight": "400", "fontSize": "20px",
                    "color": COLORS["accent2"], "letterSpacing": "4px",
                }),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div([
                html.Span("● LIVE", style={
                    "color": COLORS["accent2"], "fontSize": "11px",
                    "fontFamily": "Space Mono, monospace",
                    "letterSpacing": "2px",
                }),
                html.Span(" | Brazilian E-Commerce | 2016–2018", style={
                    "color": COLORS["subtext"], "fontSize": "11px",
                    "marginLeft": "8px",
                }),
            ]),
        ], style={
            "maxWidth": "1400px", "margin": "0 auto",
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "center",
        }),
    ], style={
        "background": f"linear-gradient(90deg, {COLORS['card']}, #12152a)",
        "borderBottom": f"1px solid {COLORS['border']}",
        "padding": "16px 24px",
    }),

    # ── Main content ──────────────────────────────────────────────────
    html.Div([

        # KPI row
        html.Div([
            html.Div("KEY METRICS", style={
                "fontFamily": "Space Mono, monospace", "fontSize": "10px",
                "color": COLORS["subtext"], "letterSpacing": "3px",
                "marginBottom": "12px",
            }),
            dbc.Row([
                kpi_card("Total Revenue",    total_revenue,
                         "All time",          COLORS["accent1"], "💰"),
                kpi_card("Total Orders",     total_orders,
                         "Processed",         COLORS["accent2"], "📦"),
                kpi_card("Total Customers",  total_customers,
                         "Unique buyers",     COLORS["accent3"], "👤"),
                kpi_card("Total Sellers",    total_sellers,
                         "Active merchants",  COLORS["accent4"], "🏪"),
                kpi_card("Avg Order Value",  avg_order_val,
                         "Per line item",     "#f74f6e",         "🧾"),
                kpi_card("Avg Review Score", avg_review,
                         "Customer rating",   COLORS["accent2"], "⭐"),
            ], className="g-3"),
        ], style={"marginBottom": "24px"}),

        # Row 1: Revenue trend + Order status
        dbc.Row([
            dbc.Col(html.Div(
                dcc.Graph(figure=make_revenue_chart(),
                          config={"displayModeBar": False}),
                style={"background": COLORS["card"], "borderRadius": "16px",
                       "border": f"1px solid {COLORS['border']}",
                       "padding": "16px"}
            ), md=8),
            dbc.Col(html.Div(
                dcc.Graph(figure=make_status_chart(),
                          config={"displayModeBar": False}),
                style={"background": COLORS["card"], "borderRadius": "16px",
                       "border": f"1px solid {COLORS['border']}",
                       "padding": "16px"}
            ), md=4),
        ], className="g-3 mb-3"),

        # Row 2: Top categories
        dbc.Row([
            dbc.Col(html.Div(
                dcc.Graph(figure=make_category_chart(),
                          config={"displayModeBar": False}),
                style={"background": COLORS["card"], "borderRadius": "16px",
                       "border": f"1px solid {COLORS['border']}",
                       "padding": "16px"}
            ), md=12),
        ], className="g-3 mb-3"),

        # Row 3: Region pie + RFM segments
        dbc.Row([
            dbc.Col(html.Div(
                dcc.Graph(figure=make_region_chart(),
                          config={"displayModeBar": False}),
                style={"background": COLORS["card"], "borderRadius": "16px",
                       "border": f"1px solid {COLORS['border']}",
                       "padding": "16px"}
            ), md=4),
            dbc.Col(html.Div(
                dcc.Graph(figure=make_rfm_chart(),
                          config={"displayModeBar": False}),
                style={"background": COLORS["card"], "borderRadius": "16px",
                       "border": f"1px solid {COLORS['border']}",
                       "padding": "16px"}
            ), md=8),
        ], className="g-3 mb-3"),

        # Footer
        html.Div([
            html.Span("Built with Dash + Plotly + BigQuery",
                      style={"color": COLORS["subtext"], "fontSize": "11px",
                             "fontFamily": "Space Mono, monospace"}),
            html.Span(" | Data Engineering Project 2026",
                      style={"color": COLORS["subtext"], "fontSize": "11px"}),
        ], style={"textAlign": "center", "padding": "24px 0 8px"}),

    ], style={"maxWidth": "1400px", "margin": "0 auto", "padding": "24px"}),

], style={
    "background": COLORS["bg"],
    "minHeight": "100vh",
    "fontFamily": "DM Sans, sans-serif",
})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)