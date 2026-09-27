
# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create the app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'font-size': 40
        }
    ),

    # TASK 1: Launch Site Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [
            {'label': site, 'value': site}
            for site in spacex_df['Launch Site'].unique()
        ],
        value='ALL',
        placeholder='Select a Launch Site',
        searchable=True
    ),

    html.Br(),

    # TASK 2: Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload],
        marks={
            0: '0',
            2500: '2500',
            5000: '5000',
            7500: '7500',
            10000: '10000'
        }
    ),

    # TASK 4: Scatter Chart
    html.Div(dcc.Graph(
        id='success-payload-scatter-chart'
    ))
])

# TASK 2: Pie Chart Callback
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):

    if entered_site == 'ALL':
        # Count successful launches at each site
        success_df = spacex_df[spacex_df['class'] == 1]

        site_counts = (
            success_df.groupby('Launch Site')
            .size()
            .reset_index(name='Success Count')
        )

        fig = px.pie(
            site_counts,
            names='Launch Site',
            values='Success Count',
            title='Total Successful Launches by Site'
        )

    else:
        # Count successes and failures for selected site
        filtered_df = spacex_df[
            spacex_df['Launch Site'] == entered_site
        ]

        outcome_counts = (
            filtered_df['class']
            .value_counts()
            .reindex([0, 1], fill_value=0)
            .rename_axis('Outcome')
            .reset_index(name='Count')
        )

        outcome_counts['Outcome'] = (
            outcome_counts['Outcome']
            .map({0: 'Failure', 1: 'Success'})
        )

        fig = px.pie(
            outcome_counts,
            names='Outcome',
            values='Count',
            title=f'Success vs. Failure for {entered_site}'
        )

    return fig

# TASK 4: Scatter Plot Callback
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def get_scatter_plot(entered_site, payload_range):

    low, high = payload_range

    # Filter by selected site
    if entered_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[
            spacex_df['Launch Site'] == entered_site
        ]

    # Filter by payload range
    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= low) &
        (filtered_df['Payload Mass (kg)'] <= high)
    ]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload Mass vs. Launch Outcome',
        labels={
            'class': 'Launch Outcome (0 = Failure, 1 = Success)',
            'Payload Mass (kg)': 'Payload Mass (kg)'
        }
    )

    return fig

# Run the app
if __name__ == '__main__':
      app.run(debug=True, port=8051)

