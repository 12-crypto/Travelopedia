"""
Enhanced Charts Component for Travelopedia
Provides reusable chart components with premium styling
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_timeline_chart(daily_schedule):
    """Create an interactive timeline for daily activities."""
    
    if not daily_schedule:
        return None
    
    # Prepare data
    tasks = []
    for day_idx, day in enumerate(daily_schedule):
        day_name = day.get('date', f'Day {day_idx + 1}')
        activities = day.get('activities', [])
        
        for activity in activities:
            tasks.append({
                'Task': activity.get('name', 'Activity'),
                'Start': f"{day_name} {activity.get('start_time', '09:00')}",
                'Finish': f"{day_name} {activity.get('end_time', '10:00')}",
                'Resource': activity.get('category', 'General')
            })
    
    if not tasks:
        return None
    
    df = pd.DataFrame(tasks)
    
    # Create Gantt-style timeline
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Resource",
        color_discrete_sequence=['#4fc3f7', '#7c4dff', '#ff6b9d', '#ffd700', '#4ade80']
    )
    
    fig.update_layout(
        title=dict(
            text='Daily Activity Timeline',
            font=dict(size=20, color='#e8eef5', family='Inter'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Time',
            titlefont=dict(color='#b0bac9'),
            tickfont=dict(color='#b0bac9'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title='Activities',
            titlefont=dict(color='#b0bac9'),
            tickfont=dict(color='#b0bac9')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        legend=dict(
            title='Category',
            font=dict(color='#e8eef5'),
            bgcolor='rgba(255,255,255,0.05)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1
        ),
        margin=dict(t=80, b=60, l=150, r=60)
    )
    
    return fig


def create_hotel_comparison_radar(hotels):
    """Create a radar chart comparing hotel features."""
    
    if not hotels or len(hotels) == 0:
        return None
    
    categories = ['Rating', 'Location', 'Amenities', 'Value', 'Cleanliness']
    
    fig = go.Figure()
    
    colors = ['#4fc3f7', '#7c4dff', '#ff6b9d', '#ffd700']
    
    for idx, hotel in enumerate(hotels[:4]):  # Limit to 4 hotels
        values = [
            hotel.get('rating', 0) * 2,  # Scale to 10
            hotel.get('location_score', 8),
            hotel.get('amenities_score', 7),
            hotel.get('value_score', 8),
            hotel.get('cleanliness_score', 9)
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=hotel.get('name', f'Hotel {idx + 1}'),
            line=dict(color=colors[idx % len(colors)], width=2),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickfont=dict(color='#b0bac9'),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(color='#e8eef5', size=12),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        title=dict(
            text='Hotel Comparison',
            font=dict(size=20, color='#e8eef5', family='Inter'),
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        legend=dict(
            font=dict(color='#e8eef5'),
            bgcolor='rgba(255,255,255,0.05)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(t=80, b=40, l=40, r=40)
    )
    
    return fig


def create_activity_distribution_chart(activities):
    """Create a sunburst chart showing activity distribution by category."""
    
    if not activities:
        return None
    
    # Prepare hierarchical data
    category_counts = {}
    for activity in activities:
        category = activity.get('category', 'Other')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    labels = ['Activities'] + list(category_counts.keys())
    parents = [''] + ['Activities'] * len(category_counts)
    values = [sum(category_counts.values())] + list(category_counts.values())
    
    colors = ['#0a0e14', '#4fc3f7', '#7c4dff', '#ff6b9d', '#ffd700', '#4ade80', '#f59e0b']
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(
            colors=colors[:len(labels)],
            line=dict(color='#0a0e14', width=2)
        ),
        textfont=dict(size=14, color='#e8eef5', family='Inter'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percentParent}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Activity Distribution',
            font=dict(size=20, color='#e8eef5', family='Inter'),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(t=80, b=40, l=40, r=40)
    )
    
    return fig


def create_savings_comparison_chart(original_budget, actual_cost, breakdown):
    """Create a waterfall chart showing budget vs actual spending."""
    
    categories = ['Budget'] + list(breakdown.keys()) + ['Total']
    values = [original_budget] + [-v for v in breakdown.values()] + [actual_cost - original_budget]
    
    # Determine colors
    colors = ['#4fc3f7'] + ['#ff6b9d' if v < 0 else '#4ade80' for v in values[1:-1]] + \
             ['#4ade80' if values[-1] < 0 else '#ff6b9d']
    
    fig = go.Figure(go.Waterfall(
        name="Budget",
        orientation="v",
        measure=["absolute"] + ["relative"] * (len(categories) - 2) + ["total"],
        x=categories,
        y=values,
        text=[f"${abs(v):,.0f}" for v in values],
        textposition="outside",
        connector={"line": {"color": "rgba(255,255,255,0.3)"}},
        marker={"color": colors, "line": {"color": "#0a0e14", "width": 2}},
        decreasing={"marker": {"color": "#ff6b9d"}},
        increasing={"marker": {"color": "#4ade80"}},
        totals={"marker": {"color": "#4fc3f7"}}
    ))
    
    fig.update_layout(
        title=dict(
            text='Budget Breakdown',
            font=dict(size=20, color='#e8eef5', family='Inter'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Category',
            titlefont=dict(color='#b0bac9'),
            tickfont=dict(color='#b0bac9')
        ),
        yaxis=dict(
            title='Amount (USD)',
            titlefont=dict(color='#b0bac9'),
            tickfont=dict(color='#b0bac9'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False,
        margin=dict(t=80, b=60, l=60, r=60)
    )
    
    return fig


def create_heatmap_destination_popularity(destinations_data):
    """Create a heatmap showing destination popularity by month."""
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Sample data (in real app, this would come from historical data)
    destinations = list(destinations_data.keys())[:5]  # Top 5 destinations
    
    # Generate sample popularity scores
    data = []
    for dest in destinations:
        data.append([np.random.randint(50, 100) for _ in range(12)])
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=months,
        y=destinations,
        colorscale=[
            [0, '#0a0e14'],
            [0.25, '#4fc3f7'],
            [0.5, '#7c4dff'],
            [0.75, '#ff6b9d'],
            [1, '#ffd700']
        ],
        text=data,
        texttemplate='%{text}',
        textfont={"size": 12, "color": "#e8eef5"},
        hovertemplate='<b>%{y}</b><br>%{x}: %{z}% popularity<extra></extra>',
        colorbar=dict(
            title="Popularity",
            titlefont=dict(color='#e8eef5'),
            tickfont=dict(color='#e8eef5'),
            bgcolor='rgba(255,255,255,0.05)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1
        )
    ))
    
    fig.update_layout(
        title=dict(
            text='Destination Popularity by Month',
            font=dict(size=20, color='#e8eef5', family='Inter'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Month',
            titlefont=dict(color='#b0bac9'),
            tickfont=dict(color='#b0bac9')
        ),
        yaxis=dict(
            title='Destination',
            titlefont=dict(color='#b0bac9'),
            tickfont=dict(color='#b0bac9')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(t=80, b=60, l=120, r=60)
    )
    
    return fig
