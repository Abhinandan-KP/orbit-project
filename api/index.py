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

    # Constants (Astrodynamics)
    R_earth = 6371 # Mean Earth Radius (km)
    Alt_leo = 550  # LEO Orbit altitude for visualization
    
    lat = df['Latitude']
    lon = df['Longitude']
    lat_rad, lon_rad = np.radians(lat), np.radians(lon)

    # Coordinate Transformation: Geocentric-Equatorial System
    r = R_earth + Alt_leo
    x = r * np.cos(lat_rad) * np.cos(lon_rad)
    y = r * np.cos(lat_rad) * np.sin(lon_rad)
    z = r * np.sin(lat_rad)

    # --- VIEW 1: NADIR GROUND TRACK (2D) ---
    fig_ground = go.Figure(go.Scattergeo(lat=lat, lon=lon, mode='lines', line=dict(width=2, color='#ff0033')))
    fig_ground.update_layout(title="Sub-Satellite Nadir Ground Track", template="plotly_dark", margin=dict(l=0,r=0,b=0,t=40),
                            geo=dict(showland=True, landcolor="#0a0a0a", showocean=True, oceancolor="#010101", 
                                    projection_type='orthographic', bgcolor='rgba(0,0,0,0)'))

    # --- VIEW 2: KINEMATIC ENVELOPE (Static 3D) ---
    fig_geom = go.Figure()
    fig_geom.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='#00f2ff', width=3), name='Orbital State Vector'))
    fig_geom.update_layout(title="Kinematic Orbital State Envelope", template="plotly_dark", 
                          scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, bgcolor="#050505"))

    # --- VIEW 3: GEOCENTRIC INERTIAL (3D Graph) ---
    fig_graph = go.Figure()
    # Earth Sphere with "Deep Space" texturing
    phi, theta = np.meshgrid(np.linspace(0, 2*np.pi, 100), np.linspace(0, np.pi, 100))
    xs, ys, zs = R_earth * np.sin(theta) * np.cos(phi), R_earth * np.sin(theta) * np.sin(phi), R_earth * np.cos(theta)
    fig_graph.add_trace(go.Surface(x=xs, y=ys, z=zs, colorscale=[[0, '#001a33'], [1, '#004d99']], opacity=0.9, showscale=False, name='Terrestrial Body'))
    fig_graph.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='#ff0033', width=4), name='Trajectory'))
    fig_graph.update_layout(title="Geocentric-Equatorial Inertial (GEI) Projection", template="plotly_dark")

    # --- VIEW 4: ORBITAL PROPAGATION (Animated Satellite) ---
    step = max(1, len(x) // 100) 
    anim_x, anim_y, anim_z = x[::step], y[::step], z[::step]
    
    fig_anim = go.Figure(
        data=[
            go.Surface(x=xs, y=ys, z=zs, colorscale=[[0, '#000814'], [1, '#001d3d']], opacity=1, showscale=False),
            go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='rgba(255,255,255,0.1)', width=1)),
            go.Scatter3d(x=[anim_x.iloc[0]], y=[anim_y.iloc[0]], z=[anim_z.iloc[0]], 
                         mode='markers', marker=dict(size=10, color='#ff0033', symbol='circle', line=dict(width=2, color='white')), name='Active Transponder')
        ],
        layout=go.Layout(title="TLE Orbital Propagation & Telemetry", template="plotly_dark",
                         updatemenus=[dict(type="buttons", buttons=[dict(label="START PROPAGATION", method="animate", args=[None, {"frame": {"duration": 50, "redraw": True}}])])]),
        frames=[go.Frame(data=[go.Scatter3d(x=[anim_x.iloc[i]], y=[anim_y.iloc[i]], z=[anim_z.iloc[i]])]) for i in range(len(anim_x))]
    )

    def to_html_comp(fig, include_js=False):
        return fig.to_html(full_html=False, include_plotlyjs='cdn' if include_js else False, config={'displayModeBar': False})

    return f"""
    <html>
        <head>
            <title>AstroDynamics Control</title>
            <style>
                body {{ background: #020202; color: #00f2ff; font-family: 'Courier New', monospace; margin: 0; overflow: hidden; }}
                .header {{ background: #000; padding: 10px; border-bottom: 1px solid #00f2ff; text-align: left; letter-spacing: 1px; font-size: 14px; font-weight: bold; }}
                .nav {{ display: flex; justify-content: flex-start; gap: 2px; background: #000; padding: 5px 10px; }}
                button {{ background: #000; border: 1px solid #1a1a1a; color: #444; padding: 8px 15px; cursor: pointer; font-size: 11px; text-transform: uppercase; }}
                button.active {{ color: #ff0033; border: 1px solid #ff0033; background: #ff003311; }}
                .view-container {{ height: calc(100vh - 100px); width: 100%; }}
                .view {{ display: none; height: 100%; }}
                .view.active {{ display: block; }}
                .overlay {{ position: fixed; bottom: 20px; right: 20px; background: rgba(0,0,0,0.8); padding: 10px; border: 1px solid #333; font-size: 10px; pointer-events: none; }}
            </style>
        </head>
        <body>
            <div class="header"> [SATELLITE_ID: ALPHA-01] // STATUS: ORBITAL_TRACKING_ACTIVE </div>
            <div class="nav">
                <button id="btn2d" onclick="show('2d')" class="active">Sub-Satellite Point</button>
                <button id="btn3ds" onclick="show('3ds')">Osculating Elements</button>
                <button id="btn3dg" onclick="show('3dg')">Geocentric Frame</button>
                <button id="btnlive" onclick="show('live')">Orbital Propagation</button>
            </div>
            <div class="view-container">
                <div id="2d" class="view active">{to_html_comp(fig_ground, True)}</div>
                <div id="3ds" class="view">{to_html_comp(fig_geom)}</div>
                <div id="3dg" class="view">{to_html_comp(fig_graph)}</div>
                <div id="live" class="view">{to_html_comp(fig_anim)}</div>
            </div>
            <div class="overlay">
                COORD_SYS: ECEF / J2000<br>
                REF_BODY: EARTH (WGS84)<br>
                PROPAGATION: SGP4_MODEL
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
        return f"<body style='background:#000;color:#ff0033;font-family:monospace;'><h1>[CRITICAL_SYSTEM_ERROR]: {str(e)}</h1></body>"
