import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import pandas as pd  # pip install pandas openpyxl
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date
import matplotlib.pyplot as plt

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Sensor Data Analysis", page_icon=":wrench:", layout="wide")

# ---- MAINPAGE ----
st.title(":bar_chart: 🏭 Sensor Data Analysis")
st.markdown("##")
st.markdown("""
This app performs simple sensor anomaly detection!
* **Python libraries:** plotly, pandas, streamlit
""")

# ---- READ EXCEL ----
# @st.cache(allow_output_mutation=True)
def get_data_from_csv():
    df = pd.read_csv(
        "MaintenanceReport.csv",  # Path to the CSV file
        sep=",",
        nrows=1000  # Limit to 1000 rows
    )
    return df

df = get_data_from_csv()

st.write('Maintenances Report Data Dimension: ' + str(df.shape[0]) + ' rows and ' + str(df.shape[1]) + ' columns.')
# Sample data structure with additional variables

st.subheader("Maintenance Details")
maintenance_counts= df['Prob. code text'].value_counts().size

# Maintenances  types in dataset
maintenance_counts= df['Prob. code text'].value_counts()

fig_maintenance_stat = px.bar(y=maintenance_counts.values,
             x=maintenance_counts.index,
             color = maintenance_counts.index,
             color_discrete_sequence=px.colors.sequential.OrRd,
             text=maintenance_counts.values,
             title="<b>Maintenances Types in the Sample</b>")

fig_maintenance_stat.update_layout(
    xaxis_title="Maintenances Types",
    yaxis_title="Count",
    font = dict(size=14,family="Franklin Gothic"))

fig_maintenance_stat.update_layout(legend=dict(
    title="Maintenances Types"
))
st.plotly_chart(fig_maintenance_stat)

st.markdown("""We can notice that **Planned** services are top frequent types of maintenance in the sample.""")

# Focusing on not planned services
df_not_planned=df[df['Prob. code text']!='Planned']
df_not_planned_not_serv = df_not_planned[~df_not_planned['Description'].isin(['DAILY SERVICE', 'Daily service', 'Daily Service', 'Daily Servive'])]

st.subheader("Maintenance Details - Not Planned")

# Grouping and aggregating the data
agg_data = df_not_planned_not_serv.groupby('Description')['Breakdown dur.'].sum().reset_index()
agg_data = agg_data.sort_values(by='Breakdown dur.', ascending=True)

# Getting the top 10 entries (you mentioned "top 5" but used tail(10) in your code)
top_10 = agg_data.tail(10)

# Create a color sequence
color_sequence = px.colors.sequential.OrRd

# Creating the Plotly figure
fig = go.Figure([go.Bar(x=top_10['Breakdown dur.'], y=top_10['Description'], orientation='h',
                        marker_color=color_sequence)])
fig.update_layout(title='Top 10 failures by repair time',
                  xaxis_title='Breakdown duration in hours',
                  yaxis_title='Description')

# Streamlit app
st.plotly_chart(fig)  # Display the Plotly figure in Streamlit

# Filtering only the bigest breakdown - not planned
df_bigest_breakdown=df_not_planned_not_serv[df_not_planned_not_serv['Breakdown dur.']>=10]

#Dataset Dataframe
st.dataframe(df_bigest_breakdown)

st.markdown("""
Main Key points:
* **Focus Periods:** We will concentrate on September and October due to the emergence of breakdowns during these months.
""")

# Sensor Data
st.subheader("Essential Characteristics for Sensor Data")
sensor_data_description = {
    "Ambient Temperature": "Ambient temperature in degrees C",
    "Distance Travelled": "Total distance travelled over equipment life in kilometers",
    "Engine Coolant Temperature": "Engine Coolant temperature in degrees C",
    "Engine Fuel Rate": "Engine fuel consumption rate in liters/hour",
    "Engine Intake Manifold Pressure": "Engine intake manifold pressure after turbo in bar",
    "Engine Intake Manifold Temperature": "Engine intake manifold temperature after turbo in degrees Celsius",
    "Engine Oil Pressure": "Engine Oil pressure in bar",
    "Engine Oil Temperature": "Engine Oil temperature in degrees C",
    "Engine RPM": "Engine RPM",
    "Idle": "Indicator, 1 if machine is idling (Engine is running and parking brake is engaged)",
    "Machine Running Hours": "Total hours engine has been running over life of the equipment",
    "Machine Speed": "Machine speed in kilometres/hour",
    "Operational": "Indicator, 1 if machine is operational (Engine is running and parking brake is disengaged)",
    "Transmission Hours": "Total hours transmission has been running over life of the transmission.",
    "Transmission Oil Pressure": "Transmission oil pressure in bar",
    "Transmission Oil Temperature": "Transmission oil temperature in degrees C."
}


