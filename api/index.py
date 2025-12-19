from flask import Flask
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # 1. Find the CSV file (it's in the same folder as this script)
        csv_path = os.path.join(os.path.dirname(__file__), 'satellite_orbit_track.csv')
        
        # 2. Read the Data
        df = pd.read_csv(csv_path)
        
        # Clean data: Remove rows where Latitude or Longitude is missing
        df = df.dropna(subset=['Latitude', 'Longitude'])

        # 3. Create the Plot
        plt.figure(figsize=(10, 6))
        plt.plot(df['Longitude'], df['Latitude'], 'b.-', label='Satellite Path')
        plt.title('Satellite Orbit Track (Latitude vs Longitude)')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid(True)
        plt.legend()

        # 4. Save Plot to a Memory Buffer (required for Vercel)
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        # 5. Return HTML with the Image
        return f"""
        <html>
            <head><title>Orbit Project</title></head>
            <body style="font-family: sans-serif; text-align: center;">
                <h1>Satellite Orbit Visualization</h1>
                <img src="data:image/png;base64,{plot_url}" style="max-width: 90%; height: auto;" />
            </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

if __name__ == '__main__':
    app.run()
