import base64
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

st.set_page_config(page_title="MTTR Dashboard", layout="wide")
st.title("📊 MTTR Analysis Dashboard")

def make_plot_text_bold(fig):
    fig.update_layout(
        title=dict(font=dict(size=20, family="Arial Black", color="black")),
        font=dict(family="Arial Black", size=14, color="black"),
        legend=dict(font=dict(size=14, family="Arial Black", color="black")),
    )
    fig.update_xaxes(
        title_font=dict(size=16, family="Arial Black", color="black"),
        tickfont=dict(size=14, family="Arial Black", color="black")
    )
    fig.update_yaxes(
        title_font=dict(size=16, family="Arial Black", color="black"),
        tickfont=dict(size=14, family="Arial Black", color="black")
    )


def download_plot_as_html(fig, filename):
    html_bytes = fig.to_html(full_html=True, include_plotlyjs='cdn').encode('utf-8')
    b64 = base64.b64encode(html_bytes).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    return href

# --- DUMMY DATA DOWNLOAD ---
SAMPLE_CSV = """Line-ID,Machine-ID,Start-Time,End-Time,Category Defect,Sub-Category Defect,Down-Time
Line-4,Machine-5,21-11-2024 06:10,21-11-2024 06:41,Hydraulic Defect,Filter Clogging,31.84
Line-3,Machine-3,12-02-2025 02:30,12-02-2025 02:47,Structural Defect,Panel Damage,17.9
Line-4,Machine-2,03-12-2024 11:10,03-12-2024 12:33,Pneumatic Defect,Air Leakage,83.47
Line-4,Machine-1,16-02-2025 22:20,16-02-2025 23:52,Electrical Defect,Pneumatic,92.94
Line-3,Machine-1,12-01-2025 06:10,12-01-2025 08:32,Hydraulic Defect,Filter Clogging,142.84
Line-4,Machine-2,29-01-2025 20:10,29-01-2025 21:55,Mechanical Defect,Belt Breakage,105.79
Line-4,Machine-4,17-12-2024 02:30,17-12-2024 03:34,Structural Defect,Panel Damage,64.75
Line-2,Machine-4,06-11-2024 21:10,06-11-2024 22:39,Pneumatic Defect,Cylinder Failure,89.48
Line-5,Machine-3,14-12-2024 01:10,14-12-2024 03:25,Mechanical Defect,Gear Failure,135.28
Line-4,Machine-1,17-02-2025 17:25,17-02-2025 18:57,Structural Defect,Panel Damage,92.15
Line-1,Machine-4,17-02-2025 08:25,17-02-2025 10:27,Pneumatic Defect,Solenoid Failure,122.31
Line-1,Machine-1,01-11-2024 11:15,01-11-2024 11:52,Electrical Defect,Work head unit,37.84
Line-3,Machine-3,14-02-2025 06:10,14-02-2025 06:36,Electrical Defect,Overload Current,26.22
Line-1,Machine-4,03-12-2024 15:30,03-12-2024 16:25,Pneumatic Defect,Cylinder Failure,55.53
Line-3,Machine-2,04-01-2025 02:25,04-01-2025 04:51,Hydraulic Defect,Valve Blockage,146.04
Line-3,Machine-1,27-02-2025 13:15,27-02-2025 14:38,Structural Defect,Weld Failure,83.18
Line-2,Machine-2,21-12-2024 06:00,21-12-2024 06:54,Pneumatic Defect,Air Leakage,54.01
Line-4,Machine-5,13-12-2024 03:25,13-12-2024 03:45,Structural Defect,Bracket Damage,20.78
Line-3,Machine-3,12-12-2024 12:30,12-12-2024 14:08,Pneumatic Defect,Cylinder Failure,98.68
Line-4,Machine-4,23-01-2025 10:10,23-01-2025 10:37,Pneumatic Defect,Solenoid Failure,27.09
Line-1,Machine-3,27-11-2024 19:25,27-11-2024 21:35,Electrical Defect,Relay Contactor,130.5
Line-3,Machine-1,21-12-2024 09:20,21-12-2024 10:04,Structural Defect,Frame Crack,44.18
Line-3,Machine-2,21-02-2025 16:10,21-02-2025 18:34,Electrical Defect,Loose connection,144.74
Line-2,Machine-3,21-02-2025 16:15,21-02-2025 17:50,Electrical Defect,Overload Current,95.34
Line-2,Machine-4,05-02-2025 00:15,05-02-2025 02:00,Structural Defect,Panel Damage,105.3
Line-5,Machine-2,14-01-2025 16:30,14-01-2025 17:31,Pneumatic Defect,Pressure Drop,61.49
Line-4,Machine-2,12-01-2025 05:25,12-01-2025 07:35,Hydraulic Defect,Oil Leakage,130.17
Line-4,Machine-3,29-01-2025 02:15,29-01-2025 03:13,Pneumatic Defect,Pressure Drop,58.81
Line-4,Machine-1,09-12-2024 17:00,09-12-2024 18:44,Electrical Defect,Work head unit,104.6
Line-1,Machine-1,01-12-2024 09:15,01-12-2024 09:57,Mechanical Defect,Seal Leakage,42.0
Line-2,Machine-4,30-12-2024 16:10,30-12-2024 18:39,Electrical Defect,Loose connection,149.48
Line-4,Machine-5,27-02-2025 08:00,27-02-2025 08:58,Structural Defect,Panel Damage,58.89
Line-3,Machine-2,24-02-2025 10:00,24-02-2025 10:32,Electrical Defect,Work head unit,32.63
Line-4,Machine-3,25-11-2024 17:30,25-11-2024 18:56,Electrical Defect,Pneumatic,86.82
Line-3,Machine-1,03-12-2024 03:00,03-12-2024 04:19,Electrical Defect,Loose connection,79.15
Line-4,Machine-3,18-12-2024 11:15,18-12-2024 12:16,Electrical Defect,Relay Contactor,61.48
Line-5,Machine-3,06-02-2025 20:30,06-02-2025 22:10,Hydraulic Defect,Valve Blockage,100.31
Line-1,Machine-1,18-12-2024 18:20,18-12-2024 18:33,Pneumatic Defect,Air Leakage,13.4
Line-1,Machine-4,06-11-2024 02:20,06-11-2024 02:32,Electrical Defect,Overload Current,12.16
Line-5,Machine-1,07-02-2025 00:20,07-02-2025 01:11,Structural Defect,Bracket Damage,51.22
Line-5,Machine-3,18-11-2024 09:30,18-11-2024 11:17,Electrical Defect,Pneumatic,107.44
Line-2,Machine-4,27-11-2024 09:10,27-11-2024 10:05,Mechanical Defect,Seal Leakage,55.16
Line-1,Machine-1,12-12-2024 22:10,13-12-2024 00:13,Hydraulic Defect,Filter Clogging,123.42
Line-1,Machine-4,07-11-2024 03:25,07-11-2024 04:02,Structural Defect,Panel Damage,37.2
Line-4,Machine-3,05-01-2025 22:30,05-01-2025 23:25,Pneumatic Defect,Cylinder Failure,55.94
Line-2,Machine-3,28-12-2024 21:00,28-12-2024 21:15,Structural Defect,Weld Failure,15.23
Line-3,Machine-1,23-12-2024 11:20,23-12-2024 12:57,Electrical Defect,Work head unit,97.2
Line-4,Machine-5,17-12-2024 02:20,17-12-2024 02:48,Pneumatic Defect,Cylinder Failure,28.58
Line-2,Machine-4,19-11-2024 16:15,19-11-2024 17:26,Mechanical Defect,Spring Failure,71.46
Line-2,Machine-1,01-01-2025 22:00,01-01-2025 23:46,Mechanical Defect,Coupling Failure,106.39
Line-1,Machine-2,19-02-2025 01:30,19-02-2025 01:53,Mechanical Defect,Belt Breakage,23.14
Line-1,Machine-4,01-11-2024 15:25,01-11-2024 17:18,Structural Defect,Frame Crack,113.31
Line-5,Machine-2,06-01-2025 11:10,06-01-2025 12:09,Structural Defect,Bracket Damage,59.84
Line-5,Machine-2,17-12-2024 16:30,17-12-2024 18:39,Electrical Defect,Overload Current,129.76
Line-4,Machine-5,29-01-2025 15:25,29-01-2025 16:41,Pneumatic Defect,Solenoid Failure,76.29
Line-1,Machine-2,10-11-2024 21:25,10-11-2024 23:39,Structural Defect,Bracket Damage,134.14
Line-4,Machine-2,28-12-2024 00:25,28-12-2024 02:10,Mechanical Defect,Bearing Failure,105.75
Line-2,Machine-1,02-12-2024 19:20,02-12-2024 20:24,Pneumatic Defect,Solenoid Failure,64.34
Line-4,Machine-1,13-12-2024 04:20,13-12-2024 05:24,Electrical Defect,Pneumatic,64.05
Line-1,Machine-4,14-12-2024 12:20,14-12-2024 12:44,Mechanical Defect,Bearing Failure,24.11
Line-2,Machine-1,05-12-2024 22:00,05-12-2024 23:41,Hydraulic Defect,Pump Failure,101.8
Line-5,Machine-2,04-12-2024 18:00,04-12-2024 19:19,Mechanical Defect,Gear Failure,79.45
Line-2,Machine-1,14-01-2025 03:00,14-01-2025 05:02,Mechanical Defect,Coupling Failure,122.49
Line-1,Machine-4,12-01-2025 02:00,12-01-2025 03:52,Mechanical Defect,Coupling Failure,112.43
Line-4,Machine-2,04-02-2025 22:30,04-02-2025 23:58,Electrical Defect,Lubrication,88.66
Line-4,Machine-1,28-01-2025 02:00,28-01-2025 03:02,Structural Defect,Bracket Damage,62.88
Line-1,Machine-2,28-01-2025 21:25,28-01-2025 23:40,Pneumatic Defect,Solenoid Failure,135.37
Line-1,Machine-4,13-02-2025 18:20,13-02-2025 19:19,Pneumatic Defect,Air Leakage,59.69
Line-4,Machine-4,19-02-2025 15:25,19-02-2025 15:47,Hydraulic Defect,Pump Failure,22.84
Line-4,Machine-1,24-01-2025 03:25,24-01-2025 05:25,Pneumatic Defect,Pressure Drop,120.82
Line-1,Machine-3,12-12-2024 06:30,12-12-2024 07:56,Structural Defect,Frame Crack,86.93
Line-5,Machine-3,14-01-2025 17:20,14-01-2025 19:06,Structural Defect,Bracket Damage,106.32
Line-2,Machine-4,07-11-2024 13:25,07-11-2024 14:06,Electrical Defect,Wheel spindle,41.16
Line-1,Machine-2,05-01-2025 04:25,05-01-2025 04:46,Hydraulic Defect,Pump Failure,21.88
Line-3,Machine-1,24-02-2025 16:00,24-02-2025 17:32,Electrical Defect,Wheel spindle,92.86
Line-4,Machine-4,16-02-2025 21:15,16-02-2025 21:59,Hydraulic Defect,Filter Clogging,44.82
Line-3,Machine-3,13-11-2024 17:20,13-11-2024 18:50,Hydraulic Defect,Filter Clogging,90.01
Line-4,Machine-4,13-02-2025 06:00,13-02-2025 07:45,Structural Defect,Bracket Damage,105.35
Line-4,Machine-1,25-11-2024 00:30,25-11-2024 01:41,Pneumatic Defect,Air Leakage,71.09
Line-2,Machine-4,15-12-2024 14:25,15-12-2024 14:41,Structural Defect,Panel Damage,16.08
Line-5,Machine-3,06-12-2024 02:15,06-12-2024 04:40,Pneumatic Defect,Air Leakage,145.7
Line-2,Machine-3,14-11-2024 14:00,14-11-2024 15:37,Electrical Defect,Relay Contactor,97.86
Line-3,Machine-3,10-02-2025 11:20,10-02-2025 12:16,Electrical Defect,Work head unit,56.99
Line-2,Machine-4,08-11-2024 17:20,08-11-2024 17:40,Pneumatic Defect,Cylinder Failure,20.88
Line-1,Machine-4,12-01-2025 00:25,12-01-2025 02:28,Hydraulic Defect,Oil Leakage,123.93
Line-4,Machine-5,05-12-2024 05:10,05-12-2024 06:18,Structural Defect,Weld Failure,68.33
Line-5,Machine-3,10-11-2024 17:15,10-11-2024 17:31,Electrical Defect,Sensor Setting,16.33
Line-1,Machine-2,04-02-2025 14:00,04-02-2025 15:02,Electrical Defect,Sensor Setting,62.74
Line-2,Machine-3,29-12-2024 16:25,29-12-2024 16:43,Electrical Defect,Wheel spindle,18.89
Line-1,Machine-3,20-02-2025 22:30,21-02-2025 00:16,Electrical Defect,Overload Current,106.84
Line-5,Machine-3,03-11-2024 20:25,03-11-2024 22:16,Structural Defect,Weld Failure,111.66
Line-2,Machine-2,24-01-2025 13:00,24-01-2025 13:28,Hydraulic Defect,Oil Leakage,28.08
Line-3,Machine-1,01-01-2025 00:00,01-01-2025 01:55,Structural Defect,Panel Damage,115.98
Line-2,Machine-4,04-12-2024 21:30,04-12-2024 23:36,Mechanical Defect,Gear Failure,126.39
Line-2,Machine-4,16-02-2025 04:30,16-02-2025 06:42,Electrical Defect,Wheel spindle,132.73
Line-1,Machine-1,14-11-2024 01:15,14-11-2024 01:54,Structural Defect,Frame Crack,39.81
Line-4,Machine-2,21-01-2025 14:15,21-01-2025 14:37,Mechanical Defect,Gear Failure,22.74
Line-2,Machine-4,05-02-2025 14:20,05-02-2025 15:11,Electrical Defect,Wheel spindle,51.71
Line-2,Machine-3,29-11-2024 03:10,29-11-2024 05:29,Electrical Defect,Overload Current,139.72
Line-2,Machine-1,27-01-2025 04:10,27-01-2025 05:46,Pneumatic Defect,Solenoid Failure,96.91
Line-2,Machine-1,20-02-2025 10:15,20-02-2025 11:40,Hydraulic Defect,Valve Blockage,85.22
Line-3,Machine-2,04-11-2024 02:15,04-11-2024 03:37,Pneumatic Defect,Solenoid Failure,82.13
Line-2,Machine-1,19-11-2024 20:25,19-11-2024 21:23,Mechanical Defect,Bearing Failure,58.31
Line-2,Machine-1,01-11-2024 04:00,01-11-2024 04:59,Structural Defect,Weld Failure,59.84
Line-2,Machine-1,27-11-2024 08:10,27-11-2024 10:11,Mechanical Defect,Coupling Failure,121.92
Line-1,Machine-2,20-01-2025 03:00,20-01-2025 03:21,Hydraulic Defect,Filter Clogging,21.83
Line-3,Machine-1,17-12-2024 21:30,17-12-2024 23:06,Pneumatic Defect,Pressure Drop,96.56
Line-2,Machine-1,29-12-2024 18:15,29-12-2024 20:30,Mechanical Defect,Spring Failure,135.33
Line-3,Machine-3,18-11-2024 05:15,18-11-2024 06:20,Pneumatic Defect,Air Leakage,65.6
Line-1,Machine-3,13-01-2025 06:00,13-01-2025 08:07,Structural Defect,Panel Damage,127.7
Line-2,Machine-2,17-11-2024 12:20,17-11-2024 13:36,Pneumatic Defect,Air Leakage,76.36
Line-2,Machine-3,19-02-2025 03:30,19-02-2025 05:02,Electrical Defect,Sensor Setting,92.16
Line-1,Machine-4,11-12-2024 04:30,11-12-2024 06:45,Hydraulic Defect,Pump Failure,135.95
Line-2,Machine-3,09-01-2025 04:00,09-01-2025 04:43,Hydraulic Defect,Filter Clogging,43.21
Line-5,Machine-2,14-01-2025 22:00,14-01-2025 22:21,Pneumatic Defect,Cylinder Failure,21.23
Line-3,Machine-3,24-11-2024 05:10,24-11-2024 06:40,Structural Defect,Panel Damage,90.64
Line-3,Machine-3,10-02-2025 18:30,10-02-2025 20:50,Electrical Defect,Work head unit,140.11
Line-3,Machine-2,14-12-2024 04:30,14-12-2024 06:55,Hydraulic Defect,Filter Clogging,145.52
Line-4,Machine-3,20-11-2024 16:20,20-11-2024 16:46,Pneumatic Defect,Air Leakage,26.08
Line-2,Machine-2,11-11-2024 03:25,11-11-2024 04:49,Structural Defect,Weld Failure,84.56
Line-1,Machine-2,10-11-2024 04:10,10-11-2024 06:38,Mechanical Defect,Bolt Loosening,148.59
Line-5,Machine-2,02-01-2025 04:00,02-01-2025 05:56,Pneumatic Defect,Air Leakage,116.43
Line-3,Machine-3,08-01-2025 11:10,08-01-2025 11:37,Hydraulic Defect,Oil Leakage,27.4
Line-3,Machine-1,07-02-2025 02:00,07-02-2025 03:53,Mechanical Defect,Shaft Misalignment,113.76
Line-4,Machine-5,09-02-2025 13:20,09-02-2025 13:52,Hydraulic Defect,Oil Leakage,32.91
Line-5,Machine-1,17-01-2025 03:00,17-01-2025 05:12,Structural Defect,Bracket Damage,132.81
Line-1,Machine-2,08-12-2024 00:00,08-12-2024 00:42,Hydraulic Defect,Filter Clogging,42.51
Line-1,Machine-3,23-12-2024 07:15,23-12-2024 08:41,Mechanical Defect,Spring Failure,86.0
Line-3,Machine-3,03-01-2025 19:25,03-01-2025 20:44,Hydraulic Defect,Pump Failure,79.36
Line-3,Machine-1,09-02-2025 22:00,09-02-2025 22:14,Electrical Defect,Relay Contactor,14.69
Line-2,Machine-2,13-01-2025 00:30,13-01-2025 02:34,Structural Defect,Bracket Damage,124.98
Line-4,Machine-5,15-11-2024 07:25,15-11-2024 08:43,Pneumatic Defect,Solenoid Failure,78.09
Line-4,Machine-4,27-11-2024 18:15,27-11-2024 19:44,Structural Defect,Weld Failure,89.17
Line-2,Machine-3,20-11-2024 10:30,20-11-2024 12:47,Hydraulic Defect,Filter Clogging,137.18
Line-2,Machine-2,29-01-2025 12:30,29-01-2025 12:54,Hydraulic Defect,Hose Rupture,24.11
Line-1,Machine-3,15-01-2025 11:20,15-01-2025 13:38,Pneumatic Defect,Pressure Drop,138.63
Line-5,Machine-1,31-01-2025 08:30,31-01-2025 08:50,Mechanical Defect,Belt Breakage,20.82
Line-1,Machine-2,16-12-2024 04:25,16-12-2024 04:58,Hydraulic Defect,Oil Leakage,33.17
Line-4,Machine-1,25-12-2024 18:25,25-12-2024 19:28,Electrical Defect,Wheel spindle,63.1
Line-5,Machine-1,27-12-2024 20:10,27-12-2024 21:06,Mechanical Defect,Shaft Misalignment,56.69
Line-4,Machine-1,08-12-2024 01:10,08-12-2024 02:27,Mechanical Defect,Bearing Failure,77.32
Line-3,Machine-1,16-02-2025 18:30,16-02-2025 19:04,Hydraulic Defect,Valve Blockage,34.69
Line-4,Machine-5,29-11-2024 10:30,29-11-2024 11:10,Electrical Defect,Relay Contactor,40.81
Line-2,Machine-1,20-01-2025 19:00,20-01-2025 19:30,Electrical Defect,Lubrication,30.81
Line-4,Machine-5,01-11-2024 12:30,01-11-2024 14:24,Electrical Defect,Lubrication,114.99
Line-3,Machine-3,15-12-2024 15:15,15-12-2024 15:34,Structural Defect,Frame Crack,19.2
Line-3,Machine-3,26-02-2025 16:10,26-02-2025 17:29,Mechanical Defect,Gear Failure,79.58
Line-3,Machine-3,08-11-2024 22:15,08-11-2024 23:17,Pneumatic Defect,Air Leakage,62.26
Line-2,Machine-3,05-02-2025 22:20,06-02-2025 00:27,Mechanical Defect,Shaft Misalignment,127.57
Line-5,Machine-1,06-01-2025 22:15,06-01-2025 23:35,Electrical Defect,Lubrication,80.77
Line-1,Machine-3,21-12-2024 00:20,21-12-2024 01:03,Structural Defect,Bracket Damage,43.35
Line-2,Machine-3,24-02-2025 04:30,24-02-2025 05:08,Hydraulic Defect,Hose Rupture,38.7
Line-2,Machine-3,03-12-2024 22:25,03-12-2024 22:38,Mechanical Defect,Seal Leakage,13.71
Line-5,Machine-3,30-12-2024 17:10,30-12-2024 19:27,Pneumatic Defect,Air Leakage,137.49
Line-5,Machine-3,02-11-2024 02:20,02-11-2024 04:26,Mechanical Defect,Seal Leakage,126.29
Line-5,Machine-2,23-12-2024 11:15,23-12-2024 13:37,Electrical Defect,Sensor Setting,142.78
Line-4,Machine-1,29-12-2024 13:00,29-12-2024 14:17,Mechanical Defect,Spring Failure,77.87
Line-1,Machine-2,05-01-2025 12:00,05-01-2025 12:46,Electrical Defect,Work head unit,46.1
Line-3,Machine-2,28-12-2024 12:10,28-12-2024 12:58,Pneumatic Defect,Cylinder Failure,48.12
Line-3,Machine-2,24-01-2025 09:20,24-01-2025 10:39,Mechanical Defect,Bolt Loosening,79.73
Line-2,Machine-1,10-02-2025 11:25,10-02-2025 11:36,Structural Defect,Frame Crack,11.54
Line-5,Machine-3,30-01-2025 07:10,30-01-2025 08:44,Electrical Defect,Wheel spindle,94.07
Line-1,Machine-1,17-11-2024 20:20,17-11-2024 22:17,Mechanical Defect,Coupling Failure,117.93
Line-2,Machine-4,21-12-2024 20:20,21-12-2024 22:17,Hydraulic Defect,Oil Leakage,117.94
Line-5,Machine-1,06-12-2024 16:15,06-12-2024 17:06,Hydraulic Defect,Valve Blockage,51.6
Line-3,Machine-2,19-02-2025 21:30,19-02-2025 23:22,Mechanical Defect,Seal Leakage,112.56
Line-1,Machine-2,20-11-2024 18:15,20-11-2024 20:22,Pneumatic Defect,Pressure Drop,127.81
Line-1,Machine-2,15-02-2025 01:00,15-02-2025 02:57,Hydraulic Defect,Filter Clogging,117.93
Line-5,Machine-1,17-11-2024 00:00,17-11-2024 01:48,Electrical Defect,Work head unit,108.69
Line-2,Machine-1,22-02-2025 04:20,22-02-2025 06:07,Hydraulic Defect,Valve Blockage,107.26
Line-2,Machine-4,14-12-2024 16:25,14-12-2024 18:25,Hydraulic Defect,Filter Clogging,120.6
Line-1,Machine-3,22-01-2025 07:25,22-01-2025 09:21,Electrical Defect,Work head unit,116.27
Line-5,Machine-2,28-01-2025 11:15,28-01-2025 13:43,Electrical Defect,Sensor Setting,148.27
Line-5,Machine-2,10-01-2025 16:10,10-01-2025 17:39,Mechanical Defect,Bolt Loosening,89.51
Line-2,Machine-3,09-11-2024 18:10,09-11-2024 19:19,Structural Defect,Bracket Damage,69.05
Line-5,Machine-2,07-02-2025 17:15,07-02-2025 19:21,Pneumatic Defect,Pressure Drop,126.05
Line-1,Machine-2,30-12-2024 12:10,30-12-2024 14:23,Hydraulic Defect,Hose Rupture,133.9
Line-3,Machine-2,15-11-2024 16:20,15-11-2024 18:20,Pneumatic Defect,Pressure Drop,120.7
Line-1,Machine-1,16-11-2024 12:10,16-11-2024 14:22,Mechanical Defect,Belt Breakage,132.73
Line-2,Machine-3,04-12-2024 22:25,04-12-2024 23:49,Hydraulic Defect,Pump Failure,84.05
Line-3,Machine-3,01-01-2025 16:25,01-01-2025 16:40,Pneumatic Defect,Air Leakage,15.26
Line-4,Machine-1,10-11-2024 06:20,10-11-2024 08:13,Pneumatic Defect,Pressure Drop,113.26
Line-1,Machine-3,30-11-2024 17:20,30-11-2024 19:10,Structural Defect,Weld Failure,110.18
Line-5,Machine-1,18-02-2025 14:00,18-02-2025 14:25,Electrical Defect,Overload Current,25.33
Line-1,Machine-4,29-12-2024 04:25,29-12-2024 05:11,Pneumatic Defect,Solenoid Failure,46.26
Line-4,Machine-3,25-11-2024 06:20,25-11-2024 06:39,Structural Defect,Weld Failure,19.1
Line-4,Machine-5,17-02-2025 13:10,17-02-2025 13:26,Structural Defect,Bracket Damage,16.57
Line-1,Machine-2,03-11-2024 05:25,03-11-2024 05:43,Electrical Defect,Relay Contactor,18.1
Line-1,Machine-1,21-02-2025 09:15,21-02-2025 11:11,Hydraulic Defect,Hose Rupture,116.15
Line-1,Machine-4,10-02-2025 12:25,10-02-2025 13:50,Hydraulic Defect,Valve Blockage,85.18
Line-1,Machine-4,11-11-2024 08:15,11-11-2024 09:03,Structural Defect,Weld Failure,48.21
Line-5,Machine-1,06-02-2025 11:10,06-02-2025 13:13,Hydraulic Defect,Oil Leakage,123.33
Line-1,Machine-1,06-02-2025 14:30,06-02-2025 15:16,Hydraulic Defect,Valve Blockage,46.37
Line-5,Machine-2,07-12-2024 15:25,07-12-2024 17:40,Mechanical Defect,Spring Failure,135.23
Line-5,Machine-1,15-12-2024 18:10,15-12-2024 19:39,Mechanical Defect,Bolt Loosening,89.98
Line-2,Machine-4,17-02-2025 00:30,17-02-2025 01:52,Hydraulic Defect,Filter Clogging,82.98
Line-4,Machine-1,18-12-2024 08:25,18-12-2024 10:32,Hydraulic Defect,Valve Blockage,127.18
Line-1,Machine-1,02-01-2025 05:20,02-01-2025 05:52,Mechanical Defect,Shaft Misalignment,32.2
Line-3,Machine-1,23-02-2025 22:10,23-02-2025 22:38,Mechanical Defect,Belt Breakage,28.04
Line-3,Machine-1,02-11-2024 13:25,02-11-2024 14:46,Mechanical Defect,Shaft Misalignment,81.05
Line-2,Machine-4,27-11-2024 16:00,27-11-2024 17:38,Structural Defect,Weld Failure,98.45
Line-2,Machine-4,20-02-2025 05:15,20-02-2025 07:11,Structural Defect,Bracket Damage,116.54
Line-2,Machine-1,28-11-2024 14:30,28-11-2024 16:25,Mechanical Defect,Seal Leakage,115.52
Line-4,Machine-4,07-01-2025 16:20,07-01-2025 16:39,Pneumatic Defect,Cylinder Failure,19.43
Line-2,Machine-2,29-01-2025 17:10,29-01-2025 19:38,Electrical Defect,Wheel spindle,148.62
Line-5,Machine-3,15-01-2025 06:25,15-01-2025 06:38,Hydraulic Defect,Hose Rupture,13.1
Line-3,Machine-3,26-11-2024 01:30,26-11-2024 02:45,Mechanical Defect,Seal Leakage,75.6
Line-4,Machine-1,13-02-2025 06:25,13-02-2025 08:12,Hydraulic Defect,Filter Clogging,107.12
Line-4,Machine-2,14-01-2025 02:00,14-01-2025 04:24,Pneumatic Defect,Cylinder Failure,144.85
Line-4,Machine-5,19-01-2025 04:15,19-01-2025 06:40,Structural Defect,Bracket Damage,145.03
Line-3,Machine-1,01-11-2024 05:10,01-11-2024 05:49,Structural Defect,Bracket Damage,39.83
Line-1,Machine-1,15-11-2024 11:15,15-11-2024 13:40,Pneumatic Defect,Cylinder Failure,145.55
Line-1,Machine-1,08-11-2024 14:15,08-11-2024 16:23,Structural Defect,Frame Crack,128.27
Line-4,Machine-3,14-12-2024 20:20,14-12-2024 22:45,Structural Defect,Panel Damage,145.45
Line-4,Machine-1,08-02-2025 08:30,08-02-2025 09:11,Electrical Defect,Loose connection,41.58
Line-4,Machine-5,27-01-2025 07:15,27-01-2025 09:42,Structural Defect,Weld Failure,147.81
Line-1,Machine-4,02-02-2025 17:30,02-02-2025 19:56,Structural Defect,Weld Failure,146.46
Line-3,Machine-1,10-02-2025 08:15,10-02-2025 09:32,Electrical Defect,Relay Contactor,77.27
Line-1,Machine-1,16-12-2024 14:30,16-12-2024 16:06,Pneumatic Defect,Air Leakage,96.54
Line-4,Machine-1,02-12-2024 17:20,02-12-2024 17:40,Mechanical Defect,Bolt Loosening,20.14
Line-1,Machine-1,16-01-2025 19:10,16-01-2025 20:15,Electrical Defect,Relay Contactor,65.57
Line-2,Machine-2,22-02-2025 14:10,22-02-2025 14:25,Mechanical Defect,Spring Failure,15.77
Line-4,Machine-1,06-01-2025 05:00,06-01-2025 07:21,Hydraulic Defect,Filter Clogging,141.07
Line-1,Machine-2,11-01-2025 17:20,11-01-2025 19:22,Pneumatic Defect,Solenoid Failure,122.24
Line-3,Machine-3,19-01-2025 03:30,19-01-2025 05:34,Hydraulic Defect,Hose Rupture,124.42
Line-2,Machine-3,30-12-2024 09:30,30-12-2024 09:51,Hydraulic Defect,Oil Leakage,21.43
Line-4,Machine-4,15-12-2024 18:10,15-12-2024 19:06,Structural Defect,Frame Crack,56.06
Line-4,Machine-5,23-12-2024 22:15,23-12-2024 22:47,Structural Defect,Bracket Damage,32.63
Line-2,Machine-3,26-12-2024 08:15,26-12-2024 09:56,Structural Defect,Panel Damage,101.05
Line-2,Machine-3,01-02-2025 21:00,01-02-2025 23:07,Hydraulic Defect,Filter Clogging,127.66
Line-1,Machine-2,28-12-2024 19:25,28-12-2024 20:23,Structural Defect,Bracket Damage,58.43
Line-4,Machine-4,20-12-2024 16:15,20-12-2024 17:46,Pneumatic Defect,Solenoid Failure,91.01
Line-4,Machine-2,08-02-2025 01:10,08-02-2025 03:11,Structural Defect,Weld Failure,121.01
Line-2,Machine-3,26-02-2025 11:15,26-02-2025 12:52,Hydraulic Defect,Pump Failure,97.22
Line-5,Machine-3,26-11-2024 07:20,26-11-2024 09:37,Electrical Defect,Pneumatic,137.26
Line-2,Machine-4,07-12-2024 04:30,07-12-2024 05:48,Mechanical Defect,Seal Leakage,78.92
Line-4,Machine-5,02-11-2024 06:30,02-11-2024 08:11,Electrical Defect,Loose connection,101.3
Line-1,Machine-1,05-12-2024 04:25,05-12-2024 05:20,Pneumatic Defect,Cylinder Failure,55.53
Line-4,Machine-4,17-12-2024 10:10,17-12-2024 10:30,Structural Defect,Bracket Damage,20.29
Line-2,Machine-1,02-02-2025 08:00,02-02-2025 09:12,Mechanical Defect,Shaft Misalignment,72.92
Line-3,Machine-1,23-01-2025 10:25,23-01-2025 11:24,Electrical Defect,Wheel spindle,59.94
Line-4,Machine-5,14-12-2024 14:30,14-12-2024 15:08,Electrical Defect,Relay Contactor,38.82
Line-5,Machine-2,07-12-2024 19:10,07-12-2024 19:25,Mechanical Defect,Belt Breakage,15.51
Line-3,Machine-2,29-12-2024 04:00,29-12-2024 05:21,Structural Defect,Frame Crack,81.01
Line-4,Machine-2,22-02-2025 10:30,22-02-2025 12:53,Pneumatic Defect,Air Leakage,143.25
Line-2,Machine-1,03-02-2025 14:15,03-02-2025 15:33,Electrical Defect,Lubrication,78.44
Line-4,Machine-4,19-01-2025 17:10,19-01-2025 19:02,Structural Defect,Panel Damage,112.61
Line-2,Machine-1,08-11-2024 05:25,08-11-2024 07:49,Electrical Defect,Lubrication,144.87
Line-2,Machine-1,13-01-2025 17:10,13-01-2025 18:46,Mechanical Defect,Bearing Failure,96.5
Line-1,Machine-4,16-12-2024 03:00,16-12-2024 04:34,Hydraulic Defect,Oil Leakage,94.09
Line-5,Machine-1,22-02-2025 05:00,22-02-2025 07:11,Electrical Defect,Sensor Setting,131.3
Line-1,Machine-4,25-02-2025 12:00,25-02-2025 12:25,Structural Defect,Frame Crack,25.28
Line-2,Machine-1,19-11-2024 05:10,19-11-2024 07:06,Pneumatic Defect,Cylinder Failure,116.72
Line-1,Machine-3,14-01-2025 00:30,14-01-2025 01:56,Hydraulic Defect,Filter Clogging,86.23
Line-1,Machine-1,15-11-2024 20:15,15-11-2024 21:19,Electrical Defect,Lubrication,64.4
Line-1,Machine-1,05-12-2024 11:30,05-12-2024 11:50,Electrical Defect,Relay Contactor,20.25
Line-3,Machine-2,16-12-2024 08:15,16-12-2024 09:40,Mechanical Defect,Gear Failure,85.93
Line-2,Machine-2,01-02-2025 11:25,01-02-2025 12:30,Pneumatic Defect,Air Leakage,65.84
Line-5,Machine-3,15-11-2024 10:30,15-11-2024 12:24,Pneumatic Defect,Solenoid Failure,114.56
Line-4,Machine-3,21-11-2024 22:15,21-11-2024 22:26,Hydraulic Defect,Filter Clogging,11.06
Line-5,Machine-3,14-01-2025 18:20,14-01-2025 20:40,Electrical Defect,Loose connection,140.82
Line-3,Machine-2,20-02-2025 20:20,20-02-2025 22:03,Structural Defect,Panel Damage,103.81
Line-5,Machine-3,08-11-2024 15:10,08-11-2024 16:45,Pneumatic Defect,Pressure Drop,95.45
Line-2,Machine-2,29-01-2025 10:20,29-01-2025 10:55,Electrical Defect,Loose connection,35.4
Line-5,Machine-3,06-12-2024 19:20,06-12-2024 19:42,Electrical Defect,Work head unit,22.19
Line-1,Machine-4,17-12-2024 12:30,17-12-2024 14:34,Structural Defect,Weld Failure,124.69
Line-4,Machine-1,15-11-2024 09:10,15-11-2024 10:10,Mechanical Defect,Belt Breakage,60.51
Line-2,Machine-4,07-01-2025 17:15,07-01-2025 19:24,Electrical Defect,Overload Current,129.16
Line-2,Machine-1,06-12-2024 09:00,06-12-2024 10:09,Mechanical Defect,Bearing Failure,69.35
Line-5,Machine-3,16-02-2025 01:00,16-02-2025 01:40,Electrical Defect,Pneumatic,40.34
Line-1,Machine-2,05-12-2024 06:15,05-12-2024 06:57,Structural Defect,Bracket Damage,42.47
Line-5,Machine-1,02-11-2024 02:25,02-11-2024 04:09,Electrical Defect,Robot,104.62
Line-2,Machine-2,11-12-2024 16:15,11-12-2024 18:43,Structural Defect,Bracket Damage,148.78
Line-4,Machine-3,10-02-2025 09:25,10-02-2025 09:46,Pneumatic Defect,Cylinder Failure,21.12
Line-5,Machine-1,12-01-2025 07:00,12-01-2025 07:41,Pneumatic Defect,Pressure Drop,41.73
Line-1,Machine-3,19-12-2024 01:20,19-12-2024 03:22,Pneumatic Defect,Air Leakage,122.05
Line-3,Machine-1,26-02-2025 11:25,26-02-2025 12:38,Mechanical Defect,Bearing Failure,73.96
Line-2,Machine-3,10-02-2025 16:15,10-02-2025 18:07,Pneumatic Defect,Cylinder Failure,112.29
Line-4,Machine-4,08-01-2025 12:25,08-01-2025 14:11,Mechanical Defect,Shaft Misalignment,106.6
Line-1,Machine-3,30-11-2024 22:20,30-11-2024 23:18,Mechanical Defect,Spring Failure,58.66
Line-4,Machine-4,23-11-2024 18:30,23-11-2024 20:58,Hydraulic Defect,Filter Clogging,148.95
Line-4,Machine-1,23-01-2025 05:30,23-01-2025 05:52,Electrical Defect,Overload Current,22.48
Line-1,Machine-1,24-02-2025 01:25,24-02-2025 01:40,Pneumatic Defect,Cylinder Failure,15.06
Line-1,Machine-3,05-01-2025 08:25,05-01-2025 09:23,Mechanical Defect,Coupling Failure,58.49
Line-1,Machine-1,22-12-2024 22:10,22-12-2024 23:44,Electrical Defect,Pneumatic,94.08
Line-3,Machine-2,09-02-2025 19:10,09-02-2025 20:30,Hydraulic Defect,Hose Rupture,80.16
Line-1,Machine-2,05-12-2024 09:30,05-12-2024 11:21,Mechanical Defect,Coupling Failure,111.0
Line-3,Machine-3,12-01-2025 14:25,12-01-2025 14:38,Pneumatic Defect,Cylinder Failure,13.21
Line-3,Machine-2,17-01-2025 19:10,17-01-2025 20:49,Hydraulic Defect,Pump Failure,99.74
Line-1,Machine-2,03-12-2024 03:30,03-12-2024 03:59,Electrical Defect,Wheel spindle,29.49
Line-5,Machine-3,06-11-2024 12:25,06-11-2024 12:52,Hydraulic Defect,Oil Leakage,27.05
Line-5,Machine-2,18-01-2025 03:25,18-01-2025 04:51,Pneumatic Defect,Air Leakage,86.93
Line-4,Machine-5,01-02-2025 05:25,01-02-2025 05:37,Pneumatic Defect,Cylinder Failure,12.48
Line-2,Machine-4,05-11-2024 18:10,05-11-2024 19:24,Hydraulic Defect,Valve Blockage,74.37
Line-2,Machine-2,01-12-2024 14:00,01-12-2024 15:10,Hydraulic Defect,Pump Failure,70.25
Line-1,Machine-3,28-11-2024 13:15,28-11-2024 13:49,Structural Defect,Frame Crack,34.89
Line-4,Machine-1,11-02-2025 07:00,11-02-2025 07:42,Pneumatic Defect,Solenoid Failure,42.57
Line-4,Machine-4,06-12-2024 05:10,06-12-2024 05:38,Structural Defect,Panel Damage,28.3
Line-4,Machine-5,31-01-2025 21:30,31-01-2025 22:04,Hydraulic Defect,Valve Blockage,34.76
Line-5,Machine-2,25-12-2024 01:30,25-12-2024 02:47,Structural Defect,Weld Failure,77.39
Line-5,Machine-2,09-12-2024 04:00,09-12-2024 04:55,Mechanical Defect,Bolt Loosening,55.29
Line-2,Machine-2,23-12-2024 17:25,23-12-2024 19:49,Structural Defect,Frame Crack,144.34
Line-4,Machine-1,30-12-2024 10:25,30-12-2024 12:33,Hydraulic Defect,Oil Leakage,128.21
Line-5,Machine-2,22-12-2024 15:20,22-12-2024 17:01,Pneumatic Defect,Cylinder Failure,101.24
Line-3,Machine-1,29-11-2024 05:10,29-11-2024 07:09,Structural Defect,Panel Damage,119.9
Line-5,Machine-1,09-11-2024 08:00,09-11-2024 10:03,Electrical Defect,Relay Contactor,123.24
Line-5,Machine-1,28-12-2024 07:25,28-12-2024 09:30,Mechanical Defect,Gear Failure,125.52
Line-2,Machine-4,18-01-2025 16:20,18-01-2025 17:33,Hydraulic Defect,Oil Leakage,73.09
Line-5,Machine-3,14-12-2024 00:25,14-12-2024 00:41,Structural Defect,Panel Damage,16.7
Line-1,Machine-3,17-02-2025 18:15,17-02-2025 18:26,Hydraulic Defect,Oil Leakage,11.7
Line-5,Machine-1,18-02-2025 03:15,18-02-2025 05:40,Mechanical Defect,Seal Leakage,145.9
Line-3,Machine-3,21-12-2024 10:10,21-12-2024 10:33,Hydraulic Defect,Hose Rupture,23.78
Line-2,Machine-2,03-02-2025 07:00,03-02-2025 09:26,Pneumatic Defect,Air Leakage,146.64
Line-2,Machine-3,07-01-2025 13:00,07-01-2025 14:40,Electrical Defect,Loose connection,100.15
Line-2,Machine-3,21-11-2024 03:20,21-11-2024 04:36,Mechanical Defect,Gear Failure,76.41
Line-2,Machine-2,02-12-2024 15:20,02-12-2024 15:51,Structural Defect,Frame Crack,31.93
Line-2,Machine-3,18-11-2024 22:00,18-11-2024 23:02,Electrical Defect,Work head unit,62.1
Line-3,Machine-2,28-01-2025 17:30,28-01-2025 18:18,Pneumatic Defect,Cylinder Failure,48.33
Line-4,Machine-5,21-12-2024 13:00,21-12-2024 14:40,Pneumatic Defect,Solenoid Failure,100.41
Line-3,Machine-2,17-12-2024 17:25,17-12-2024 19:20,Electrical Defect,Robot,115.71
Line-5,Machine-2,14-01-2025 21:30,14-01-2025 23:57,Pneumatic Defect,Solenoid Failure,147.85
Line-4,Machine-5,02-11-2024 20:20,02-11-2024 22:24,Structural Defect,Weld Failure,124.49
Line-3,Machine-3,22-11-2024 10:25,22-11-2024 11:57,Pneumatic Defect,Air Leakage,92.65
Line-3,Machine-3,30-11-2024 06:20,30-11-2024 07:59,Hydraulic Defect,Filter Clogging,99.08
Line-5,Machine-3,16-11-2024 07:00,16-11-2024 08:53,Mechanical Defect,Gear Failure,113.84
Line-3,Machine-1,07-02-2025 09:10,07-02-2025 09:48,Pneumatic Defect,Solenoid Failure,38.56
Line-2,Machine-1,05-01-2025 08:25,05-01-2025 09:50,Hydraulic Defect,Valve Blockage,85.42
Line-4,Machine-2,24-12-2024 11:00,24-12-2024 11:11,Mechanical Defect,Gear Failure,11.54
Line-1,Machine-2,20-11-2024 10:15,20-11-2024 12:22,Structural Defect,Frame Crack,127.88
Line-3,Machine-1,19-02-2025 03:20,19-02-2025 05:19,Mechanical Defect,Shaft Misalignment,119.26
Line-3,Machine-2,24-01-2025 21:25,24-01-2025 21:39,Structural Defect,Weld Failure,14.07
Line-4,Machine-4,17-11-2024 22:20,17-11-2024 23:41,Electrical Defect,Loose connection,81.42
Line-3,Machine-1,24-02-2025 03:30,24-02-2025 04:48,Mechanical Defect,Seal Leakage,78.12
Line-2,Machine-3,19-11-2024 16:30,19-11-2024 17:00,Pneumatic Defect,Solenoid Failure,30.86
Line-5,Machine-2,25-02-2025 03:15,25-02-2025 04:26,Mechanical Defect,Spring Failure,71.63
Line-4,Machine-1,02-01-2025 19:00,02-01-2025 20:33,Electrical Defect,Sensor Setting,93.75
Line-3,Machine-3,26-02-2025 12:00,26-02-2025 13:08,Hydraulic Defect,Oil Leakage,68.97
Line-4,Machine-4,14-01-2025 06:00,14-01-2025 08:23,Hydraulic Defect,Hose Rupture,143.04
Line-5,Machine-1,10-11-2024 17:15,10-11-2024 17:28,Pneumatic Defect,Air Leakage,13.67
Line-1,Machine-2,20-01-2025 12:15,20-01-2025 14:36,Structural Defect,Weld Failure,141.7
Line-2,Machine-3,08-01-2025 04:20,08-01-2025 06:22,Mechanical Defect,Bearing Failure,122.37
Line-2,Machine-4,09-01-2025 03:30,09-01-2025 05:21,Structural Defect,Panel Damage,111.91
Line-2,Machine-3,27-12-2024 03:30,27-12-2024 03:48,Electrical Defect,Work head unit,18.02
Line-4,Machine-4,01-12-2024 19:00,01-12-2024 21:23,Pneumatic Defect,Air Leakage,143.93
Line-4,Machine-2,05-12-2024 22:20,06-12-2024 00:20,Pneumatic Defect,Pressure Drop,120.2
Line-2,Machine-4,16-01-2025 05:20,16-01-2025 05:51,Mechanical Defect,Belt Breakage,31.89
Line-4,Machine-3,15-02-2025 20:20,15-02-2025 21:14,Pneumatic Defect,Cylinder Failure,54.13
Line-3,Machine-3,14-01-2025 19:25,14-01-2025 19:42,Mechanical Defect,Bolt Loosening,17.32
Line-4,Machine-1,21-11-2024 17:25,21-11-2024 19:06,Structural Defect,Weld Failure,101.58
Line-2,Machine-1,23-02-2025 20:20,23-02-2025 21:18,Electrical Defect,Pneumatic,58.93
Line-1,Machine-1,07-01-2025 09:00,07-01-2025 11:09,Mechanical Defect,Coupling Failure,129.09
Line-1,Machine-1,06-02-2025 10:00,06-02-2025 12:00,Structural Defect,Frame Crack,120.84
Line-1,Machine-1,18-02-2025 05:10,18-02-2025 06:27,Mechanical Defect,Spring Failure,77.86
Line-5,Machine-1,20-02-2025 01:10,20-02-2025 02:24,Mechanical Defect,Spring Failure,74.72
Line-3,Machine-1,19-02-2025 07:30,19-02-2025 09:32,Pneumatic Defect,Solenoid Failure,122.9
Line-2,Machine-3,03-01-2025 06:25,03-01-2025 06:58,Hydraulic Defect,Oil Leakage,33.06
Line-4,Machine-4,25-01-2025 19:20,25-01-2025 20:05,Structural Defect,Bracket Damage,45.77
Line-5,Machine-1,26-11-2024 16:10,26-11-2024 16:29,Mechanical Defect,Shaft Misalignment,19.13
Line-3,Machine-1,07-02-2025 05:20,07-02-2025 06:33,Mechanical Defect,Shaft Misalignment,73.24
Line-3,Machine-2,08-01-2025 18:15,08-01-2025 18:53,Hydraulic Defect,Valve Blockage,38.53
Line-2,Machine-4,11-12-2024 03:25,11-12-2024 05:03,Pneumatic Defect,Solenoid Failure,98.84
Line-1,Machine-3,30-12-2024 19:30,30-12-2024 21:31,Mechanical Defect,Gear Failure,121.06
Line-3,Machine-1,22-02-2025 10:30,22-02-2025 10:59,Hydraulic Defect,Valve Blockage,29.7
Line-1,Machine-3,18-12-2024 10:25,18-12-2024 11:36,Structural Defect,Panel Damage,71.65
Line-3,Machine-1,16-12-2024 22:00,16-12-2024 23:08,Pneumatic Defect,Pressure Drop,68.49
Line-5,Machine-1,04-11-2024 05:10,04-11-2024 06:19,Structural Defect,Weld Failure,69.85
Line-3,Machine-1,05-02-2025 03:00,05-02-2025 05:05,Electrical Defect,Pneumatic,125.21
Line-2,Machine-2,31-12-2024 08:20,31-12-2024 10:38,Structural Defect,Bracket Damage,138.55
Line-3,Machine-1,17-12-2024 11:20,17-12-2024 12:13,Hydraulic Defect,Pump Failure,53.97
Line-2,Machine-2,31-01-2025 15:25,31-01-2025 15:50,Hydraulic Defect,Hose Rupture,25.81
Line-2,Machine-2,05-12-2024 19:10,05-12-2024 20:08,Electrical Defect,Overload Current,58.71
Line-2,Machine-2,23-11-2024 15:30,23-11-2024 17:23,Hydraulic Defect,Oil Leakage,113.33
Line-4,Machine-3,03-12-2024 19:25,03-12-2024 21:09,Hydraulic Defect,Valve Blockage,104.66
Line-2,Machine-3,09-12-2024 05:00,09-12-2024 06:41,Pneumatic Defect,Pressure Drop,101.74
Line-1,Machine-4,28-12-2024 14:30,28-12-2024 15:30,Hydraulic Defect,Hose Rupture,60.45
Line-5,Machine-3,23-12-2024 13:20,23-12-2024 15:41,Electrical Defect,Overload Current,141.36
Line-4,Machine-1,16-01-2025 14:10,16-01-2025 15:51,Electrical Defect,Pneumatic,101.11
Line-3,Machine-3,06-02-2025 13:30,06-02-2025 14:11,Hydraulic Defect,Valve Blockage,41.74
Line-5,Machine-2,30-11-2024 13:15,30-11-2024 14:24,Hydraulic Defect,Valve Blockage,69.16
Line-1,Machine-4,26-01-2025 21:00,26-01-2025 21:50,Mechanical Defect,Spring Failure,50.91
Line-3,Machine-3,12-01-2025 19:25,12-01-2025 21:49,Mechanical Defect,Bearing Failure,144.79
Line-1,Machine-3,19-11-2024 14:20,19-11-2024 14:45,Pneumatic Defect,Pressure Drop,25.76
Line-5,Machine-1,20-01-2025 08:00,20-01-2025 09:15,Pneumatic Defect,Solenoid Failure,75.63
Line-1,Machine-2,07-02-2025 08:15,07-02-2025 10:07,Hydraulic Defect,Filter Clogging,112.23
Line-1,Machine-4,31-01-2025 07:10,31-01-2025 08:53,Hydraulic Defect,Hose Rupture,103.49
Line-1,Machine-4,21-02-2025 15:30,21-02-2025 16:40,Structural Defect,Weld Failure,70.09
Line-3,Machine-2,21-11-2024 04:20,21-11-2024 05:00,Mechanical Defect,Coupling Failure,40.83
Line-4,Machine-1,12-01-2025 08:20,12-01-2025 10:31,Structural Defect,Frame Crack,131.6
Line-2,Machine-4,15-12-2024 22:20,16-12-2024 00:37,Electrical Defect,Work head unit,137.49
Line-1,Machine-3,01-02-2025 21:25,01-02-2025 23:03,Mechanical Defect,Shaft Misalignment,98.38
Line-4,Machine-1,04-11-2024 22:20,04-11-2024 22:44,Structural Defect,Bracket Damage,24.59
Line-4,Machine-5,05-01-2025 01:15,05-01-2025 03:09,Hydraulic Defect,Hose Rupture,114.1
Line-1,Machine-4,17-11-2024 11:30,17-11-2024 11:46,Electrical Defect,Sensor Setting,16.39
Line-3,Machine-2,01-02-2025 12:00,01-02-2025 13:37,Electrical Defect,Robot,97.15
Line-3,Machine-1,19-12-2024 12:25,19-12-2024 12:35,Pneumatic Defect,Solenoid Failure,10.77
Line-1,Machine-2,05-02-2025 06:25,05-02-2025 07:36,Hydraulic Defect,Hose Rupture,71.4
Line-2,Machine-3,27-01-2025 04:00,27-01-2025 05:36,Electrical Defect,Robot,96.39
Line-5,Machine-3,09-12-2024 12:15,09-12-2024 12:31,Hydraulic Defect,Oil Leakage,16.28
Line-3,Machine-1,10-12-2024 11:15,10-12-2024 12:22,Structural Defect,Frame Crack,67.54
Line-5,Machine-1,31-12-2024 15:00,31-12-2024 17:05,Structural Defect,Panel Damage,125.33
Line-4,Machine-2,25-11-2024 13:30,25-11-2024 14:16,Structural Defect,Panel Damage,46.07
Line-1,Machine-3,18-11-2024 01:20,18-11-2024 02:23,Pneumatic Defect,Cylinder Failure,63.74
Line-4,Machine-2,19-02-2025 07:20,19-02-2025 09:36,Structural Defect,Bracket Damage,136.04
Line-4,Machine-2,09-12-2024 01:25,09-12-2024 03:10,Hydraulic Defect,Oil Leakage,105.01
Line-2,Machine-3,10-11-2024 13:10,10-11-2024 13:39,Hydraulic Defect,Filter Clogging,29.44
Line-1,Machine-1,23-01-2025 05:15,23-01-2025 07:08,Pneumatic Defect,Pressure Drop,113.74
Line-5,Machine-2,20-01-2025 08:30,20-01-2025 09:54,Hydraulic Defect,Pump Failure,84.55
Line-3,Machine-1,29-01-2025 04:25,29-01-2025 06:28,Structural Defect,Bracket Damage,123.12
Line-1,Machine-3,28-11-2024 20:30,28-11-2024 22:39,Electrical Defect,Wheel spindle,129.26
Line-4,Machine-3,12-01-2025 20:30,12-01-2025 22:30,Structural Defect,Bracket Damage,120.46
Line-4,Machine-4,06-01-2025 02:20,06-01-2025 03:51,Mechanical Defect,Bolt Loosening,91.1
Line-1,Machine-3,27-12-2024 21:20,27-12-2024 22:25,Hydraulic Defect,Pump Failure,65.02
Line-2,Machine-4,07-11-2024 03:25,07-11-2024 05:39,Pneumatic Defect,Air Leakage,134.61
Line-1,Machine-3,29-11-2024 09:20,29-11-2024 10:23,Pneumatic Defect,Pressure Drop,63.05
Line-3,Machine-3,19-12-2024 16:30,19-12-2024 18:38,Hydraulic Defect,Valve Blockage,128.6
Line-2,Machine-4,15-01-2025 05:00,15-01-2025 05:24,Pneumatic Defect,Solenoid Failure,24.74
Line-1,Machine-1,30-11-2024 02:15,30-11-2024 02:44,Mechanical Defect,Coupling Failure,29.01
Line-2,Machine-3,14-02-2025 18:10,14-02-2025 19:03,Hydraulic Defect,Valve Blockage,53.85
Line-5,Machine-3,12-12-2024 04:10,12-12-2024 04:36,Structural Defect,Weld Failure,26.26
Line-2,Machine-4,26-01-2025 05:20,26-01-2025 07:49,Structural Defect,Bracket Damage,149.28
Line-1,Machine-1,29-12-2024 14:30,29-12-2024 15:34,Structural Defect,Frame Crack,64.53
Line-5,Machine-2,07-12-2024 08:00,07-12-2024 09:24,Pneumatic Defect,Air Leakage,84.52
Line-5,Machine-2,26-01-2025 18:15,26-01-2025 19:07,Structural Defect,Bracket Damage,52.33
Line-5,Machine-3,24-01-2025 13:20,24-01-2025 14:02,Mechanical Defect,Belt Breakage,42.91
Line-3,Machine-3,01-11-2024 02:25,01-11-2024 04:02,Pneumatic Defect,Pressure Drop,97.67
Line-3,Machine-3,07-02-2025 17:30,07-02-2025 18:59,Structural Defect,Frame Crack,89.71
Line-2,Machine-3,24-01-2025 07:20,24-01-2025 09:29,Structural Defect,Bracket Damage,129.36
Line-5,Machine-2,25-02-2025 01:15,25-02-2025 02:14,Hydraulic Defect,Valve Blockage,59.48
Line-4,Machine-5,05-11-2024 16:20,05-11-2024 17:35,Hydraulic Defect,Hose Rupture,75.35
Line-2,Machine-4,19-11-2024 15:20,19-11-2024 16:37,Electrical Defect,Pneumatic,77.68
Line-2,Machine-4,01-01-2025 22:15,01-01-2025 23:36,Hydraulic Defect,Oil Leakage,81.58
Line-1,Machine-3,21-12-2024 20:30,21-12-2024 21:43,Mechanical Defect,Belt Breakage,73.84
Line-4,Machine-3,17-02-2025 02:00,17-02-2025 02:18,Pneumatic Defect,Pressure Drop,18.33
Line-5,Machine-1,05-02-2025 07:15,05-02-2025 08:08,Electrical Defect,Relay Contactor,53.67
Line-3,Machine-3,17-12-2024 13:25,17-12-2024 15:44,Structural Defect,Frame Crack,139.69
Line-2,Machine-4,13-12-2024 02:30,13-12-2024 03:53,Structural Defect,Weld Failure,83.81
Line-5,Machine-2,05-12-2024 14:15,05-12-2024 16:44,Electrical Defect,Work head unit,149.69
Line-2,Machine-1,06-12-2024 04:00,06-12-2024 04:19,Hydraulic Defect,Oil Leakage,19.66
Line-5,Machine-1,12-01-2025 00:20,12-01-2025 02:08,Pneumatic Defect,Solenoid Failure,108.0
Line-1,Machine-2,03-02-2025 05:15,03-02-2025 06:13,Pneumatic Defect,Cylinder Failure,58.83
Line-3,Machine-2,15-12-2024 01:25,15-12-2024 03:48,Pneumatic Defect,Air Leakage,143.72
Line-3,Machine-2,17-11-2024 22:10,18-11-2024 00:11,Mechanical Defect,Bolt Loosening,121.23
Line-4,Machine-2,13-11-2024 14:20,13-11-2024 16:30,Mechanical Defect,Gear Failure,130.88
Line-3,Machine-3,11-02-2025 20:00,11-02-2025 21:26,Hydraulic Defect,Filter Clogging,86.86
Line-5,Machine-1,23-12-2024 18:00,23-12-2024 19:56,Structural Defect,Bracket Damage,116.35
Line-1,Machine-3,08-02-2025 07:30,08-02-2025 07:50,Mechanical Defect,Gear Failure,20.05
Line-2,Machine-2,18-02-2025 19:25,18-02-2025 21:27,Mechanical Defect,Shaft Misalignment,122.55
Line-4,Machine-5,12-11-2024 22:30,13-11-2024 00:43,Hydraulic Defect,Pump Failure,133.48
Line-2,Machine-3,15-01-2025 16:00,15-01-2025 16:10,Hydraulic Defect,Oil Leakage,10.02
Line-2,Machine-1,04-02-2025 21:30,04-02-2025 23:45,Mechanical Defect,Gear Failure,135.4
Line-2,Machine-4,08-01-2025 11:00,08-01-2025 11:21,Electrical Defect,Wheel spindle,21.58
Line-4,Machine-3,15-02-2025 18:00,15-02-2025 20:07,Electrical Defect,Relay Contactor,127.98
Line-4,Machine-4,15-11-2024 18:25,15-11-2024 19:34,Pneumatic Defect,Cylinder Failure,69.13
Line-4,Machine-3,28-12-2024 22:10,28-12-2024 23:39,Structural Defect,Frame Crack,89.05
Line-4,Machine-3,25-12-2024 09:25,25-12-2024 11:14,Electrical Defect,Work head unit,109.83
Line-5,Machine-1,16-02-2025 10:00,16-02-2025 11:44,Electrical Defect,Work head unit,104.66
Line-1,Machine-2,23-01-2025 18:15,23-01-2025 19:55,Electrical Defect,Overload Current,100.18
Line-2,Machine-1,18-12-2024 06:20,18-12-2024 08:31,Structural Defect,Weld Failure,131.21
Line-3,Machine-3,17-01-2025 02:20,17-01-2025 02:30,Mechanical Defect,Bolt Loosening,10.4
Line-1,Machine-1,13-11-2024 03:10,13-11-2024 03:49,Mechanical Defect,Coupling Failure,39.68
Line-1,Machine-2,08-02-2025 12:25,08-02-2025 12:40,Hydraulic Defect,Oil Leakage,15.03
Line-1,Machine-4,03-11-2024 05:20,03-11-2024 05:37,Pneumatic Defect,Cylinder Failure,17.31
Line-4,Machine-1,15-02-2025 02:25,15-02-2025 02:43,Pneumatic Defect,Air Leakage,18.13
Line-2,Machine-1,23-12-2024 09:30,23-12-2024 10:13,Pneumatic Defect,Pressure Drop,43.86
Line-2,Machine-2,14-11-2024 09:15,14-11-2024 10:34,Electrical Defect,Loose connection,79.0
Line-1,Machine-4,29-11-2024 10:00,29-11-2024 12:24,Pneumatic Defect,Solenoid Failure,144.89
Line-4,Machine-2,27-02-2025 15:00,27-02-2025 16:22,Electrical Defect,Loose connection,82.98
Line-2,Machine-4,12-12-2024 14:30,12-12-2024 15:31,Hydraulic Defect,Filter Clogging,61.48
Line-5,Machine-2,03-12-2024 22:10,03-12-2024 22:51,Structural Defect,Frame Crack,41.26
Line-1,Machine-2,19-01-2025 10:25,19-01-2025 12:05,Pneumatic Defect,Solenoid Failure,100.5
Line-4,Machine-3,05-02-2025 22:00,05-02-2025 22:50,Electrical Defect,Work head unit,50.76
Line-5,Machine-2,12-02-2025 02:25,12-02-2025 03:06,Hydraulic Defect,Hose Rupture,41.95
Line-2,Machine-2,18-01-2025 22:20,18-01-2025 22:38,Pneumatic Defect,Air Leakage,18.1
Line-2,Machine-4,05-11-2024 19:10,05-11-2024 20:50,Electrical Defect,Lubrication,100.24
Line-4,Machine-1,14-02-2025 09:15,14-02-2025 10:45,Electrical Defect,Lubrication,90.96
Line-3,Machine-1,12-02-2025 03:20,12-02-2025 04:59,Structural Defect,Panel Damage,99.99
Line-1,Machine-1,27-01-2025 21:20,27-01-2025 22:45,Pneumatic Defect,Cylinder Failure,85.43
Line-1,Machine-2,21-02-2025 17:25,21-02-2025 18:44,Mechanical Defect,Gear Failure,79.62
Line-1,Machine-3,08-12-2024 01:25,08-12-2024 03:47,Electrical Defect,Sensor Setting,142.87
Line-5,Machine-2,13-01-2025 13:25,13-01-2025 14:39,Mechanical Defect,Spring Failure,74.2
Line-3,Machine-2,14-12-2024 12:15,14-12-2024 13:59,Structural Defect,Panel Damage,104.41
Line-1,Machine-4,20-12-2024 10:20,20-12-2024 12:02,Hydraulic Defect,Filter Clogging,102.28
Line-1,Machine-4,18-12-2024 11:15,18-12-2024 12:29,Pneumatic Defect,Pressure Drop,74.25
Line-2,Machine-3,06-11-2024 03:20,06-11-2024 05:20,Mechanical Defect,Gear Failure,120.96
Line-3,Machine-1,15-02-2025 10:25,15-02-2025 12:48,Mechanical Defect,Belt Breakage,143.41
Line-2,Machine-3,08-11-2024 03:30,08-11-2024 05:09,Structural Defect,Weld Failure,99.69
Line-1,Machine-3,22-02-2025 21:25,22-02-2025 22:44,Pneumatic Defect,Solenoid Failure,79.85
Line-1,Machine-1,09-02-2025 09:15,09-02-2025 09:31,Mechanical Defect,Shaft Misalignment,16.45
Line-2,Machine-4,11-01-2025 15:15,11-01-2025 16:00,Mechanical Defect,Seal Leakage,45.53
Line-3,Machine-1,16-02-2025 12:25,16-02-2025 12:51,Structural Defect,Bracket Damage,26.59
Line-1,Machine-2,23-02-2025 00:00,23-02-2025 01:56,Hydraulic Defect,Pump Failure,116.54
Line-1,Machine-3,25-02-2025 02:15,25-02-2025 04:38,Pneumatic Defect,Solenoid Failure,143.13
Line-3,Machine-2,15-12-2024 19:25,15-12-2024 20:53,Electrical Defect,Sensor Setting,88.97
Line-3,Machine-2,22-02-2025 00:10,22-02-2025 02:22,Pneumatic Defect,Air Leakage,132.83
Line-4,Machine-4,14-01-2025 08:00,14-01-2025 08:42,Mechanical Defect,Bearing Failure,42.02
Line-1,Machine-1,17-02-2025 08:25,17-02-2025 09:35,Mechanical Defect,Bolt Loosening,70.39
Line-3,Machine-3,15-01-2025 18:15,15-01-2025 18:45,Structural Defect,Bracket Damage,30.13
Line-2,Machine-4,17-01-2025 03:10,17-01-2025 05:24,Structural Defect,Frame Crack,134.44
Line-2,Machine-4,08-11-2024 08:15,08-11-2024 09:48,Structural Defect,Frame Crack,93.13
Line-4,Machine-1,15-11-2024 02:25,15-11-2024 03:39,Hydraulic Defect,Hose Rupture,74.4
"""

