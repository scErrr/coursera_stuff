# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px


# Functions
def find_unique_value(df, column_name="Launch Site"):
    uniques = list(df[column_name].unique())
    return uniques

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = find_unique_value(spacex_df, "Launch Site")
options = [{'label': 'All Sites', 'value': 'ALL'}]
# filter the data once, to reduce redundance
filtered_df = spacex_df.groupby(["Launch Site", "class"]).agg(class_count=('class', 'count')).reset_index()

for site in launch_sites:
    temp = {"label":site, "value":site}
    options.append(temp)

# Create a dash application
app = dash.Dash(__name__)


# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=options,
                                             value="ALL",
                                             placeholder="All Sites",
                                             searchable=True
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', 
                                                min=0, 
                                                max=10000, 
                                                step=1000, 
                                                marks={0: '0',2500: '2500', 5000: '5000', 7500: '7500'},
                                                value=[min_payload, max_payload]
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        plot_data = filtered_df[filtered_df["class"]==1]
        fig = px.pie(plot_data, values='class_count', names=plot_data["Launch Site"], title='Total Success Launch by Site')
        return fig
    else:
        plot_data = filtered_df[filtered_df["Launch Site"]==entered_site]
        # print(f"SITE: {entered_site}")
        # print(plot_data)
        # plot_data = plot_data[["class", "class_count"]]
        # print(plot_data)
        fig = px.pie(plot_data, values='class_count', names=plot_data["class"], title=f'Total Success Launch for site {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
[Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_slider_chart(entered_site, slider_value):
    min = slider_value[0]
    max = slider_value[1]
    ranged_plot_data = spacex_df[(spacex_df["Payload Mass (kg)"] >= min) & (spacex_df["Payload Mass (kg)"]<=max)]
    if entered_site == 'ALL':
        fig = px.scatter(ranged_plot_data, x="Payload Mass (kg)", y="class", color="Launch Site")
    else:
        plot_data = ranged_plot_data[ranged_plot_data["Launch Site"] == entered_site]
        fig = px.scatter(plot_data, x="Payload Mass (kg)", y="class", color="class")

    return fig

# # Run the app
if __name__ == '__main__':
    app.run()
