from flask import Flask
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # 1. Correct Path for Vercel Environment
        # This ensures it finds the CSV inside the 'api' folder during deployment
        base_path = os.path.dirname(__file__)
        csv_path = os.path.join(base_path, 'satellite_orbit_track.csv')
        
        df = pd.read_csv(csv_path)
        
        # Clean data - ensure column names match your CSV exactly (Case Sensitive)
        # Using .columns to be safe against small typos
        df.columns = df.columns.str.strip() 
        df = df.dropna(subset=['Latitude', 'Longitude'])

        # 2. Vector Math: Spherical to Cartesian
        R_earth = 6371
        R_orbit = R_earth + 400 
        lat_rad = np.radians(df['Latitude'])
        lon_rad = np.radians(df['Longitude'])
        
        x = R_orbit * np.cos(lat_rad) * np.cos(lon_rad)
        y = R_orbit * np.cos(lat_rad) * np.sin(lon_rad)
        z = R_orbit * np.sin(lat_rad)

        # 3. Create 3D Interactive Plot
        fig = go.Figure()

        # Add Earth (Blue Sphere)
        phi = np.linspace(0, 2*np.pi, 100)
        theta = np.linspace(0, np.pi, 100)
        phi, theta = np.meshgrid(phi, theta)
        
        x_earth = R_earth * np.sin(theta) * np.cos(phi)
        y_earth = R_earth * np.sin(theta) * np.sin(phi)
        z_earth = R_earth * np.cos(theta)
        
        fig.add_trace(go.Surface(
            x=x_earth, y=y_earth, z=z_earth,
            colorscale=[[0, 'rgb(10,10,50)'], [1, 'rgb(20,70,200)']],
            opacity=0.7,
            showscale=False,
            name='Earth'
        ))

        # Add Satellite Path (Neon Red/Cyan Line)
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(color='cyan', width=5),
            name='Orbit Path'
        ))

        fig.update_layout(
            title='Satellite Orbit Visualization (Real-Time Render)',
            template='plotly_dark',
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=1)
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )

        # 4. Return HTML with Plotly JS included
        return fig.to_html(include_plotlyjs='cdn')

    except Exception as e:
        return f"<h1>Deployment Error: {str(e)}</h1><p>Check if satellite_orbit_track.csv is in the api/ folder.</p>"

# This line is crucial for Vercel to recognize the app
app.debug = True
