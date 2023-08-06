# Mosaiq for Python

This is a simplified [mosaic plot](https://en.wikipedia.org/wiki/Mosaic_plot)
technique that works for numeric/categorical data.

![Imgur](https://i.imgur.com/atssMvU.png)

For categorical data, a frequency table of values is calculated.  Only the top 7
most common categories are preserved.  The rest are replaced by "NA_TOPN".

For numeric data, a histogram is calculated over the distribution. The precise
numeric values are replaced by its respective bin.

Call it with the following arguments:

1. A dataframe
2. The name of a "feature" column
3. The name of a "target" column
4. Whether the color ramp should be inverted (default : False)
5. A colormap (default : derived from target column)
6. The number of categories to preserve in categorical data (default : 7)

```python
# dat (pandas dataframe)
# feature (feature name string)
# target (target name string)
mosaiq(dat, feature, target)
```

Using this visualization makes it easy to iterate through all feature/target
interactions in a given dataset:


```python
for col in dat.columns:
    if col == target:
        continue # skip the plot if the column is the target

    mosaiq(mdat, col, target)
    plt.show()

```


