import requests
import json
import pandas as pd
import plotly.express as px
from pandas import json_normalize
from dash import Dash, Input, Output, dcc, html
from datetime import timedelta
import numpy as np


#url = "https://fleetserver/api/v1/fleet/hosts"
payload={}
headers = {
    #'Authorization': 'Bearer <token>'
}

response = requests.request("GET", url, headers=headers, data=payload)

hosts = response.json()
host_data = json_normalize(hosts['hosts'])

# Data Handling
host_data["created_at"] = pd.to_datetime(host_data["created_at"], format="%Y-%m-%d")
host_data["team_name"].fillna('No Team', inplace=True)

platforms = host_data["os_version"]
hw_manufacturers = host_data["hardware_vendor"]
status = host_data["status"]
failing_policies = host_data["issues.failing_policies_count"]


#external_stylesheets = [
#    {
#        "href": (
#            "https://fonts.googleapis.com/css2?"
#            "family=Lato:wght@400;700&display=swap"
#        ),
#        "rel": "stylesheet",
#    },
#]

#app = Dash(__name__, external_stylesheets=external_stylesheets)
app = Dash(__name__)
app.title = "Fleet Dashboard"

app.layout = html.Div(children=[
        html.Div(children=[
                html.Img(
                    src="assets/fleet-logo.png",
                    style={
                    'height':'45%', 
                    'width':'4%', 
                    'margin': '10px'
                    }
                ),
            ],
            className="header",),
            html.Div(children=[
                html.Div(children=[
                        html.Div(children="status", className="menu-title"),
                        dcc.Dropdown(
                            id="status-filter",
                            options=[
                                {"label": status, "value": status}
                                for status in np.sort(host_data.status.unique())
                            ],
                            value="online",
                            clearable=False,
                            className="Dropdown",
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(children=[
                html.Div(
                    children=dcc.Graph(
                        id="device-uptime-chart",
                        config={"displayModeBar": False},
                    ), 
                    className="card",),
                html.Div(children=
                    dcc.Graph(
                        id="failing-policies-chart",
                        config={"displayModeBar": False}, 
                    ), 
                    className="card",style={'width': '50%', 'display': 'inline-block'}),
                html.Div(children=
                    dcc.Graph(
                        id="failing-policies-team-chart",
                        config={"displayModeBar": False},
                    ),className="card",style={'width': '50%', 'display': 'inline-block'}),
                html.Div(children=
                    dcc.Graph(
                        id="os-chart",
                        config={"displayModeBar": False},
                    ),className="card",style={'width': '50%', 'display': 'inline-block'}),
                html.Div(children=
                    dcc.Graph(
                        id="hardware-chart",
                        config={"displayModeBar": False},
                    ),className="card",style={'width': '50%', 'display': 'inline-block'}),
                html.Div(children=
                    dcc.Graph(
                        id="disk-space-chart",
                        config={"displayModeBar": False},
                    ),className="card",style={'width': '100%', 'display': 'inline-block'}),
            ],
        className="wrapper",),
    ]
)


@app.callback(
    [Output("device-uptime-chart", "figure"), Output("failing-policies-chart", "figure"),
     Output("failing-policies-team-chart", "figure"), Output("os-chart", "figure"),
     Output("hardware-chart", "figure"),Output("disk-space-chart", "figure")],
    [
        Input("status-filter", "value"),
    ],
)
def update_charts(status):
    #url = "https://fleetserver/api/v1/fleet/hosts"
    payload={}
    headers = {
    #'Authorization': 'Bearer <token>'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    hosts = response.json()
    print(hosts)
    #host_data = json_normalize(hosts['hosts'])

    # Conversions
    host_data["created_at"] = pd.to_datetime(host_data["created_at"], format="%Y-%m-%d")
    host_data["team_name"].fillna('No Team', inplace=True)

    mask = (
        (host_data.status == status)
    )
    filtered_data = host_data.loc[mask, :]
    device_uptime_chart_figure = {
        "data": [
            {
                "x": filtered_data["hostname"],
                "y": filtered_data["uptime"].div(3600000000000),
                "type": "bar",
                "opacity": "0.7",
                "meta": filtered_data["seen_time"],
                "hovertemplate": (
                    "%{y:.1f} hours <extra>last checkin: %{meta}</extra>"
                ),
            },
        ],
        "layout": {
            "paper_bgcolor": 'rgba(0,0,0,0)',
            "style": { 
                'border-radius':'15px', 
                },
            "title": {
                "text": "Device uptime",
                "x": 0.05,
                "xanchor": "left",
        },
            "xaxis": {"fixedrange": True},
            "yaxis": {
                "fixedrange": False,
            },
            "colorway": ['#636EFA'],
        },
    }

    failing_policies_chart_figure = {
        "data": [
            {
                "labels": filtered_data["hostname"],
                "values": filtered_data["issues.failing_policies_count"],
                "type": "pie",
                "opacity": "0.7",
                "hole": ".3",
                "showlegend": False,
                "hovertemplate": (
                    ""
                ),
            },
        ],
        "layout": {
            "paper_bgcolor": 'rgba(0,0,0,0)',
            "style": { 
                'border-radius':'15px', 
                },
            "title": {
                "text": "Compliance policy failures",
                "x": 0.5,
            },
            "colorway": ['#FF6692', '#B6E880', '#FF97FF', '#FECB52'],
        },
    }
    
    failing_policies_team_chart_figure = {
        "data": [
            {
                "labels": filtered_data["team_name"],
                "values": filtered_data["issues.failing_policies_count"],
                "type": "pie",
                "opacity": "0.7",
                "hole": ".3",
                "showlegend": False,
                "hovertemplate": (
                    ""
                ),
            },
        ],
        "layout": {
            "paper_bgcolor": 'rgba(0,0,0,0)',
            "style": { 
                'border-radius':'15px', 
                },
            "title": {
                "text": "Compliance policy failures by team",
                "x": 0.80,
                "xanchor": "right",
            },
            "colorway": ['#FF6692', '#B6E880', '#FF97FF', '#FECB52'],
        },
    }

    os_chart_figure = {
        "data": [
            {
                "labels": filtered_data["os_version"],
                #"values": filtered_data["os_version"],
                "type": "pie",
                "opacity": "0.7",
                "hole": ".3",
                "showlegend": False,
                "hovertemplate": (
                    ""
                ),
            },
        ],
        "layout": {
            "paper_bgcolor": 'rgba(0,0,0,0)',
            "style": { 
                'border-radius':'15px', 
                },
            "title": {
                "text": "Operating System Distribution",
                "x": 0.25,
                "xanchor": "left",
            },
            "colorway": ['#FF6692', '#B6E880', '#FF97FF', '#FECB52'],
        },
    }

    hardware_chart_figure = {                      
        "data": [
            {
                "labels": filtered_data["hardware_model"],
                #"values": filtered_data["os_version"],
                "type": "pie",
                "opacity": "0.7",
                "hole": ".3",
                "showlegend": False,
                "hovertemplate": (
                    ""
                ),
            },
        ],
        "layout": {
            "paper_bgcolor": 'rgba(0,0,0,0)',
            "style": { 
                'border-radius':'15px', 
                },
            "title": {
                "text": "Hardware distribution",
                "x": 0.7,
                "xanchor": "right",
            },
            "colorway": ['#FF6692', '#B6E880', '#FF97FF', '#FECB52'],
        },
    }
    disk_space_chart_figure = {
        "data": [
            {
                "x": filtered_data["hostname"],
                "y": filtered_data["percent_disk_space_available"],
                "type": "bar",
                "opacity": "0.7",
                "meta": filtered_data["seen_time"],
                "hovertemplate": (
                    "%{y:.1f} % <extra>last checkin: %{meta}</extra>"
                ),
            },
        ],
        "layout": {
            "paper_bgcolor": 'rgba(0,0,0,0)',
            "style": { 
                'border-radius':'15px', 
                },
            "title": {
                "text": "Percent disk space available",
                "x": 0.05,
                "xanchor": "left",
        },
            "xaxis": {"fixedrange": True},
            "yaxis": {
                "fixedrange": False,
            },
            "colorway": ['#636EFA'],
        },
    }

    
    return device_uptime_chart_figure, failing_policies_chart_figure,failing_policies_team_chart_figure, os_chart_figure, hardware_chart_figure, disk_space_chart_figure

if __name__ == "__main__":
    app.run_server(debug=True)
