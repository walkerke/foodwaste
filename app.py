from dash import dcc, html, Input, Output, ctx  
import dash  
import plotly.graph_objects as go  
  
# Initialize app  
app = dash.Dash(__name__)  
app.title = "Food Waste Impact Dashboard"  
  
# Waste mana Weight  
base_flows = {  
   'retail_to_landfill': 2712077,  
   'retail_to_combustion': 881432,  
   'retail_to_compost': 1900141,  
   'service_to_landfill': 14008021,  
   'service_to_combustion': 3416734,  
   'service_to_compost': 252512,  
   'residential_to_landfill': 17532332,  
   'residential_to_combustion': 4010257,  
   'residential_to_compost': 977975  
}  
  
# GHG and cost factors  
ghg_factors = {'landfill': 0.50146, 'combustion': -0.13426, 'compost': -0.15213}  
cost_factors = {'landfill': 69.7, 'combustion': 69.7, 'compost': 9.7}  
  
# Color palette  
colors = {  
   'landfill': "rgba(165, 64, 45, 0.8)",  
   'combustion': "rgba(213,98,33, 0.8)",  
   'compost': "rgba(255, 207, 153, 0.8)",  
   'node': "#721121",  
   'background': "#FFCF99",  
   'text': "#721121",  
   'slider': "#A5402D",  
   'bar': "#d56221"  
}  
  
# Function to calculate GHG and cost impacts  
def calculate_impacts(values):  
   ghg_impact = {src: sum(values[f'{src}_to_{dest}'] * ghg_factors[dest.split('_')[-1]]  
                  for dest in ['landfill', 'combustion', 'compost'])  
            for src in ['retail', 'service', 'residential']}  
   cost_impact = {src: sum(values[f'{src}_to_{dest}'] * cost_factors[dest.split('_')[-1]]  
                   for dest in ['landfill', 'combustion', 'compost'])  
             for src in ['retail', 'service', 'residential']}  
   return ghg_impact, cost_impact  
  
# Function to filter flows by category  
def filter_flows(category, flows):  
   if category == "2019":  
      return flows  # Return all flows combined  
   return {key: value for key, value in flows.items() if key.startswith(category)}  
  
