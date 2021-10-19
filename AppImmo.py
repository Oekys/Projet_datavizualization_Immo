import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.io.formats.format import format_percentiles
import streamlit as st
import time



def count_rows(rows):
    return len(rows)

def get_dom(dt):
    return dt.day

#log
def log(func):
    def wrapper(*args,**kwargs):
        with open("logProjet.txt","a") as f:
            debut = time.time()
            value = func(*args,**kwargs)
            fin = time.time()
            f.write("Called function "+ func.__name__+" loaded in "+str(fin - debut)+"\n")
            return value
    return wrapper

#Loading data
@log
@st.cache(allow_output_mutation=True)
def loadingdata(file_path):
    df = pd.read_csv(file_path)
    return df


#Transforming data
@log
@st.cache(allow_output_mutation=True)
def prepare_date(df):
    df["date_mutation"] = pd.to_datetime(df["date_mutation"])
    #df.drop(['adresse_code_voie',"code_commune","code_departement","ancien_code_commune","ancien_nom_commune","ancien_id_parcelle","numero_volume","lot1_numero","lot2_numero","lot3_numero","lot4_numero","lot5_numero"], inplace=True)
    df["day"]=df["date_mutation"].map(get_dom)
    df['months'] = df['date_mutation'].dt.month
    df["nature_mutation"] = df["nature_mutation"].fillna("Inconnue")        #Fill missing values
    df['type_local'] = df['type_local'].fillna("Inconnue")      #Fill missing values

@log
@st.cache(allow_output_mutation=True) 
def prepare_map(df):
    map_data = df[["latitude","longitude","months"]].sample(frac=0.0033)
    map_data.dropna(subset = ["latitude"], inplace=True) #Droping missing values
    map_data.dropna(subset = ["longitude"], inplace=True)
    return map_data

@log
@st.cache(allow_output_mutation=True)
def prepare_codepostal(df):
    df['new_code_postal'] = df['code_postal'].astype(str)                       #Transforming into str            
    df["new_code_postal"]=df["new_code_postal"].str.extract(r'(\d{1,2})')       #Grouping departments using the 2 first digits  

    

#Streamlit
@log
def print_raw_data(df):
    st.write(df[["date_mutation","type_local","nature_mutation","longitude","latitude"]].head(15))

@log
def map(df):
    map_data=prepare_map(df)
    months_filter = st.slider('Select a month (1 --> January, etc ... )', 1, 12,3) 
    map_data_filtered = map_data[map_data["months"] == months_filter] #Printing only values from the choosed month
    st.map(map_data_filtered,zoom=2)

@log
def bar_type_local(df):
    fig = plt.figure(figsize = (24, 12))
    plt.hist(df["type_local"],color='orange')
    plt.title("Type of Local")
    plt.xticks(fontsize=20)
    st.pyplot(fig)

@log
def pie_nature_local(df):
    fig2 = plt.figure(figsize = (24, 12))
    by_nature_local=df.groupby('nature_mutation').apply(count_rows)
    liste=[]
    end=len(by_nature_local.index)
    for i in range (0,end):
        liste.append(by_nature_local.index[i])
    plt.title("Type of real estate transactions ")
    plt.legend(fontsize=8, labels=liste)
    plt.pie(by_nature_local,labels = liste)
    st.pyplot(fig2)


@log
def plot_nature_mutation(df):
    fig3 = plt.figure(figsize = (24, 12))
    appart=df[df['type_local'].str.contains("Appartement")]
    maison=df[df['type_local'].str.contains("Maison")]
    local=df[df['type_local'].str.contains("Local industriel. commercial ou assimilé")]
    dependance=df[df['type_local'].str.contains("Dépendance")]

    appartbydate=appart.groupby('months').apply(count_rows)
    maisonbydate=maison.groupby('months').apply(count_rows)
    localbydate=local.groupby('months').apply(count_rows)
    dependancebydate=dependance.groupby('months').apply(count_rows)

    if st.checkbox('Show Appart'):
        plt.plot(appartbydate,color="blue" )
    if st.checkbox('Show Maison'):
        plt.plot(maisonbydate,color="orange" )
    if st.checkbox('Show Local'):
        plt.plot(localbydate,color="green" )
    if st.checkbox('Show Dependance'):
        plt.plot(dependancebydate,color="black" )


    plt.legend(['Appartement','Local','Local','Dépendance'],loc = "upper right")
    st.pyplot(fig3)


@log
def nb_transac_per_codepostal(df):
    prepare_codepostal(df)
    bycode_postal=df.groupby('new_code_postal').apply(count_rows)
    st.bar_chart(bycode_postal)

@log
def main():
    path = ("Full_2020.csv")
    dataset = loadingdata(path)
    st.title('Real Estate Transactions of 2020')
    prepare_date(dataset)
    st.subheader("Raw Data")
    print_raw_data(dataset)
    st.subheader("Map of all estate transactions per month")
    map(dataset)
    st.subheader("All types of local in 2020")
    bar_type_local(dataset)
    st.subheader("All types of real estate transactions in 2020") 
    pie_nature_local(dataset)
    st.subheader("Real estate transactions per types of local")
    st.write("Select line(s) : ")
    plot_nature_mutation(dataset)
    st.subheader("All real estate transactions per departments ")
    nb_transac_per_codepostal(dataset)

main()
