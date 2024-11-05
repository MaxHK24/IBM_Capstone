# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load the dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Instantiate the Dash app
app = dash.Dash(__name__)

# Build the list of dropdown options
launch_sites = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
]

# Define the layout of the app
app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'font-size': 36, 'color': '#4A5A6A'}),
    
    # Dropdown menu for selecting launch sites
    dcc.Dropdown(
        id='launch-site-dropdown',
        options=launch_sites,
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),
    
    # Pie chart for launch success
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    # Payload slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={i: f'{i}' for i in range(0, 11000, 2000)},
        value=[min_payload, max_payload]
    ),
    
    # Scatter plot for payload success correlation
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for updating the pie chart based on selected launch site
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('launch-site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    # Filter data based on site selection
    if selected_site == 'ALL':
        df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            df,
            names='Launch Site',
            title="Total Success Launches by Site"
        )
    else:
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            site_data,
            names='class',
            title=f"Success vs Failure for {selected_site}",
            hole=0.4
        )
    return fig

# Callback for updating the scatter plot based on selected site and payload range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('launch-site-dropdown', 'value'), Input('payload-slider', 'value')]
)
def update_scatter_plot(selected_site, payload_range):
    # Filter data by payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    # Further filter data based on selected site
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        size='Payload Mass (kg)',
        title="Payload and Success Correlation by Booster Version"
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)