# Create the Sankey diagram  
def create_sankey(flows, subset):  
   if subset == "2019":  
      labels = ["Retail", "Service", "Residential", "Landfill", "Combustion", "Compost"]  
      sources = [0, 1, 2, 0, 1, 2, 0, 1, 2]  
      targets = [3, 3, 3, 4, 4, 4, 5, 5, 5]  
      values = [  
        flows['retail_to_landfill'], flows['service_to_landfill'], flows['residential_to_landfill'],  
        flows['retail_to_combustion'], flows['service_to_combustion'], flows['residential_to_combustion'],  
        flows['retail_to_compost'], flows['service_to_compost'], flows['residential_to_compost']  
      ]  
   else:  
      labels = [subset.capitalize(), "Landfill", "Combustion", "Compost"]  
      sources = [0, 0, 0]  
      targets = [1, 2, 3]  
      values = [  
        flows[f'{subset}_to_landfill'],  
        flows[f'{subset}_to_combustion'],  
        flows[f'{subset}_to_compost']  
      ]  
  
   flow_colors = [colors['landfill'], colors['combustion'], colors['compost']]  
  
   fig = go.Figure(go.Sankey(  
      node=dict(  
        pad=15,  
        thickness=20,  
        line=dict(color="black", width=0.5),  
        label=labels,  
        color=[colors['node']] + [colors['landfill'], colors['combustion'], colors['compost']]  
      ),  
      link=dict(  
        source=sources,  
        target=targets,  
        value=values,  
        color=flow_colors * (len(values) // 3)  
      )  
   ))  
   fig.update_layout(  
      title_text=f"{subset.capitalize()} Waste Flow Diagram" if subset != "2019" else "2019 Combined Waste Flow Diagram",  
      font_size=12,  
      height=600,  
      plot_bgcolor=colors['background']  
   )  
   return fig  
  
# Create the impact metrics graph   
from plotly.subplots import make_subplots   
def create_impact_graph(ghg, cost, subset):  
   if subset == "2019":  
      categories = ["Retail", "Service", "Residential", "2019 (Baseline)"]  
      ghg_values = [ghg[cat] for cat in ['retail', 'service', 'residential']] + [sum(ghg.values())]  
      cost_values = [cost[cat] for cat in ['retail', 'service', 'residential']] + [sum(cost.values())]  
   else:  
      categories = [f"{subset.capitalize()} (per ton - Adjusted)", f"{subset.capitalize()} (per ton - 2019)"]  
      ghg_values = [ghg[subset], sum(base_flows[f"{subset}_to_{dest}"] * ghg_factors[dest.split('_')[-1]] for dest in ['landfill', 'combustion', 'compost'])]  
      cost_values = [cost[subset], sum(base_flows[f"{subset}_to_{dest}"] * cost_factors[dest.split('_')[-1]] for dest in ['landfill', 'combustion', 'compost'])]  
  
   fig = make_subplots(specs=[[{"secondary_y": True}]])  
   fig.add_trace(go.Bar(  
      x=categories,  
      y=ghg_values,  
      name='GHG emmission (kg CO₂e)',  
      marker_color=colors['landfill'],  
      offsetgroup=0  
   ), secondary_y=False)  
   fig.add_trace(go.Bar(  
      x=categories,  
      y=cost_values,  
      name='Cost ($)',  
      marker_color=colors['combustion'],  
      offsetgroup=1  
   ), secondary_y=True)  
  
   fig.update_layout(  
      title_text=f"Impact Metrics: {subset.capitalize()}" if subset != "2019" else "Impact Metrics: 2019 Combined",  
      xaxis_title="Category",  
      yaxis_title="GHG Emission (kg CO₂e)",  
      yaxis2_title="Cost ($)",  
      legend=dict(x=0.1, y=1.1),  
      plot_bgcolor=colors['background'],  
      bargroupgap=0.15  
   )  
   fig.update_yaxes(title_text="GHG Emission (kg CO₂e)", secondary_y=False)  
   fig.update_yaxes(title_text="Cost ($)", secondary_y=True)  
   return fig

  
# app layout  
app.layout = html.Div([  
   html.H1("Food Waste Impact Dashboard", style={"textAlign": "center", "color": colors['text']}),  
  
   html.Div([  
      html.Label("Select Data Subset", style={"fontWeight": "bold", "color": colors['text']}),  
      dcc.Dropdown(  
        id="subset-dropdown",  
        options=[  
           {"label": "2019", "value": "2019"},  
           {"label": "Retail", "value": "retail"},  
           {"label": "Service", "value": "service"},  
           {"label": "Residential", "value": "residential"}  
        ],  
        value="2019",  
        clearable=False,  
        style={"marginBottom": "20px"}  
      )  
   ]),  
  
   dcc.Graph(id="sankey-diagram"),  
  
   html.Div([  
      html.Label("Adjust Waste Distribution (%)", style={"fontWeight": "bold", "color": colors['text']}),  
  
      html.Div([  
        html.Label("Landfill", style={"color": colors['text']}),  
        dcc.Slider(  
           id="landfill-slider", min=0, max=100, step=1, value=75,  
           marks={i: str(i) for i in range(0, 101, 10)},  
           tooltip={"always_visible": True}, updatemode="drag",  
           disabled=True  
        ),  
  
        html.Label("Combustion", style={"color": colors['text'], "marginTop": "15px"}),  
        dcc.Slider(  
           id="combustion-slider", min=0, max=100, step=1, value=18,  
           marks={i: str(i) for i in range(0, 101, 10)},  
           tooltip={"always_visible": True}, updatemode="drag",  
           disabled=True  
        ),  
  
        html.Label("Compost", style={"color": colors['text'], "marginTop": "15px"}),  
        dcc.Slider(  
           id="compost-slider", min=0, max=100, step=1, value=7,  
           marks={i: str(i) for i in range(0, 101, 10)},  
           tooltip={"always_visible": True}, updatemode="drag",  
           disabled=True  
        ),  
      ], style={"padding": "20px", "backgroundColor": colors['background'], "borderRadius": "8px"})  
   ], style={"marginTop": "20px", "padding": "10px"}),  
  
   dcc.Graph(id="impact-metrics")  
])  
  
@app.callback(  
   [Output("landfill-slider", "disabled"),  
    Output("combustion-slider", "disabled"),  
    Output("compost-slider", "disabled")],  
   [Input("subset-dropdown", "value")],  
   prevent_initial_call=False  
)  
def adjust_slider(subset):  
   if subset == "2019":  
      return True, True, True  
   return False, False, False  
  
@app.callback(  
   [Output("landfill-slider", "value"),  
    Output("combustion-slider", "value"),  
    Output("compost-slider", "value")],  
   [Input("landfill-slider", "value"),  
    Input("combustion-slider", "value"),  
    Input("compost-slider", "value")],  
   prevent_initial_call=True  
)  
def adjust_sliders(landfill, combustion, compost):  
   total = 100  
   trigger_id = ctx.triggered_id  
   if trigger_id == "landfill-slider":  
      combustion = (total - landfill) / 2  
      compost = total - landfill - combustion  
   elif trigger_id == "combustion-slider":  
      compost = total - landfill - combustion  
   elif trigger_id == "compost-slider":  
      combustion = total - landfill - compost  
  
   return landfill, combustion, compost  
  
@app.callback(  
   [Output("sankey-diagram", "figure"),  
    Output("impact-metrics", "figure")],  
   [Input("landfill-slider", "value"),  
    Input("combustion-slider", "value"),  
    Input("compost-slider", "value"),  
    Input("subset-dropdown", "value")]  
)  
def update_dashboard(landfill_pct, combustion_pct, compost_pct, subset):  
   if subset == "2019":  
      sankey_fig = create_sankey(base_flows, subset)  
      ghg_impact, cost_impact = calculate_impacts(base_flows)  
      impact_fig = create_impact_graph(ghg_impact, cost_impact, subset)  
   else:  
      # Adjust the flow values based on slider inputs  
      adjusted_flows = {  
        f"{subset}_to_{dest}": (  
           sum(base_flows[f"{subset}_to_{d}"] for d in ['landfill', 'combustion', 'compost']) *  
           (landfill_pct if dest == 'landfill' else combustion_pct if dest == 'combustion' else compost_pct) / 100  
        ) for dest in ['landfill', 'combustion', 'compost']  
      }  
  
      # Calculate the GHG and cost impacts based on the filtered flows  
      ghg_impact = {subset: sum(adjusted_flows[f'{subset}_to_{dest}'] * ghg_factors[dest] for dest in ['landfill', 'combustion', 'compost'])}  
      cost_impact = {subset: sum(adjusted_flows[f'{subset}_to_{dest}'] * cost_factors[dest] for dest in ['landfill', 'combustion', 'compost'])}  
  
      # Create the Sankey diagram and impact metrics graph  
      sankey_fig = create_sankey(adjusted_flows, subset)  
      impact_fig = create_impact_graph(ghg_impact, cost_impact, subset)  
  
   return sankey_fig, impact_fig  
  
if __name__ == "__main__":  
   app.run_server()