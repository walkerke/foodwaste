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
   'restaurants+hotels_to_landfill': 14008021,  
   'restaurants+hotels_to_combustion': 3416734,  
   'restaurants+hotels_to_compost': 252512,  
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
   'compost': "rgba(176,211,49, 0.8)",  
   'node': "#730d05",  
   'background': "#FFFFFF",  
   'text': "#730d05",  
   'slider': "#ececa3",  
   'bar': "#ececa3"
}  
  
# Function to calculate GHG and cost impacts  
def calculate_impacts(values):  
   ghg_impact = {src: sum(values[f'{src}_to_{dest}'] * ghg_factors[dest.split('_')[-1]]  
                  for dest in ['landfill', 'combustion', 'compost'])  
            for src in ['retail', 'restaurants+hotels', 'residential']}  
   cost_impact = {src: sum(values[f'{src}_to_{dest}'] * cost_factors[dest.split('_')[-1]]  
                   for dest in ['landfill', 'combustion', 'compost'])  
             for src in ['retail', 'restaurants+hotels', 'residential']}  
   return ghg_impact, cost_impact  
  
# Function to filter flows by category  
def filter_flows(category, flows):  
   if category == "Most Recent Data":  
      return flows  # Return all flows combined  
   return {key: value for key, value in flows.items() if key.startswith(category)}  
  
