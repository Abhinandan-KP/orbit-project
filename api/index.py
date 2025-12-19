from flask import Flask
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # 1. Load Data
        csv_path = os.path.join(os.path.dirname(__file__), 'satellite_orbit_track.csv')
        df = pd.read_csv(csv_path)
        # Clean data
        df = df.dropna(subset=['Latitude', 'Longitude'])

        # 2. Convert Lat/Lon to 3D Coordinates for plotting
        # Earth Radius approx 6371 km. We add a small buffer so the line sits above the surface.
        R = 6371 + 400 
        lat_rad = np.radians(df['Latitude'])
        lon_rad = np.radians(df['Longitude'])
        
        # Spherical to Cartesian conversion
        x = R * np.cos(lat_rad) * np.cos(lon_rad)
        y = R * np.cos(lat_rad) * np.sin(lon_rad)
        z = R * np.sin(lat_rad)

        # 3. Create 3D Interactive Plot
        fig = go.Figure()

        # Add Earth (Blue Sphere)
        # Create a sphere mesh
        phi = np.linspace(0, 2*np.pi, 100)
        theta = np.linspace(0, np.pi, 100)
        phi, theta = np.meshgrid(phi, theta)
        
        r_earth = 6371
        x_earth = r_earth * np.sin(theta) * np.cos(phi)
        y_earth = r_earth * np.sin(theta) * np.sin(phi)
        z_earth = r_earth * np.cos(theta)
        
        fig.add_trace(go.Surface(
            x=x_earth, y=y_earth, z=z_earth,
            colorscale=[[0, 'rgb(0,0,50)'], [1, 'rgb(0,50,150)']], # Dark blue ocean color
            opacity=0.8,
            showscale=False,
            name='Earth'
        ))

        # Add Satellite Path (Red Line)
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(color='red', width=5),
            name='Orbit Path'
        ))

        # Make it look nice
        fig.update_layout(
            title='3D Satellite Orbit Visualization',
            template='plotly_dark',
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )

        # 4. Return the Interactive HTML directly
        return fig.to_html()

    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

if __name__ == '__main__':
    app.run()
