import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pricing_engine.black import BlackScholes
from datetime import datetime
import plotly.graph_objects as go

# this module holds functions for creating visuals in app.py

def plot_heatmap(spot, K, r, T, vol, call_axis, put_axis) -> list:
    # 10 x 10 
    difference = spot / 5
    max = spot + difference
    min = spot - difference
    spots = np.linspace(min, max, 10)

    difference = vol / 5
    max = vol + difference
    min = vol - difference
   
    vols = np.linspace(.05, .6, 10)

    calls = np.ndarray((10, 10))
    puts = np.ndarray((10, 10))
   
    for i in range(10):
      for j in range(10):

        #calculate calls and puts for heatmap
        calls[i][j] = format(BlackScholes(spots[j], K, r, T, vols[i]).call(), '.2f')
        puts[i][j] = format(BlackScholes(spots[j], K, r, T, vols[i]).put(), '.2f')
    
    # x and y axis spots and volatility labels
    for i in range(len(vols)):
        vols[i] = format(vols[i], ".2f")
        spots[i] = format(spots[i], ".2f")
    

    call_map =sns.heatmap(calls,vmin=calls[0][0], 
                vmax=calls[9, 9], 
                annot=True, 
                cmap='RdYlGn',
                xticklabels=spots,
                yticklabels=vols,
                ax=call_axis
                )
   
    put_map = sns.heatmap(puts, vmin=puts.min(),
                vmax=puts.max(),
                annot=True,
                cmap='RdYlGn',
                xticklabels=spots,
                yticklabels=vols,
                ax=put_axis)

    return [call_map, put_map]



def plot_tree(stock_tree, value_tree, N) -> go.Figure:
    
    fig = go.Figure()

    # plot edges first, so nodes draw on top
    for i in range(N):
        for j in range(i + 1):
            x0, y0 = i, j - i / 2  # spread nodes vertically, centered
            # up-child
            x1, y1 = i + 1, (j + 1) - (i + 1) / 2
            fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines',
                                      line=dict(color='lightgray'), showlegend=False))
            # down-child
            x2, y2 = i + 1, j - (i + 1) / 2
            fig.add_trace(go.Scatter(x=[x0, x2], y=[y0, y2], mode='lines',
                                      line=dict(color='lightgray'), showlegend=False))

    # plot nodes
    for i in range(N + 1):
        for j in range(i + 1):
            x, y = i, j - i / 2
            fig.add_trace(go.Scatter(
                x=[x], y=[y], mode='markers+text',
                marker=dict(size=20, color='steelblue'),
                text=[f"${value_tree[i,j]:.2f}"],
                textposition='top center',
                hovertext=f"Stock: ${stock_tree[i,j]:.2f}<br>Option: ${value_tree[i,j]:.2f}",
                hoverinfo='text',
                showlegend=False
            ))

    fig.update_layout(
        xaxis_title="Time Step",
        yaxis=dict(showticklabels=False),
        showlegend=False,
        height=500
    )
    return fig

if __name__ == "__main__":
    plot_heatmap(400, 370, .1, datetime(2026, 9, 27), .15)

