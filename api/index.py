from flask import Flask
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

app = Flask(__name__)

def generate_dashboard():
    # 1. Load Orbital Ephemeris Data
    base_path = os.path.dirname(__file__)
    csv_path = os.path.join(base_path, 'satellite_orbit_track.csv')
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Constants
    R_earth = 6371 # Mean Earth Radius (km)
    Alt_leo = 450  # Low Earth Orbit altitude buffer
    
    lat = df['Latitude']
    lon = df['Longitude']
    lat_rad, lon_rad = np.radians(lat), np.radians(lon)

    # Vector Transformation: Geocentric Cartesian Coordinates (ECEF approximation)
    r = R_earth + Alt_leo
    x = r * np.cos(lat_rad) * np.cos(lon_rad)
    y = r * np.cos(lat_rad) * np.sin(lon_rad)
    z = r * np.sin(lat_rad)

    # --- VIEW 1: GROUND TRACK (2D) ---
    fig_ground = go.Figure(go.Scattergeo(lat=lat, lon=lon, mode='lines', line=dict(width=2, color='#00f2ff')))
    fig_ground.update_layout(title="Sub-Satellite Ground Track", template="plotly_dark", margin=dict(l=0,r=0,b=0,t=40),
                            geo=dict(showland=True, landcolor="#111", showocean=True, oceancolor="#050505", 
                                    projection_type='natural earth', bgcolor='rgba(0,0,0,0)'))

    # --- VIEW 2: ORBITAL GEOMETRY (Static 3D) ---
    fig_geom = go.Figure()
    fig_geom.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='#ff0055', width=3), name='Orbital Path'))
    fig_geom.update_layout(title="Kinematic Orbital Envelope", template="plotly_dark", 
                          scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False))

    # --- VIEW 3: GEOCENTRIC VISUALIZATION (3D Graph) ---
    fig_graph = go.Figure()
    phi, theta = np.meshgrid(np.linspace(0, 2*np.pi, 60), np.linspace(0, np.pi, 60))
    xs, ys, zs = R_earth * np.sin(theta) * np.cos(phi), R_earth * np.sin(theta) * np.sin(phi), R_earth * np.cos(theta)
    fig_graph.add_trace(go.Surface(x=xs, y=ys, z=zs, colorscale='Blues', opacity=0.5, showscale=False, name='Terrestrial Reference'))
    fig_graph.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='#00f2ff', width=5), name='Trajectory'))
    fig_graph.update_layout(title="Geocentric Inertial Projection", template="plotly_dark")

    # --- VIEW 4: LIVE PROPAGATION (Animated Satellite) ---
    # We take a subset of data to make the animation smooth
    step = max(1, len(x) // 50) 
    anim_x, anim_y, anim_z = x[::step], y[::step], z[::step]
    
    fig_anim = go.Figure(
        data=[
            go.Surface(x=xs, y=ys, z=zs, colorscale='Viridis', opacity=0.4, showscale=False),
            go.Scatter3d(x=[anim_x.iloc[0]], y=[anim_y.iloc[0]], z=[anim_z.iloc[0]], 
                         mode='markers', marker=dict(size=8, color='#00f2ff', symbol='diamond'), name='Active Sat')
        ],
        layout=go.Layout(title="Real-Time Orbital Propagation", template="plotly_dark",
                         updatemenus=[dict(type="buttons", buttons=[dict(label="Propagate Orbit", method="animate", args=[None])])]),
        frames=[go.Frame(data=[go.Scatter3d(x=[anim_x.iloc[i]], y=[anim_y.iloc[i]], z=[anim_z.iloc[i]])]) for i in range(len(anim_x))]
    )

    # HTML Conversion
    def to_html_comp(fig, include_js=False):
        return fig.to_html(full_html=False, include_plotlyjs='cdn' if include_js else False)

    return f"""
    <html>
        <head>
            <title>Orbital Mission Control</title>
            <style>
                body {{ background: #050505; color: #e0e0e0; font-family: 'Courier New', monospace; margin: 0; overflow: hidden; }}
                .header {{ background: #111; padding: 15px; border-bottom: 2px solid #222; text-align: center; letter-spacing: 2px; color: #00f2ff; }}
                .nav {{ display: flex; justify-content: center; gap: 10px; padding: 15px; background: #0a0a0a; }}
                button {{ background: #1a1a1a; border: 1px solid #333; color: #666; padding: 10px 15px; cursor: pointer; transition: 0.2s; font-size: 12px; text-transform: uppercase; }}
                button.active {{ border-color: #00f2ff; color: #00f2ff; background: #00f2ff11; }}
                .view-container {{ height: calc(100vh - 130px); width: 100%; }}
                .view {{ display: none; height: 100%; }}
                .view.active {{ display: block; }}
            </style>
        </head>
        <body>
            <div class="header">MISSION CONTROL: SATELLITE TRACKING & ORBITAL ANALYSIS</div>
            <div class="nav">
                <button id="btn2d" onclick="show('2d')" class="active">Ground Track</button>
                <button id="btn3ds" onclick="show('3ds')">Orbital Geometry</button>
                <button id="btn3dg" onclick="show('3dg')">Geocentric 3D</button>
                <button id="btnlive" onclick="show('live')">Live Propagation</button>
            </div>
            <div class="view-container">
                <div id="2d" class="view active">{to_html_comp(fig_ground, True)}</div>
                <div id="3ds" class="view">{to_html_comp(fig_geom)}</div>
                <div id="3dg" class="view">{to_html_comp(fig_graph)}</div>
                <div id="live" class="view">{to_html_comp(fig_anim)}</div>
            </div>
            <script>
                function show(id) {{
                    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
                    document.querySelectorAll('button').forEach(b => b.classList.remove('active'));
                    document.getElementById(id).classList.add('active');
                    document.getElementById('btn' + id).classList.add('active');
                    window.dispatchEvent(new Event('resize'));
                }}
            </script>
        </body>
    </html>
    """

@app.route('/')
def home():
    try:
        return generate_dashboard()
    except Exception as e:
        return f"<body style='background:#000;color:#ff0055;font-family:monospace;'><h1>SYSTEM_FAILURE: {str(e)}</h1></body>"
