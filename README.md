# 🛰️ 3D Satellite Orbit Visualization

Hi! 👋 This is a project I built to visualize how satellites actually move around the Earth.

I wanted to move beyond simple 2D charts and create something interactive. This web app reads satellite coordinate data (latitude, longitude, altitude) and plots the orbit trajectory on a **3D rotating globe**.

## 🧐 What does it do?
Instead of just looking at numbers in a CSV file, this app turns that data into a visual experience:
* **3D Earth Model:** You can zoom, rotate, and pan around the globe.
* **Orbit Path:** It draws the actual path of the satellite in red, showing how it wraps around the planet.
* **Real Data:** It uses real-world coordinate data to calculate the 3D positions.

## 🛠️ How I built it
I used **Python** for the backend because it's great for handling data. Here are the main libraries I used:
* **Flask**: To create the web server.
* **Pandas**: To read and clean the CSV data files.
* **Plotly**: To generate the 3D interactive graph (this was the game changer!).
* **Vercel**: For hosting the website online.

## 🚀 How to run it on your laptop
If you want to try this out locally, follow these steps:

1.  **Clone this repo**
    ```bash
    git clone [https://github.com/Abhinandan-KP/orbit-project.git](https://github.com/Abhinandan-KP/orbit-project.git)
    cd orbit-project
    ```

2.  **Install the required libraries**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the app**
    ```bash
    python api/index.py
    ```



## 📝 What I learned
Building this helped me understand how to:
* Connect a Python backend to a frontend visualization.
* Work with 3D coordinate systems (converting Latitude/Longitude to X/Y/Z).
* Deploy a Python app to the cloud using Vercel.

---
*Built by Abhinandan | SRM KTR* 🚀



