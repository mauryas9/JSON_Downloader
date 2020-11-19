import numpy as np
import pandas as pd
import streamlit as st
import requests
import json
import time
from tabulate import tabulate
from datetime import datetime

st.title('Real Time Monitoring of Air Pollution')
st.markdown(
    """
<style>
.sidebar .sidebar-content {
    background-image: linear-gradient(#e04938,#e86354);
    color: white;
}
</style>
""",
    unsafe_allow_html=True,
)
st.sidebar.header("Coded by Maurya S.")
st.sidebar.write("Datasource: www.data.gov.in, refreshed hourly with one hour delay")
flag=0
my_bar=st.sidebar.progress(0)
status=st.sidebar.empty()
status.write("Initializing...")
@st.cache(ttl=3600)
def JSON_Downloader(flag):
	offset=10
	limit=10
	#Get Total Number of records and First set of records
	status.write("Getting Total Number of records and First set of records")
	JSONContent = requests.get("https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69?api-key=579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b&format=json&offset=0&limit=10").json()
	total=JSONContent['total']
	my_bar.progress(offset/total)
	status.write("Downloading "+str(offset)+ " of " + str(total) + " records")
	#Build JSON file by Downloading Total no. of records.
	while offset<total:
		JSONContent1 = requests.get("https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69?api-key=579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b&format=json&offset=" + str(offset) +"&limit=" + str(limit)).json()
		if 'error' not in JSONContent1:
			my_bar.progress(offset/total)
			status.write("Downloading "+str(offset)+ " of " + str(total) + " records")
			offset = offset + limit
			JSONContent['records']=[*JSONContent['records'] , *JSONContent1['records']]
	my_bar.progress(1.0)
	status.write("Downloaded "+str(total)+ " of " + str(total) + " records and built the DataFrame")
	pol_recs=pd.DataFrame.from_records(JSONContent['records'],index='id')
	json_updated=JSONContent['updated_date']
	last_update=pd.to_datetime(pol_recs.last_update.unique())[0]
	stations=len(pol_recs.station.unique())
	list1= [pol_recs, total, last_update, stations, json_updated]
	return list1


list2=JSON_Downloader(flag)
my_bar.progress(1.0)
noofstations=list2[3]
last_update=list2[2]
status.write("Downloaded records for all " + str(noofstations) + "\n stations and built the DataFrame at "+ last_update.strftime("%m/%d/%Y, %H:%M"))
recs=list2[0]



State = st.sidebar.selectbox(
    'Select State',
     recs.state.unique())
Station = st.sidebar.selectbox(
    'Select Station',
     recs[(recs['state']==State)].station.unique())
filt_recs=recs[(recs['state']==State)&(recs['station']==Station)]
st.write("Showing data for " + str(Station)+ ", " + str(State) +  " updated at "+ last_update.strftime("%m/%d/%Y, %H:%M") )
st.table(filt_recs[['pollutant_id','pollutant_min','pollutant_avg','pollutant_max']])
#st.write(tabulate(filt_recs[['pollutant_id','pollutant_min','pollutant_avg','pollutant_max']],headers=["Pollutant","Lowest\nValue","Average\nValue","Highest\nValue"],showindex=False))