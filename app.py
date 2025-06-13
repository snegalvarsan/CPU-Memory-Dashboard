import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import requests
import plotly.graph_objs as go
from flask import Flask, Response
import os

server = Flask(__name__)
DATA_URL = os.getenv("DATA_URL", "http://35.154.27.230/data")

def fetch_data():
    response = requests.get(DATA_URL)
    response.raise_for_status()
    df = pd.DataFrame(response.json())
    df = df.sort_values(by="time")
    df["time"] = pd.to_datetime(df["time"])
    return df

app = dash.Dash(__name__, server=server, url_base_pathname="/", suppress_callback_exceptions=True)
app.title = "CPU & Memory Monitor"

app.layout = html.Div([
    html.Div([
        html.H2("CPU & Memory Monitor", style={"margin-bottom": "10px"}),
        html.Div(id="stats-summary", style={"margin-bottom": "20px"}),
        html.Div([
            html.Button("Pause Updates", id="pause-btn", className="btn", n_clicks=0),
            #html.Button("Download CSV", id="download-btn", className="btn"),
            #html.A("⬇️ Download Now", id="download-link", href="/download", className="btn", style={"display": "none"})
	    html.A("⬇️ Download CSV", href="/download", className="btn", target="_blank")
        ]),

        html.Br(),
        html.Label("Select Time Range:"),
        dcc.DatePickerRange(
            id='date-range',
            display_format='YYYY-MM-DD',
            minimum_nights=0,
            clearable=True,
        ),
    ], style={"padding": "10px"}),

    dcc.Graph(id="usage-graph"),

    dcc.Interval(id="refresh", interval=15 * 1000, n_intervals=0),

    html.Div(id="spike-info", style={"margin-top": "10px", "font-weight": "bold"}),
])

@app.callback(
    Output("refresh", "disabled"),
    Output("pause-btn", "children"),
    Input("pause-btn", "n_clicks"),
    State("refresh", "disabled")
)
def toggle_refresh(n, is_disabled):
    if n is None:
        raise dash.exceptions.PreventUpdate
    return not is_disabled, "Resume Updates" if not is_disabled else "Pause Updates"

@app.callback(
    Output("usage-graph", "figure"),
    Output("stats-summary", "children"),
    Output("spike-info", "children"),
    Input("refresh", "n_intervals"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_graph(_, start_date, end_date):
    df = fetch_data()

    if start_date and end_date:
      df = df[(df["time"] >= start_date) & (df["time"] <= end_date)]

    spikes = df[df["cpu"] > 3]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["cpu"], mode="lines", name="CPU"))
    fig.add_trace(go.Scatter(x=df["time"], y=df["memory"], mode="lines", name="Memory"))
    fig.add_trace(go.Scatter(x=spikes["time"], y=spikes["cpu"], mode="markers", name="Spikes", marker=dict(color="red", size=8)))

    fig.update_layout(
        title="CPU and Memory Usage Over Time",
        xaxis_title="Time",
        yaxis_title="Usage",
        template="plotly_white"
    )

    def color_level(val, max_val):
        if val > max_val * 0.85:
            return "red"
        elif val > max_val * 0.5:
            return "orange"
        return "green"

    stats = html.Div([
        html.P([
            html.Span("Latest CPU: ", style={"font-weight": "bold"}),
            html.Span(f"{df.iloc[-1]['cpu']}", style={"color": color_level(df.iloc[-1]['cpu'], df['cpu'].max())}),
            html.Span(" | "),
            html.Span("Latest Memory: ", style={"font-weight": "bold"}),
            html.Span(f"{df.iloc[-1]['memory']}", style={"color": color_level(df.iloc[-1]['memory'], df['memory'].max())}),
        ]),
        html.P(f"Avg CPU: {df['cpu'].mean():.2f}, Max CPU: {df['cpu'].max()}"),
        html.P(f"Avg Memory: {df['memory'].mean():.2f}, Max Memory: {df['memory'].max()}"),
    ])

    spike_info = f"Spike Count: {len(spikes)} | Last Spike: {spikes['time'].max() if not spikes.empty else 'None'}"

    return fig, stats, spike_info

@server.route("/download")
def download_csv():
    df = fetch_data()
    csv = df.to_csv(index=False)
    return Response(csv, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=metrics.csv"})

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8000, debug=True)

