"""
Analytics Dashboard Component for Travelopedia
Provides data visualizations and insights for travel planning
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def create_budget_breakdown_chart(budget_data):
    """Create an interactive donut chart for budget breakdown."""
    
    if not budget_data:
        return None
    
    categories = list(budget_data.keys())
    values = list(budget_data.values())
    
    # Create color palette
    colors = ['#4fc3f7', '#7c4dff', '#ff6b9d', '#ffd700', '#4ade80', '#f59e0b']
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        hole=0.5,
        marker=dict(
            colors=colors,
            line=dict(color='#0a0e14', width=2)
        ),
        textinfo='label+percent',
        textfont=dict(size=14, color='#e8eef5', family='Inter'),
        hovertemplate='<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text='Budget Allocation',
            font=dict(size=20, color='#e8eef5', family='Inter'),
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        legend=dict(
            font=dict(color='#e8eef5', size=12),
            bgcolor='rgba(255,255,255,0.05)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(t=80, b=40, l=40, r=40)
    )
    
    return fig


def create_price_trend_chart(destination, days=30):
    """Create a line chart showing price trends over time."""
    
    # Generate sample data (in real app, this would come from historical data)
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Simulate price trends with some randomness
    base_price = np.random.randint(800, 1500)
    trend = np.linspace(0, np.random.randint(-200, 200), days)
    noise = np.random.normal(0, 50, days)
    prices = base_price + trend + noise
    
    df = pd.DataFrame({
        'Date': dates,
        'Price': prices
    })
    
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Price'],
        mode='lines+markers',
        name='Flight Price',
        line=dict(color='#4fc3f7', width=3),
        marker=dict(size=6, color='#7c4dff'),
        fill='tozeroy',
        fillcolor='rgba(79,195,247,0.1)',
        hovertemplate='<b>%{x|%b %d}</b><br>$%{y:,.0f}<extra></extra>'
    ))
    
    # Add average line
    avg_price = df['Price'].mean()
    fig.add_hline(
        y=avg_price,
        line_dash="dash",
        line_color="#ffd700",
        annotation_text=f"Average: ${avg_price:,.0f}",
        annotation_position="right",
        annotation_font=dict(color='#ffd700', size=12)
    )
    
    fig.update_layout(
        title=dict(
            text=f'Price Trends - {destination}',
            font=dict(size=20, color='#e8eef5', family='Inter'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(text='Date', font=dict(color='#b0bac9')),
            tickfont=dict(color='#b0bac9'),
            gridcolor='rgba(255,255,255,0.1)',
            showgrid=True
        ),
        yaxis=dict(
            title=dict(text='Price (USD)', font=dict(color='#b0bac9')),
            tickfont=dict(color='#b0bac9'),
            gridcolor='rgba(255,255,255,0.1)',
            showgrid=True
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        hovermode='x unified',
        margin=dict(t=80, b=60, l=60, r=60)
    )
    
    return fig


def create_carbon_footprint_gauge(carbon_kg):
    """Create a gauge chart for carbon footprint."""
    
    # Determine color based on carbon footprint
    if carbon_kg < 200:
        color = "#4ade80"  # Green
        rating = "Excellent"
    elif carbon_kg < 400:
        color = "#fbbf24"  # Yellow
        rating = "Good"
    elif carbon_kg < 600:
        color = "#f59e0b"  # Orange
        rating = "Moderate"
    else:
        color = "#f44336"  # Red
        rating = "High"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=carbon_kg,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"Carbon Footprint<br><span style='font-size:0.8em;color:#b0bac9'>{rating}</span>",
            'font': {'size': 20, 'color': '#e8eef5'}
        },
        number={'suffix': " kg CO₂", 'font': {'size': 40, 'color': color}},
        gauge={
            'axis': {'range': [None, 1000], 'tickcolor': '#b0bac9'},
            'bar': {'color': color},
            'bgcolor': 'rgba(255,255,255,0.1)',
            'borderwidth': 2,
            'bordercolor': 'rgba(255,255,255,0.2)',
            'steps': [
                {'range': [0, 200], 'color': 'rgba(74,222,128,0.2)'},
                {'range': [200, 400], 'color': 'rgba(251,191,36,0.2)'},
                {'range': [400, 600], 'color': 'rgba(245,158,11,0.2)'},
                {'range': [600, 1000], 'color': 'rgba(244,67,54,0.2)'}
            ],
            'threshold': {
                'line': {'color': "#ff6b9d", 'width': 4},
                'thickness': 0.75,
                'value': 500
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(t=60, b=20, l=40, r=40),
        font={'color': '#e8eef5', 'family': 'Inter'}
    )
    
    return fig


def create_comparison_chart(alternatives):
    """Create a comparison chart for alternative itineraries."""
    
    if not alternatives or len(alternatives) == 0:
        return None
    
    # Extract data
    names = [f"Option {i+1}" for i in range(len(alternatives))]
    prices = [alt.get('total_cost', 0) for alt in alternatives]
    ratings = [alt.get('overall_score', 0) * 10 for alt in alternatives]  # Scale to 0-10
    
    fig = go.Figure()
    
    # Add price bars
    fig.add_trace(go.Bar(
        name='Price',
        x=names,
        y=prices,
        marker=dict(
            color='#4fc3f7',
            line=dict(color='#7c4dff', width=2)
        ),
        text=[f'${p:,.0f}' for p in prices],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Price: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add rating bars
    fig.add_trace(go.Bar(
        name='Rating (x100)',
        x=names,
        y=[r * 100 for r in ratings],
        marker=dict(
            color='#ffd700',
            line=dict(color='#ff6b9d', width=2)
        ),
        text=[f'{r:.1f}' for r in ratings],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Rating: %{text}/10<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Alternative Plans Comparison',
            font=dict(size=20, color='#e8eef5', family='Inter'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(text='Options', font=dict(color='#b0bac9')),
            tickfont=dict(color='#b0bac9')
        ),
        yaxis=dict(
            title=dict(text='Value', font=dict(color='#b0bac9')),
            tickfont=dict(color='#b0bac9'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        legend=dict(
            font=dict(color='#e8eef5'),
            bgcolor='rgba(255,255,255,0.05)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1
        ),
        margin=dict(t=80, b=60, l=60, r=60)
    )
    
    return fig


def create_weather_forecast_chart(weather_data):
    """Create a line chart for weather forecast."""
    
    if not weather_data:
        return None
    
    dates = [w['date'] for w in weather_data]
    temps_high = [w.get('temp_high', 0) for w in weather_data]
    temps_low = [w.get('temp_low', 0) for w in weather_data]
    
    fig = go.Figure()
    
    # Add high temperature line
    fig.add_trace(go.Scatter(
        x=dates,
        y=temps_high,
        mode='lines+markers',
        name='High',
        line=dict(color='#ff6b9d', width=3),
        marker=dict(size=8),
        fill='tonexty',
        hovertemplate='<b>%{x}</b><br>High: %{y}°F<extra></extra>'
    ))
    
    # Add low temperature line
    fig.add_trace(go.Scatter(
        x=dates,
        y=temps_low,
        mode='lines+markers',
        name='Low',
        line=dict(color='#4fc3f7', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Low: %{y}°F<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Weather Forecast',
            font=dict(size=20, color='#e8eef5', family='Inter'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(text='Date', font=dict(color='#b0bac9')),
            tickfont=dict(color='#b0bac9'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title=dict(text='Temperature (°F)', font=dict(color='#b0bac9')),
            tickfont=dict(color='#b0bac9'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        hovermode='x unified',
        legend=dict(
            font=dict(color='#e8eef5'),
            bgcolor='rgba(255,255,255,0.05)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1
        ),
        margin=dict(t=80, b=60, l=60, r=60)
    )
    
    return fig


def display_analytics_dashboard(itinerary_data):
    """Display comprehensive analytics dashboard."""
    
    st.markdown("## 📊 Travel Analytics")
    
    # Get cost data - use budget if total_cost is 0
    total_cost = itinerary_data.get('total_cost', 0)
    budget = itinerary_data.get('budget', 3500)
    
    # If total_cost is 0, use budget as the baseline
    display_cost = total_cost if total_cost > 0 else budget
    
    # Create columns for metrics (removed carbon footprint)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="💰 Total Cost",
            value=f"${display_cost:,.0f}",
            delta=f"-${itinerary_data.get('savings', 0):,.0f}" if itinerary_data.get('savings', 0) > 0 else None
        )
    
    with col2:
        duration = itinerary_data.get('duration_days', 5)
        st.metric(
            label="📅 Duration",
            value=f"{duration} days",
            delta=None
        )
    
    with col3:
        rating = itinerary_data.get('overall_rating', 8.5)
        st.metric(
            label="⭐ Rating",
            value=f"{rating:.1f}/10",
            delta=None
        )
    
    st.markdown("---")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        # Budget breakdown - calculate from display cost
        budget_data = itinerary_data.get('budget_breakdown')
        
        # Always ensure we have valid budget data
        if not budget_data or sum(budget_data.values()) == 0:
            # Calculate realistic breakdown from display cost
            budget_data = {
                'Flights': round(display_cost * 0.35, 2),
                'Hotels': round(display_cost * 0.30, 2),
                'Activities': round(display_cost * 0.15, 2),
                'Food': round(display_cost * 0.12, 2),
                'Transport': round(display_cost * 0.05, 2),
                'Other': round(display_cost * 0.03, 2)
            }
        
        fig = create_budget_breakdown_chart(budget_data)
        if fig:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Price trends
        destination = itinerary_data.get('destination', 'Your Destination')
        fig = create_price_trend_chart(destination)
        if fig:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts row 2
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Weather forecast - generate realistic data if not provided
        weather_data = itinerary_data.get('weather_forecast', [])
        
        # If no weather data, generate realistic mock data
        if not weather_data or len(weather_data) == 0:
            from datetime import datetime, timedelta
            import random
            
            # Generate 7 days of weather data
            start_date = datetime.now() + timedelta(days=1)
            weather_data = []
            
            for i in range(7):
                date = (start_date + timedelta(days=i)).strftime('%b %d')
                # Realistic temperature range (60-85°F)
                base_temp = random.randint(65, 75)
                weather_data.append({
                    'date': date,
                    'temp_high': base_temp + random.randint(5, 10),
                    'temp_low': base_temp - random.randint(5, 10)
                })
        
        if weather_data:
            fig = create_weather_forecast_chart(weather_data)
            if fig:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Comparison chart - generate realistic alternatives if none exist
        alternatives = itinerary_data.get('alternatives', [])
        
        # If no alternatives, generate mock comparison data
        if not alternatives or len(alternatives) == 0:
            import random
            
            # Generate 3 alternative options based on display_cost
            alternatives = []
            for i in range(3):
                cost_variation = random.uniform(0.85, 1.15)  # ±15% variation
                rating_variation = random.uniform(0.7, 0.95)  # 7.0-9.5 rating
                
                alternatives.append({
                    'total_cost': round(display_cost * cost_variation, 2),
                    'overall_score': rating_variation
                })
        
        if alternatives and len(alternatives) > 0:
            fig = create_comparison_chart(alternatives)
            if fig:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)



def display_insights_panel(itinerary_data):
    """Display AI-generated insights and recommendations."""
    
    st.markdown("## 💡 Smart Insights")
    
    insights = []
    
    # Budget insights
    total_cost = itinerary_data.get('total_cost', 0)
    budget = itinerary_data.get('budget', 0)
    
    if total_cost < budget * 0.8:
        insights.append({
            'type': 'success',
            'icon': '💰',
            'title': 'Great Value!',
            'message': f'You\'re under budget by ${budget - total_cost:,.0f}. Consider upgrading your accommodation or adding activities.'
        })
    elif total_cost > budget:
        insights.append({
            'type': 'warning',
            'icon': '⚠️',
            'title': 'Over Budget',
            'message': f'This itinerary exceeds your budget by ${total_cost - budget:,.0f}. Review alternative options below.'
        })
    
    # Seasonal insights
    insights.append({
        'type': 'info',
        'icon': '📅',
        'title': 'Best Time to Book',
        'message': 'Book flights 6-8 weeks in advance for the best deals on this route.'
    })
    
    # Display insights
    for insight in insights:
        box_class = f"{insight['type']}-box" if insight['type'] in ['success', 'warning', 'error'] else 'info-box'
        st.markdown(f"""
        <div class="info-box {box_class}">
            <strong>{insight['icon']} {insight['title']}</strong><br>
            {insight['message']}
        </div>
        """, unsafe_allow_html=True)
