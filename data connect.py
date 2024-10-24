import os
import pandas as pd
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
df1 = pd.read_csv(os.path.join(current_dir, '2_co2_kibocsajtas.csv'),index_col=0)

current_dir = os.path.dirname(os.path.abspath(__file__))
df2 = pd.read_excel(os.path.join(current_dir, 'regions.xlsx'),index_col=0,header=0)
df2.rename(columns={'Country or Area':'Country'}, inplace=True)

ures=df2['Region 1'].isna().sum()
#print(ures)

df2_altered=df2[['Country','Region 1']]
#print(df2_altered.head())

co2_merge = pd.merge(df1, df2_altered, on='Country', how='left')
#print(co2_merge.iloc[9:15])


co2_merge.loc[co2_merge['Country'].str.contains('Former', na=False), 'Region 1']='Eastern Europe'
co2_merge.loc[co2_merge['Country'].str.contains('Czech', na=False), 'Region 1']='Eastern Europe'

for column in co2_merge.columns:
    if co2_merge[column].dtype in ['float64', 'int64']:
        mean_values = co2_merge.groupby('Region 1')[column].transform('mean')
        co2_merge.loc[co2_merge[column].isna(), column] = mean_values




columns_to_check = ['Energy_consumption','Energy_production','GDP','Population','Energy_intensity_per_capita','Energy_intensity_by_GDP','CO2_emission']
outliers_dict = {}
for column in columns_to_check:
    mean = co2_merge[column].mean()
    std_dev = co2_merge[column].std()
    z_scores = (co2_merge[column] - mean) / std_dev

    outliers = np.abs(z_scores) > 3
    outliers_dict[column] = co2_merge[outliers]

    co2_merge.loc[outliers, column] = mean

for column, outliers in outliers_dict.items():
    print(f"Kiugrók az {column} oszlopban:")
    print(outliers)
co2_merge.to_csv("co2_merge.csv",header=True)