st.download_button(
    label="📥 Download Sample CSV (500 rows)",
    data=SAMPLE_CSV.encode(),
    file_name="sample_data.csv",
    mime="text/csv"
)

uploaded_file = st.file_uploader("Upload your file in CSV Format only", type=["csv"])
st.caption("📋 Your dataset must have these columns: **Line-ID**, **Machine-ID**, **Start-Time**, **End-Time**, **Category Defect**, **Sub-Category Defect**, **Down-Time**")

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df['Start-Time'] = pd.to_datetime(df['Start-Time'], dayfirst=True)
    df['End-Time'] = pd.to_datetime(df['End-Time'], dayfirst=True)

    st.sidebar.subheader("⏱️ Time Range Filter")

    min_time = df['Start-Time'].min()
    max_time = df['End-Time'].max()

    start_date = st.sidebar.date_input("Start Date", min_time.date())
    end_date = st.sidebar.date_input("End Date", max_time.date())

    selected_start = pd.to_datetime(f"{start_date} ")
    selected_end = pd.to_datetime(f"{end_date} ")

    if selected_end < selected_start:
        st.error("❌ End Time cannot be earlier than Start Time. Please correct the selection.")
        st.stop()

    df = df[(df['Start-Time'] >= selected_start) & (df['End-Time'] <= selected_end)]

    with st.sidebar:
        st.markdown("---")
        st.subheader("🔧 Filter Options")
        min_loss_time_input = st.number_input("Minimum LossTime (in minutes)", min_value=0, value=0, key="min_loss_input")
        if st.button("Apply LossTime Filter"):
            st.session_state["min_loss_applied"] = min_loss_time_input

    min_loss_time = st.session_state.get("min_loss_applied", 0)
    df = df[df['Down-Time'] >= min_loss_time]

    total_available_time_minutes = 24 * 60

    # --- LINE-LEVEL SUMMARY ---
    st.header("Pareto Chart by Line")
    line_summary = df.groupby('Line-ID').agg(
        Mean_LossTime=('Down-Time', 'mean'),
        Total_Frequency=('Down-Time', 'count'),
        Total_LossTime=('Down-Time', 'sum')
    ).reset_index()

    line_summary = line_summary.sort_values(by='Mean_LossTime', ascending=False)
    line_summary['Cumulative MTTR'] = line_summary['Mean_LossTime'].cumsum()
    line_summary['Cumulative Percentage'] = 100 * line_summary['Cumulative MTTR'] / line_summary['Mean_LossTime'].sum()

    fig_line = make_subplots(specs=[[{"secondary_y": True}]])
    fig_line.add_trace(go.Bar(
        x=line_summary['Line-ID'],
        y=line_summary['Mean_LossTime'],
        name='MTTR (Mean LossTime)',
        marker_color='blue',
        hovertext=[
            f"<b>Line: {line}<br>MTTR: {mttr:.2f} min<br>Total Frequency: {freq}</b>"
            for line, mttr, freq in zip(line_summary['Line-ID'], line_summary['Mean_LossTime'], line_summary['Total_Frequency'])
        ]
    ), secondary_y=False)

    fig_line.add_trace(go.Scatter(
        x=line_summary['Line-ID'],
        y=line_summary['Cumulative Percentage'],
        name="Cumulative %",
        mode="lines+markers",
        line=dict(color="red")
    ), secondary_y=True)

    fig_line.update_layout(title_text=f"Pareto Chart of Line by MTTR (Down-Time ≥ {min_loss_time} min)")
    make_plot_text_bold(fig_line)
    fig_line.update_yaxes(title_text="MTTR (min)", secondary_y=False)
    fig_line.update_yaxes(title_text="Cumulative %", secondary_y=True)

    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown(download_plot_as_html(fig_line, "Pareto_Line.html"), unsafe_allow_html=True)
    with st.expander("Show Summary Table"):
        st.dataframe(line_summary)

    # --- MACHINE-LEVEL MTTR ---
    st.header("Select Line for Machine-wise MTTR")
    selected_line = st.selectbox("Choose a Line", line_summary['Line-ID'])
    machine_df = df[df['Line-ID'] == selected_line]

    machine_summary = machine_df.groupby('Machine-ID').agg(
        Mean_LossTime=('Down-Time', 'mean'),
        Total_Frequency=('Down-Time', 'count')
    ).reset_index()

    machine_summary = machine_summary.sort_values(by='Mean_LossTime', ascending=False)
    machine_summary['Cumulative MTTR'] = machine_summary['Mean_LossTime'].cumsum()
    machine_summary['Cumulative Percentage'] = 100 * machine_summary['Cumulative MTTR'] / machine_summary['Mean_LossTime'].sum()

    fig_machine = make_subplots(specs=[[{"secondary_y": True}]])
    fig_machine.add_trace(go.Bar(
        x=machine_summary['Machine-ID'],
        y=machine_summary['Mean_LossTime'],
        name='MTTR (Mean LossTime)',
        marker_color='blue',
        hovertext=[
            f"<b>Machine: {machine}<br>MTTR: {mttr:.2f} min<br>Total Frequency: {freq}</b>"
            for machine, mttr, freq in zip(machine_summary['Machine-ID'], machine_summary['Mean_LossTime'], machine_summary['Total_Frequency'])
        ]
    ), secondary_y=False)

    fig_machine.add_trace(go.Scatter(
        x=machine_summary['Machine-ID'],
        y=machine_summary['Cumulative Percentage'],
        name="Cumulative %",
        mode="lines+markers",
        line=dict(color="red")
    ), secondary_y=True)

    fig_machine.update_layout(title_text=f"Pareto Chart of MTTR by Machine in {selected_line} Line: (Down-Time ≥ {min_loss_time} min)")
    make_plot_text_bold(fig_machine)
    fig_machine.update_yaxes(title_text="MTTR (min)", secondary_y=False)
    fig_machine.update_yaxes(title_text="Cumulative %", secondary_y=True)

    st.plotly_chart(fig_machine, use_container_width=True)
    st.markdown(download_plot_as_html(fig_machine, f"Pareto_{selected_line}_Machines_MTTR.html"), unsafe_allow_html=True)
    with st.expander("Show Summary Table"):
        st.dataframe(machine_summary)

    # --- LOSS-LEVEL MTTR ---
    st.header("Select Machine for Loss-wise MTTR")
    selected_machine = st.selectbox("Choose a Machine", machine_summary['Machine-ID'])
    loss_df = df[df['Machine-ID'] == selected_machine]

    loss_summary = loss_df.groupby(['Category Defect', 'Sub-Category Defect']).agg(
        Mean_LossTime=('Down-Time', 'mean'),
        Total_Frequency=('Down-Time', 'count')
    ).reset_index()

    loss_summary['Loss_Label'] = loss_summary['Category Defect'] + ' - ' + loss_summary['Sub-Category Defect']
    loss_summary = loss_summary.sort_values(by='Mean_LossTime', ascending=False)
    loss_summary['Cumulative MTTR'] = loss_summary['Mean_LossTime'].cumsum()
    loss_summary['Cumulative Percentage'] = 100 * loss_summary['Cumulative MTTR'] / loss_summary['Mean_LossTime'].sum()

    fig_loss = make_subplots(specs=[[{"secondary_y": True}]])
    fig_loss.add_trace(go.Bar(
        x=loss_summary['Loss_Label'],
        y=loss_summary['Mean_LossTime'],
        name='MTTR (Mean LossTime)',
        marker_color='blue',
        hovertext=[
            f"<b>Loss: {label}<br>MTTR: {mttr:.2f} min<br>Total Frequency: {freq}</b>"
            for label, mttr, freq in zip(loss_summary['Loss_Label'], loss_summary['Mean_LossTime'], loss_summary['Total_Frequency'])
        ]
    ), secondary_y=False)

    fig_loss.add_trace(go.Scatter(
        x=loss_summary['Loss_Label'],
        y=loss_summary['Cumulative Percentage'],
        name="Cumulative %",
        mode="lines+markers",
        line=dict(color="red")
    ), secondary_y=True)

    fig_loss.update_layout(title_text=f"Pareto Chart of MTTR by Loss in {selected_machine} Machine: (Down-Time ≥ {min_loss_time} min)")
    make_plot_text_bold(fig_loss)
    fig_loss.update_yaxes(title_text="MTTR (min)", secondary_y=False)
    fig_loss.update_yaxes(title_text="Cumulative %", secondary_y=True)

    st.plotly_chart(fig_loss, use_container_width=True)
    st.markdown(download_plot_as_html(fig_loss, f"Pareto_{selected_machine}_Losses_MTTR.html"), unsafe_allow_html=True)
    with st.expander("Show Summary Table"):
        st.dataframe(loss_summary)

    # --- COMMON DEFECTS SECTION ---
    st.header("🔍 Common Defects by Line")
    df['Frequency'] = 1
    selected_line = st.selectbox("Choose Line for Defect Analysis:", options=sorted(df['Line-ID'].unique()))

    if selected_line:
        st.subheader(f"Top 5 Defects in Line: {selected_line}")
        filtered_df = df[df['Line-ID'] == selected_line]

        defect_summary = filtered_df.groupby(['Line-ID', 'Machine-ID', 'Category Defect', 'Sub-Category Defect']).agg(
            Frequency=('Down-Time', 'count'),
            TotalLossTime=('Down-Time', 'sum')
        ).reset_index()

        defect_summary['MTTR'] = defect_summary['TotalLossTime'] / defect_summary['Frequency']
        defect_summary['Defect'] = defect_summary['Category Defect'] + ' - ' + defect_summary['Sub-Category Defect']

        grouped_defects = defect_summary.groupby(['Line-ID', 'Defect']).agg(
            Frequency=('Frequency', 'sum'),
            TotalLossTime=('TotalLossTime', 'sum'),
            Machines=('Machine-ID', lambda x: ', '.join(sorted(set(x)))),
            MaxMTTR=('MTTR', 'max')
        ).reset_index()

        grouped_defects.rename(columns={'MaxMTTR': 'MTTR'}, inplace=True)
        grouped_defects['MTTR'] = grouped_defects['MTTR'].round(2)
        top_defects = grouped_defects.sort_values(by='Frequency', ascending=False).head(5)

        st.dataframe(top_defects[['Defect', 'Machines', 'Frequency', 'MTTR']])

    # --- COMMON DEFECTS ACROSS LINES/MACHINES ---
    st.markdown("### 🏁 Common Defects Across Selected Lines & Machines")

    df_summary = df.copy()
    df_summary['Frequency'] = 1
    df_summary['TotalLossTime'] = df_summary['Down-Time']
    df_summary['Defect'] = df_summary['Category Defect'] + " - " + df_summary['Sub-Category Defect']

    grouped_defects = df_summary.groupby(['Defect', 'Line-ID', 'Machine-ID']).agg(
        Frequency=('Frequency', 'sum'),
        TotalLossTime=('TotalLossTime', 'sum')
    ).reset_index()

    grouped_defects['MTTR_machine'] = grouped_defects['TotalLossTime'] / grouped_defects['Frequency']

    machine_counts = grouped_defects.groupby('Defect')['Machine-ID'].nunique().reset_index(name='Machine_Count')
    machine_lists = grouped_defects.groupby('Defect')['Machine-ID'].apply(lambda x: sorted(set(x))).reset_index(name='Machine_List')
    line_counts = grouped_defects.groupby('Defect')['Line-ID'].nunique().reset_index(name='Line_Count')
    line_lists = grouped_defects.groupby('Defect')['Line-ID'].apply(lambda x: sorted(set(x))).reset_index(name='Line_List')

    overall_common = grouped_defects.groupby('Defect').agg(
        Lines=('Line-ID', lambda x: ', '.join(sorted(set(x)))),
        Machines=('Machine-ID', lambda x: ', '.join(sorted(set(x)))),
        Total_Frequency=('Frequency', 'sum'),
        Total_LossTime=('TotalLossTime', 'sum'),
        MTTR=('MTTR_machine', 'max')
    ).reset_index()

    overall_common = overall_common.merge(machine_counts, on='Defect')
    overall_common = overall_common.merge(machine_lists, on='Defect')
    overall_common = overall_common.merge(line_counts, on='Defect')
    overall_common = overall_common.merge(line_lists, on='Defect')

    if not overall_common.empty:
        overall_common['MTTR'] = overall_common['MTTR'].round(2)

    overall_common.drop(columns=['Machine_Count', 'Machine_List', 'Line_Count', 'Line_List'], inplace=True)
    overall_common = overall_common.sort_values(by='MTTR', ascending=False)

    st.dataframe(overall_common[['Defect', 'Lines', 'Machines', 'Total_Frequency', 'MTTR']])

else:
    st.info("Please upload a file in CSV format to get started.")