# Create the Sankey diagram  
def create_sankey(flows, subset):  
   if subset == "Most Recent Data":  
      labels = ["Retail", "restaurants+hotels", "Residential", "Landfill", "Combustion", "Compost"]  
      sources = [0, 1, 2, 0, 1, 2, 0, 1, 2]  
      targets = [3, 3, 3, 4, 4, 4, 5, 5, 5]  
      values = [  
        flows['retail_to_landfill'], flows['restaurants+hotels_to_landfill'], flows['residential_to_landfill'],  
        flows['retail_to_combustion'], flows['restaurants+hotels_to_combustion'], flows['residential_to_combustion'],  
        flows['retail_to_compost'], flows['restaurants+hotels_to_compost'], flows['residential_to_compost']  
      ]  
      node_colors = [colors['node']] * 6  
   else:  
      labels = [subset.capitalize(), "Landfill", "Combustion", "Compost"]  
      sources = [0, 0, 0]  
      targets = [1, 2, 3]  
      values = [  
        flows[f'{subset}_to_landfill'],  
        flows[f'{subset}_to_combustion'],  
        flows[f'{subset}_to_compost']  
      ]  
      node_colors = [colors['node']] * 4  
  
   flow_colors = [colors['landfill'], colors['combustion'], colors['compost']]  
  
   fig = go.Figure(go.Sankey(  
      node=dict(  
        pad=15,  
        thickness=20,  
        line=dict(color="white", width=0.5),  
        label=labels,  
        color=node_colors  
      ),  
      link=dict(  
        source=sources,  
        target=targets,  
        value=values,  
        color=flow_colors * (len(values) // 3)  
      )  
   ))  
   fig.update_layout(  
      title_text=f"{subset.capitalize()} Waste Flow Diagram" if subset != "Most Recent Data" else "Most Recent Data Combined Waste Flow Diagram",  
      font_size=12,  
      height=600,  
      plot_bgcolor=colors['background']  
   )  
   fig.update_layout(hovermode='x unified')  
   return fig  
 # Create the impact metrics graph   
from plotly.subplots import make_subplots   
def create_impact_graph(ghg, cost, subset, adjusted_ghg, adjusted_cost):  
   if subset == "Most Recent Data":  
      categories = ["Retail", "restaurants+hotels", "Residential", "Most Recent Data (Baseline)"]  
      ghg_values = [ghg[cat] / 1e6 for cat in ['retail', 'restaurants+hotels', 'residential']] + [sum(ghg.values()) / 1e6]  
      cost_values = [cost[cat] / 1e6 for cat in ['retail', 'restaurants+hotels', 'residential']] + [sum(cost.values()) / 1e6]  
   else:  
      categories = [f"{subset.capitalize()} (per ton - Adjusted)", f"{subset.capitalize()} (per ton - Most Recent Data)"]  
      ghg_values = [adjusted_ghg[subset] / 1e6, sum(base_flows[f"{subset}_to_{dest}"] * ghg_factors[dest.split('_')[-1]] for dest in ['landfill', 'combustion', 'compost']) / 1e6]  
      cost_values = [adjusted_cost[subset] / 1e6, sum(base_flows[f"{subset}_to_{dest}"] * cost_factors[dest.split('_')[-1]] for dest in ['landfill', 'combustion', 'compost']) / 1e6]  
  
   fig = make_subplots(specs=[[{"secondary_y": True}]])  
   fig.add_trace(go.Bar(  
      x=categories,  
      y=ghg_values,  
      name='GHG emmission (M kg CO₂e)',  
      marker_color=colors['landfill'],  
      offsetgroup=0  
   ), secondary_y=False)  
   fig.add_trace(go.Bar(  
      x=categories,  
      y=cost_values,  
      name='Cost (M $)',  
      marker_color=colors['combustion'],  
      offsetgroup=1  
   ), secondary_y=True)  
  
   fig.update_layout(  
      title_text=f"Impact Metrics: {subset.capitalize()}" if subset != "Most Recent Data" else "Impact Metrics: Most Recent Data Combined",  
      xaxis_title="Category",  
      yaxis_title="GHG Emission (M kg CO₂e)",  
      yaxis2_title="Cost (M $)",  
      legend=dict(x=0.5, y=0.95, orientation='h'),  
      plot_bgcolor=colors['background'],  
      bargroupgap=0.15,  
      margin=dict(l=50, r=50, t=100, b=50)  
   )  
   fig.update_yaxes(title_text="GHG Emission (M kg CO₂e)", secondary_y=False)  
   fig.update_yaxes(title_text="Cost (M $)", secondary_y=True)  
   return fig

app.layout = html.Div([
    dcc.Graph(id="sankey-diagram", style={'height': '600px'}),
    
    html.Div([
        html.Label("Select Data Subset", style={"fontWeight": "bold", "color": colors['text']}),
        dcc.Dropdown(
            id="subset-dropdown",
            options=[
                {"label": "Most Recent Data", "value": "Most Recent Data"},
                {"label": "Retail", "value": "retail"},
                {"label": "restaurants+hotels", "value": "restaurants+hotels"},
                {"label": "Residential", "value": "residential"}
            ],
            value="Most Recent Data",
            clearable=False,
            style={"marginBottom": "20px"}
        )
    ]),
    
    html.Div([
        html.Label("Adjust Waste Distribution (%)", style={"fontWeight": "bold", "color": colors['text']}),
        
        html.Div([
            html.Label("Compost", style={"color": colors['text'], "marginTop": "15px"}),
            dcc.Slider(
                id="compost-slider", min=0, max=100, step=1, value=7,
                marks={i: str(i) for i in range(0, 101, 10)},
                tooltip={"always_visible": True}, updatemode="drag",
                disabled=True
            ),
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
        ], style={"padding": "20px", "backgroundColor": colors['background'], "borderRadius": "8px"})
    ], style={"marginTop": "20px", "padding": "10px"}),
    
    dcc.Graph(id="impact-metrics", style={'height': '600px'})
])

@app.callback(
    [Output("landfill-slider", "disabled"),
     Output("combustion-slider", "disabled"),
     Output("compost-slider", "disabled")],
    [Input("subset-dropdown", "value")],
    prevent_initial_call=False
)
def adjust_slider(subset):
    if subset == "Most Recent Data":
        return True, True, True
    return False, False, False



@app.callback(
     [Output("landfill-slider", "value"),
     Output("combustion-slider", "value"),
     Output("compost-slider", "value")],
    [Input("landfill-slider", "value"),
     Input("combustion-slider", "value"),
     Input("compost-slider", "value"),
     Input("subset-dropdown", "value")],
    prevent_initial_call=True
)
def adjust_sliders(landfill, combustion, compost, subset):
    default_values = {
        "retail": {"landfill": 49, "combustion": 16, "compost": 35},
        "restaurants+hotels": {"landfill": 79, "combustion": 19, "compost": 2},
        "residential": {"landfill": 78, "combustion": 18, "compost": 4}
    }
    
    if subset in default_values:
        if ctx.triggered_id == "subset-dropdown":
            return default_values[subset]["landfill"], default_values[subset]["combustion"], default_values[subset]["compost"]
    
    total = 100
    trigger_id = ctx.triggered_id
    
    if trigger_id == "compost-slider":
        if compost + combustion > total:
            combustion = total - compost
        landfill = total - compost - combustion
        return landfill, combustion, compost
    elif trigger_id == "combustion-slider":
        if combustion + compost > total:
            compost = total - combustion
        landfill = total - compost - combustion
        return landfill, combustion, compost
    elif trigger_id == "landfill-slider":
        if landfill + compost > total:
            compost = total - landfill
        combustion = total - landfill - compost
        return landfill, combustion, compost
    
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
    if subset == "Most Recent Data":
        sankey_fig = create_sankey(base_flows, subset)
        ghg_impact, cost_impact = calculate_impacts(base_flows)
        impact_fig = create_impact_graph(ghg_impact, cost_impact, subset, ghg_impact, cost_impact)
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
        impact_fig = create_impact_graph({subset: sum(base_flows[f"{subset}_to_{dest}"] * ghg_factors[dest.split('_')[-1]] for dest in ['landfill', 'combustion', 'compost'])},
                                         {subset: sum(base_flows[f"{subset}_to_{dest}"] * cost_factors[dest.split('_')[-1]] for dest in ['landfill', 'combustion', 'compost'])},
                                         subset, ghg_impact, cost_impact)
    
    return sankey_fig, impact_fig

if __name__ == "__main__":
    app.run_server()
