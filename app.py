import pandas as pd
import plotly.express as px
import seaborn
from shiny.express import input, ui, render
from shinywidgets import render_plotly, render_altair
import altair as alt
from palmerpenguins import load_penguins
from vega_datasets import data

penguins_df = pd.DataFrame(load_penguins())

with ui.sidebar(open="open"):
    ui.h2("Sidebar")
    ui.input_selectize("selected_attribute", "Attribute", ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"])
    ui.input_numeric("plotly_bin_count", "Plotly Bins", 20)
    ui.input_slider("seaborn_bin_count", "Seaborn Bins", 1, 100, 20)
    ui.input_checkbox_group("selected_species_list", "Species", ["Adelie", "Gentoo", "Chinstrap"], selected=["Adelie"], inline=True)
    ui.hr()
    ui.a("GitHub", href="https://github.com/brianpereboom/cintel-02-data", target="_blank")

with ui.layout_columns():
    @render.data_frame
    def table():
        return render.DataTable(penguins_df)
        
    @render.data_frame
    def grid():
        return render.DataGrid(penguins_df)
        
with ui.layout_columns():
    
    @render_plotly
    def plotly_hist():
        return px.histogram(penguins_df, x=input.selected_attribute.get(),\
            nbins=input.plotly_bin_count.get())

    @render.plot()
    def seaborn_hist():
        return seaborn.histplot(penguins_df, x=input.selected_attribute.get(),\
            bins=input.seaborn_bin_count.get())

with ui.card(full_screen=True):

    ui.card_header("Plotly Scatterplot: Species")
    
    @render_plotly
    def plotly_scatterplot():
        return px.scatter(penguins_df, x="bill_length_mm", y="bill_depth_mm", color="species")

with ui.card(full_screen=True):

    ui.card_header("Altair Ridgeline Plot")
    
    @render_altair
    def altair_ridgeline():

        attribute = input.selected_attribute.get().split('_')
        for w, word in enumerate(attribute[:-1]):
            attribute[w] = word.capitalize()
        attribute[-1] = '(' + attribute[-1] + ')'
        attribute = ' '.join(attribute)

        penguins_data = {}
        for island in penguins_df['island'].unique():
            penguins_data[island] = penguins_df[penguins_df['island'] == island][input.selected_attribute.get()]
        penguins_data = pd.DataFrame(penguins_data)

        height = 25
        step = 1000
        
        return (
            alt.Chart(penguins_data).transform_fold( 
                list(penguins_data.keys()), 
                as_=['Columns', 'Values'] 
            ).mark_area(
                interpolate='monotone',
                fillOpacity=0.25,
                stroke='lightgray',
                strokeWidth=0.1
            ).encode( 
                alt.X(
                    'Values:Q',
                    bin=True,
                    title = attribute,
                    scale=alt.Scale(clamp=True)
                ),
                alt.Y(
                    'count()',
                    stack=None,
                    scale=alt.Scale(range=[height, -step]),
                    axis=None
                ),
                alt.Color('Columns:N'),
                alt.Row(
                    "Columns:N",
                    title=None,
                    header=alt.Header(labelAngle=0, labelAlign="left")
                )
            ).properties(
                bounds="flush",
                height=height,
                width=600
            ).configure_facet(
                spacing=0
            ).configure_view(
                stroke=None
            )
        )