# Create a DataFrame
df_sensor_desc = pd.DataFrame(sensor_data_description.items(), columns=["Variable", "Description"])

# Create an expander for variable descriptions
with st.expander("View Variable Descriptions"):
    st.table(df_sensor_desc)

st.markdown("""
Anomaly Detection Analysis Plan:
* **Objective:** Detect anomalies indicating irregularities in machinery.
* **Detection Methods:** Utilize box plots to identify outliers in the data.
                        Employ a correlation matrix to assess relationships between variables.
* **Key Focus:** Analyze variables related to temperature and pressure due to the prevalence of outliers.
* **Correlation Analysis:** Investigate if a positive correlation exists between 
                            variables, checking for simultaneous increases.
""")

def get_sensor_data_from_csv():
    df_sensor = pd.read_csv(
        "sensor_data_pivoted.csv",  # Path to the CSV file
        sep=",",
        parse_dates=['TimeStamp']
    )
    return df_sensor

df_pivot= get_sensor_data_from_csv()

#Histograms
st.subheader("Analysis of Variable Distribution")

# Checkbox to toggle the chart visibility
show_chart_hist = st.checkbox("Show histograms")

continuous_vars =  df_pivot.drop(['TimeStamp','date','time'], axis=1).columns


if show_chart_hist:
    fig, axes = plt.subplots(4, 4)

    for i, el in enumerate(continuous_vars):
        ax = axes.flatten()[i]
        df_pivot[el].plot(kind='hist', bins=30, ax=ax,  color='#fdd39b')
        ax.set_title(el)

    fig.set_size_inches(15, 15)
    plt.tight_layout()
    st.pyplot(fig)

#Box plots

# Checkbox to toggle the chart visibility
show_chart_box = st.checkbox("Show Box plots")

if show_chart_box:
    fig, axes = plt.subplots(4,4) # create figure and axes

    for i, el in enumerate(list(df_pivot[continuous_vars].columns.values)):
        a = df_pivot.boxplot(el, ax=axes.flatten()[i], fontsize='large', color='#d55233')

    fig.set_size_inches(15, 15)
    plt.tight_layout()
    st.pyplot(fig)

#Relationship
st.subheader("Relationship")

# Keep only numeric columns
df_numeric = df_pivot.select_dtypes(include=['number'])

# Calculate the correlation matrix
corr_matrix = df_numeric.corr()

# Create a Plotly heatmap for the correlation matrix
fig = px.imshow(corr_matrix,
                labels=dict(x="Variables", y="Variables", color="Correlation"),
                x=corr_matrix.columns,  # List of all your 40 variable names in columns
                y=corr_matrix.columns,  # List of all your 40 variable names in rows
                color_continuous_scale='RdBu_r',
                zmin=-1, zmax=1)

# Customize layout to fit large number of variables
fig.update_layout(
    title='Correlation Matrix Heatmap',
    xaxis_tickangle=-45,  # Tilt x-axis labels for better readability
    height=1000,  # Increase the figure height to accommodate all variables
    width=1000,  # Increase the width if necessary
)

# Display the heatmap in Streamlit
st.plotly_chart(fig)

st.markdown("""
Main Key points:
* Analysis of the correlation plot reveals that temperature-related variables are positively correlated.
* Strong positive correlations are also observed between:
    * Engine Fuel Rate and Engine Intake Manifold Pressure
    * Engine Oil Pressure and both Engine RPM and Machine Speed
* We will focus on identifying outliers within these relationships.
* Additionally, we will examine how these variables change over time.
""")

# Set the title of the app
st.subheader("Date Range Selector")

