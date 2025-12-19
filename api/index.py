from flask import Flask
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

app = Flask(__name__)

def generate_dashboard():
    # 1. Load and Clean Data
    base_path = os.path.dirname(__file__)
    csv_path = os.path.join(base_path, 'satellite_orbit_track.csv')
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Data for 2D View
    lat = df['Latitude']
    lon = df['Longitude']

    # Data for 3D Views (Vector Math)
    R_earth = 6371
    R_orbit = R_earth + 450
    lat_rad, lon_rad = np.radians(lat), np.radians(lon)
    x = R_orbit * np.cos(lat_rad) * np.cos(lon_rad)
    y = R_orbit * np.cos(lat_rad) * np.sin(lon_rad)
    z = R_orbit * np.sin(lat_rad)

    # --- VIEW 1: 2D MAP ---
    fig2d = go.Figure(go.Scattergeo(lat=lat, lon=lon, mode='lines', line=dict(width=2, color='#00f2ff')))
    fig2d.update_layout(title="Global 2D Projection", template="plotly_dark", margin=dict(l=0,r=0,b=0,t=40),
                        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular', bgcolor='rgba(0,0,0,0)'))

    # --- VIEW 2: 3D STATIC ---
    fig3d_static = go.Figure()
    fig3d_static.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='#ff0055', width=3)))
    fig3d_static.update_layout(title="Orbital Envelope", template="plotly_dark", scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False))

    # --- VIEW 3: WORKING 3D (Interactive Globe) ---
    fig3d_work = go.Figure()
    # Earth Sphere
    phi, theta = np.meshgrid(np.linspace(0, 2*np.pi, 60), np.linspace(0, np.pi, 60))
    xs, ys, zs = R_earth * np.sin(theta) * np.cos(phi), R_earth * np.sin(theta) * np.sin(phi), R_earth * np.cos(theta)
    fig3d_work.add_trace(go.Surface(x=xs, y=ys, z=zs, colorscale='Blues', opacity=0.6, showscale=False))
    # Active Path
    fig3d_work.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines+markers', marker=dict(size=2, color='white'), line=dict(color='#00f2ff', width=6)))
    fig3d_work.update_layout(title="Live Working Environment", template="plotly_dark", scene_aspectmode='cube')

    # Convert to HTML
    html_2d = fig2d.to_html(full_html=False, include_plotlyjs='cdn')
    html_3d_s = fig3d_static.to_html(full_html=False, include_plotlyjs=False)
    html_3d_w = fig3d_work.to_html(full_html=False, include_plotlyjs=False)

    return f"""
    <html>
        <head>
            <title>Orbit Dashboard</title>
            <style>
                body {{ background: #0a0a0c; color: white; font-family: 'Segoe UI', sans-serif; margin: 0; overflow: hidden; }}
                .nav {{ display: flex; justify-content: center; gap: 20px; padding: 20px; background: #16161a; border-bottom: 1px solid #333; }}
                button {{ background: #222; border: 1px solid #444; color: #888; padding: 10px 20px; border-radius: 5px; cursor: pointer; transition: 0.3s; }}
                button.active {{ border-color: #00f2ff; color: #00f2ff; box-shadow: 0 0 10px #00f2ff33; }}
                .view-container {{ height: calc(100vh - 80px); width: 100%; }}
                .view {{ display: none; height: 100%; }}
                .view.active {{ display: block; }}
            </style>
        </head>
        <body>
            <div class="nav">
                <button id="btn2d" onclick="show('2d')" class="active">2D View</button>
                <button id="btn3ds" onclick="show('3ds')">3D Static</button>
                <button id="btn3dw" onclick="show('3dw')">Working 3D</button>
            </div>
            <div class="view-container">
                <div id="2d" class="view active">{html_2d}</div>
                <div id="3ds" class="view">{html_3d_s}</div>
                <div id="3dw" class="view">{html_3d_w}</div>
            </div>
            <script>
                function show(id) {{
                    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
                    document.querySelectorAll('button').forEach(b => b.classList.remove('active'));
                    document.getElementById(id).classList.add('active');
                    document.getElementById('btn' + id).classList.add('active');
                    window.dispatchEvent(new Event('resize')); // Forces Plotly to redraw
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
        return f"<body style='background:#000;color:red;'><h1>Data Error</h1>{str(e)}</body>"

app.debug = True
