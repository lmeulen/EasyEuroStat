# EasyEuroStat
Package for downloading Eurostat datasets

Reading a dataset from Eurostat:

```
from easy_eurostat importget_eurostat_dataset

df = get_eurostat_dataset("teilm020")
df
```
![dataframe](https://github.com/lmeulen/EasyEuroStat/blob/main/dataframe.png?raw=true)


Creating a chloropeth map

```
from easy_eurostat import get_eurostat_geodata, get_eurostat_dataset

df = get_eurostat_dataset("teilm020", replace_codes=True, transpose=False, keep_codes=['geo', 's_adj'])
df = df[(df['age'] == 'Total') & (df['sex'] == 'Total')]

df = countries.merge(df, right_on='geo', left_on='NUTS_ID')
ax = df.plot(column='2022M08', figsize=(10,10), legend=True)
ax.set_xlim(2000000, 7000000)
ax.set_ylim(1000000, 6000000)
ax.set_title('Unemployment in the European Union')
```

![map](https://github.com/lmeulen/EasyEuroStat/blob/main/map.png?raw=true)