# Set default start and end dates
default_start_date = date(2016, 9, 12)
default_end_date = date(2016, 9, 14)

# Create date input fields for start and end dates
start_date = st.date_input("Start Date", default_start_date)
end_date = st.date_input("End Date", default_end_date)

# Convert
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Ensure the end date is after the start date
if end_date < start_date:
    st.error("End date must be after start date.")
else:
    st.success(f"You selected a date range from {start_date} to {end_date}.")

    df_pivot['date'] = df_pivot['TimeStamp'].dt.date
    df_pivot['time'] = df_pivot['TimeStamp'].dt.time
    df_pivot['date'] = pd.to_datetime(df_pivot['date'], errors='coerce')
    filtered_df = df_pivot[(df_pivot['date'] >= start_date) & (df_pivot['date'] <= end_date)]

    st.write('Sensor Data Dimension: ' + str(filtered_df.shape[0]) + ' rows and ' + str(filtered_df.shape[1]) + ' columns.')

# Streamlit app
st.subheader("Sensor Data Analysis")

# Filter the DataFrame
#filtered_df['TimeStamp'] = pd.to_datetime(filtered_df['TimeStamp'], infer_datetime_format=True, errors='coerce')
#filtered_df_op = filtered_df[(filtered_df['TimeStamp'] >= start_date) & (filtered_df['TimeStamp'] <= end_date)]


st.markdown("""
Main Key points:
* **Objective:** Exclude outliers related to machine downtime.
* **Focus:** Analyze data where the machine is actively operating.
* **Goal:** This will allow us to concentrate our analysis on meaningful patterns during active operation.
""")

filtered_df_op=filtered_df[filtered_df['Operational']==1.0]
filtered_df_op=filtered_df_op[filtered_df_op['Idle']!=1.0]

# Create two columns
col1, col2 = st.columns(2)

# Create scatter plot
if not filtered_df_op.empty:  # Check if the DataFrame is not empty
    with col1:
        fig = px.scatter(
            filtered_df_op,
            x='TimeStamp',
            y='Engine_Oil_Temperature',
            color='Engine_Oil_Pressure',
            title='Scatter Plot - Engine Oil Temperature',
            labels={
                'TimeStamp': "Date & Time",  # Correct the key to the x-axis label
                'Engine_Oil_Temperature': "Engine Oil Temperature",
                'Engine_Oil_Pressure': "Engine Oil Pressure"
            }
        )

        fig.update_layout(
            title='Scatter Plot - Engine Oil Temperature',
            xaxis_tickangle=-45,
            height=600,
            width=700,
        )

        # Display the scatter plot in the first column
        st.plotly_chart(fig)
    with col2:
        st.subheader("Trends and Anomalies in Engine Oil Temperature and Pressure")
        st.markdown(""" 
            Main Key points:
            * The graph shows clear, regular patterns of increase and decrease in engine oil temperature and pressure, indicating normal operation.
            * Irregular shapes in the sensor data suggest potential anomalies.
            * These discrepancies require further investigation to rule out underlying issues affecting engine performance.
            """)
else:
    with col1:
        st.warning("No data available for the selected date range.")

# Create two columns in Streamlit
col1, col2 = st.columns(2)

# Create a scatter plot for Engine Oil Pressure vs Machine Speed
with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(filtered_df_op['Engine_Oil_Pressure'], filtered_df_op['Machine_Speed'],
                         c=filtered_df_op.index, cmap='magma')
    ax.set_title('Engine Oil Pressure vs Machine Speed')
    ax.set_xlabel('Engine Oil Pressure')
    ax.set_ylabel('Machine Speed')

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Index')

    # Display the plot in Streamlit
    st.pyplot(fig)

with col2:
    if start_date.month == 9:  # September
        st.subheader("September Review")
        st.markdown(""" 
        Main Key points:
        * **Cluster at zero machine speed:** This may indicate sensor malfunctions during the leak, as the machine wasn't idle.
        * **Scattered points at low speeds and pressures:** Could reflect inconsistencies or erratic readings during the leak.
        * **Outliers at higher pressures:** These may represent pressure fluctuations due to the leakage.
        """)
    elif start_date.month == 10:  # October
        st.subheader("October Review")
        st.markdown("""
        Main Key points:
        * **Fluctuating Oil Pressure:** Exclude outliers related to machine downtime.
        * **Erratic Pressure Readings:** Unstable oil pressure could point to a failing brake cooler pump, risking overheating and further mechanical failure.
        * **High-Speed Outliers:** Outliers at high speeds indicate stress on the system due to insufficient cooling highlighting the need for proper maintenance.
        """)

