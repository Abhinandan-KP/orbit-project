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
    R_earth = 6371 
    Alt_leo = 550  
    
    lat = df['Latitude']
    lon = df['Longitude']
    lat_rad, lon_rad = np.radians(lat), np.radians(lon)

    # Geocentric-Equatorial Transformation
    r = R_earth + Alt_leo
    x = r * np.cos(lat_rad) * np.cos(lon_rad)
    y = r * np.cos(lat_rad) * np.sin(lon_rad)
    z = r * np.sin(lat_rad)

    # Earth Sphere Geometry
    phi, theta = np.meshgrid(np.linspace(0, 2*np.pi, 100), np.linspace(0, np.pi, 100))
    xs, ys, zs = R_earth * np.sin(theta) * np.cos(phi), R_earth * np.sin(theta) * np.sin(phi), R_earth * np.cos(theta)

    # --- VIEW 1: NADIR GROUND TRACK ---
    fig_ground = go.Figure(go.Scattergeo(lat=lat, lon=lon, mode='lines', line=dict(width=2, color='#ff0033')))
    fig_ground.update_layout(template="plotly_dark", margin=dict(l=0,r=0,b=0,t=0),
                            geo=dict(showland=True, landcolor="#0a0a0a", showocean=True, oceancolor="#010101", 
                                    projection_type='orthographic', bgcolor='rgba(0,0,0,0)'))

    # --- VIEW 2: OSCULATING ELEMENTS ---
    fig_geom = go.Figure()
    fig_geom.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='#00f2ff', width=3)))
    fig_geom.update_layout(template="plotly_dark", margin=dict(l=0,r=0,b=0,t=0),
                          scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, bgcolor="#020202"))

    # --- VIEW 3: GEOCENTRIC FRAME ---
    fig_graph = go.Figure()
    fig_graph.add_trace(go.Surface(x=xs, y=ys, z=zs, colorscale=[[0, '#000814'], [1, '#001d3d']], opacity=1, showscale=False))
    fig_graph.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='#ff0033', width=4)))
    fig_graph.update_layout(template="plotly_dark", margin=dict(l=0,r=0,b=0,t=0),
                           scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False))

    # --- VIEW 4: ORBITAL PROPAGATION ---
    step = max(1, len(x) // 100) 
    anim_x, anim_y, anim_z = x[::step], y[::step], z[::step]
    
    fig_anim = go.Figure(
        data=[
            go.Surface(x=xs, y=ys, z=zs, colorscale=[[0, '#000814'], [1, '#003566']], opacity=1, showscale=False),
            go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='rgba(0,242,255,0.2)', width=1)),
            go.Scatter3d(x=[anim_x.iloc[0]], y=[anim_y.iloc[0]], z=[anim_z.iloc[0]], 
                         mode='markers', marker=dict(size=12, color='#ff0033', line=dict(width=2, color='white')))
        ],
        layout=go.Layout(template="plotly_dark", margin=dict(l=0,r=0,b=0,t=0),
                         scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
                         # REMOVED: updatemenus (This removes the white box)
                         ),
        frames=[go.Frame(data=[go.Scatter3d(x=[anim_x.iloc[i]], y=[anim_y.iloc[i]], z=[anim_z.iloc[i]])], name=str(i)) for i in range(len(anim_x))]
    )

    def to_html_comp(fig, id, include_js=False):
        return fig.to_html(full_html=False, include_plotlyjs='cdn' if include_js else False, 
                          config={'displayModeBar': False}, div_id=id)

    return f"""
    <html>
        <head>
            <title>AstroDynamics Control</title>
            <style>
                body {{ background: #010101; color: #00f2ff; font-family: 'Courier New', monospace; margin: 0; overflow: hidden; }}
                .header {{ background: #000; padding: 12px; border-bottom: 1px solid #1a1a1a; text-align: left; font-size: 13px; letter-spacing: 1px; color: #00f2ff; }}
                .nav {{ display: flex; background: #000; padding: 5px 15px; border-bottom: 1px solid #111; }}
                button {{ background: transparent; border: 1px solid #222; color: #444; padding: 10px 18px; cursor: pointer; font-size: 10px; text-transform: uppercase; margin-right: 5px; }}
                button.active {{ color: #ff0033; border: 1px solid #ff0033; background: #ff00330a; }}
                .view-container {{ height: calc(100vh - 90px); width: 100%; }}
                .view {{ display: none; height: 100%; }}
                .view.active {{ display: block; }}
                .overlay {{ position: fixed; bottom: 20px; right: 20px; background: rgba(0,0,0,0.9); padding: 12px; border: 1px solid #1a1a1a; font-size: 9px; line-height: 1.5; color: #666; pointer-events: none; }}
            </style>
        </head>
        <body>
            <div class="header"> [SYS_ID: ALPHA-01] // STATUS: <span style="color:#ff0033">ACTIVE_TRACKING</span> </div>
            <div class="nav">
                <button id="btn2d" onclick="show('2d')" class="active">Sub-Satellite Point</button>
                <button id="btn3ds" onclick="show('3ds')">Osculating Elements</button>
                <button id="btn3dg" onclick="show('3dg')">Geocentric Frame</button>
                <button id="btnlive" onclick="show('live')">Orbital Propagation</button>
            </div>
            <div class="view-container">
                <div id="2d" class="view active">{to_html_comp(fig_ground, 'graph2d', True)}</div>
                <div id="3ds" class="view">{to_html_comp(fig_geom, 'graph3ds')}</div>
                <div id="3dg" class="view">{to_html_comp(fig_graph, 'graph3dg')}</div>
                <div id="live" class="view">{to_html_comp(fig_anim, 'graphlive')}</div>
            </div>
            <div class="overlay">
                EPOCH: 2025.352<br>
                REF_BODY: EARTH_WGS84<br>
                MODEL: SGP4_INTEGRATOR<br>
                SENSORS: NOMINAL
            </div>
            <script>
                function show(id) {{
                    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
                    document.querySelectorAll('button').forEach(b => b.classList.remove('active'));
                    document.getElementById(id).classList.add('active');
                    document.getElementById('btn' + id).classList.add('active');
                    window.dispatchEvent(new Event('resize'));
                    
                    // If switching to live propagation, start the animation automatically
                    if(id === 'live') {{
                        Plotly.animate('graphlive', null, {{
                            frame: {{duration: 60, redraw: true}},
                            fromcurrent: true,
                            mode: 'immediate',
                            loop: true
                        }});
                    }} else {{
                        Plotly.animate('graphlive', [], {{mode: 'immediate'}}); // Stop animation when switching away
                    }}
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
        return f"<body style='background:#000;color:#ff0033;font-family:monospace;'><h1>[DATA_STREAM_INTERRUPT]: {str(e)}</h1></body>"
