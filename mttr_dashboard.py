import base64
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

uploaded_file = st.file_uploader("Upload your file in CSV Format only", type=["csv"])
st.caption("📋 Your dataset must have these columns: **Line-ID**, **Machine-ID**, **Start-Time**, **End-Time**, **Category Defect**, **Sub-Category Defect**, **Down-Time**")

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Convert StartTime and EndTime to datetime
    df['Start-Time'] = pd.to_datetime(df['Start-Time'], dayfirst=True)
    df['End-Time'] = pd.to_datetime(df['End-Time'], dayfirst=True)

    st.sidebar.subheader("⏱️ Time Range Filter")

    # Get min/max time range from the dataset
    min_time = df['Start-Time'].min()
    max_time = df['End-Time'].max()

    # Sidebar date and time inputs
    start_date = st.sidebar.date_input("Start Date", min_time.date())
    end_date = st.sidebar.date_input("End Date", max_time.date())

    # Combine selected date and time to datetime
    selected_start = pd.to_datetime(f"{start_date} ")
    selected_end = pd.to_datetime(f"{end_date} ")

    if selected_end < selected_start:
        st.error("❌ End Time cannot be earlier than Start Time. Please correct the selection.")
        st.stop()

    # Filter the dataframe based on selected range
    df = df[(df['Start-Time'] >= selected_start) & (df['End-Time'] <= selected_end)]

    # Sidebar filter for LossTime
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔧 Filter Options")

        # Temporary input value
        min_loss_time_input = st.number_input("Minimum LossTime (in minutes)", min_value=0, value=0, key="min_loss_input")
        
        # Button to apply filter
        if st.button("Apply LossTime Filter"):
            st.session_state["min_loss_applied"] = min_loss_time_input

    # Get the applied value (default to 0)
    min_loss_time = st.session_state.get("min_loss_applied", 0)

    # Now filter the data only based on the applied value
    df = df[df['Down-Time'] >= min_loss_time]

    total_available_time_minutes = 24 * 60  # Can be customized

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