# Create two columns in Streamlit
col1, col2 = st.columns(2)

# Create a scatter plot for Engine RPM vs Engine Oil Pressure
with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(filtered_df_op['Engine_RPM'], filtered_df_op['Engine_Oil_Pressure'],
                         c=filtered_df_op.index, cmap='magma')
    ax.set_title('Engine Oil Pressure vs Engine RPM')
    ax.set_xlabel('Engine RPM')
    ax.set_ylabel('Engine Oil Pressure')

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Index')

    # Display the plot in Streamlit
    st.pyplot(fig)

with col2:
    # Check if the selected month is September or October
    if start_date.month == 9:
        # Comments for September
        st.subheader("September Review")
        st.markdown("""
        Main Key points:
        * **Low RPM with low pressure:** Indicates potential pressure drops caused by the leak.
        * **Moderate RPM with high pressure:** Suggests system overcompensation to maintain pressure during the leak.
        * **Variability in pressure:** Likely due to pressure instability caused by the leak.
        """)
    elif start_date.month == 10:
        # Comments for October
        st.subheader("October Review")
        st.markdown("""
        Main Key points:
        * **Inconsistent Pressure Readings:** Inconsistent oil pressure can signal problems with the brake cooler pump, which may lead to overheating and compromised braking performance.
        * **Pressure Spikes:** Sudden spikes in oil pressure at varying RPMs may reflect abnormal load conditions, stressing both the transmission and cooling systems.
        """)

# Create two columns in Streamlit
col1, col2 = st.columns(2)

# Create a scatter plot for Transmission Oil Pressure vs Engine Oil Pressure
with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(filtered_df_op['Transmission_Oil_Pressure'], filtered_df_op['Engine_Oil_Pressure'],
                         c=filtered_df_op.index, cmap='magma')
    ax.set_title('Engine Oil Pressure vs Transmission Oil Pressure')
    ax.set_xlabel('Transmission Oil Pressure')
    ax.set_ylabel('Engine Oil Pressure')

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Index')

    # Display the plot in Streamlit
    st.pyplot(fig)

with col2:
    if start_date.month == 9:  # September
        st.subheader("September Review")
        st.markdown(""" 
        Main Key points:
        * Overall, the leak led to pressure instability, especially at lower values, with some system adjustments seen in transmission pressure.
        """)
    elif start_date.month == 10:  # October
        st.subheader("October Review")
        st.markdown("""
        Main Key points:
        * **High Engine Pressure with Low Transmission Pressure:** This combination may suggest a blockage or failure in the transmission system.
        """)

# Create two columns in Streamlit
col1, col2 = st.columns(2)

# Create a scatter plot for Engine Fuel Rate vs Engine Intake Manifold Pressure
with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(filtered_df_op['Engine_Intake_Manifold_Pressure'], filtered_df_op['Engine_Fuel_Rate'],
                         c=filtered_df_op.index, cmap='magma')
    ax.set_title('Engine Fuel Rate vs Engine Intake Manifold Pressure')
    ax.set_xlabel('Engine Intake Manifold Pressure')
    ax.set_ylabel('Engine Fuel Rate')

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Index')

    # Display the plot in Streamlit
    st.pyplot(fig)

with col2:
    if start_date.month == 9:  # September
        st.subheader("September Review")
        st.markdown(""" 
        Main Key points:
        * **Inconsistent Manifold Pressure:** Fluctuations or irregular patterns in intake manifold pressure may indicate unstable engine operation, likely due to the oil leak affecting combustion efficiency.
        """)
    elif start_date.month == 10:  # October
        st.subheader("October Review")
        st.markdown("""
        Main Key points:
        * **High Manifold Pressure with Low Fuel Rate:** High intake manifold pressure alongside low fuel rates suggests air intake restrictions or inadequate fuel supply, potentially linked to transmission problems.
        """)