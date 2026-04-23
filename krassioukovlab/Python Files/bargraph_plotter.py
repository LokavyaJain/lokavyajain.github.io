import pandas as pd
import plotly.express as px
import plotly.io as pio


#First, for the interactive line graph 
dataFrame = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/Summary.csv')
statistic = "Avg_SBP_Drop_During_Daytime_OH"

print(dataFrame.columns)

def pairedPointPlotMaker(dataframe, statistic: str): 
    hover_columns = [statistic, "Pre or Post", "Participant"]
    
    fig = px.line(
        dataFrame,
        x='Pre or Post',
        y=statistic,
        color='Participant',                
        markers=True,              
        line_group='Participant',       
        hover_name='Participant',
        hover_data= hover_columns
    )

    fig.update_layout(
        title=statistic,
        xaxis_title='Time Point',
        showlegend=False,  # You can turn this on if desired
        width=600,
        height=600
    )

    fig.show()


pairedPointPlotMaker(dataFrame, statistic)





#Then, for the black bar graphs 

#This iteration has mean differences displayed on the graph, and removes the validator column 

def shapiroWilkTester(dataFrame, statistic: str): 
    allColumns = list(dataFrame.columns)
    allColumns.remove('Participant')
    allColumns.remove('Grant')
    allColumns.remove('Pre or Post')
    allColumns.remove('Validator (Random Values)')
    allColumns.remove(statistic)
    dataFrame = dataFrame.drop(columns=allColumns)
    
    preDataFrame = dataFrame.loc[dataFrame['Pre or Post'] == 'Pre']
    postDataFrame = dataFrame.loc[dataFrame['Pre or Post'] == 'Post']

    preList = preDataFrame[statistic].tolist()
    postList = postDataFrame[statistic].tolist()

    preList = [x for x in preList if str(x) != 'nan']
    postList = [x for x in postList if str(x) != 'nan']

    dataList = preList+postList

    SWTest = stats.shapiro(dataList)
    pvalue = SWTest.pvalue
    pvalue = round(pvalue, 9)
    pvalue = format(pvalue, '.10f')

    return pvalue


def tTester(dataFrame, statistic: str):
    allColumns = list(dataFrame.columns)
    allColumns.remove('Participant')
    allColumns.remove('Grant')
    allColumns.remove('Pre or Post')
    allColumns.remove('Validator (Random Values)')
    allColumns.remove(statistic)
    dataFrame = dataFrame.drop(columns=allColumns)
    
    preDataFrame = dataFrame.loc[dataFrame['Pre or Post'] == 'Pre']
    postDataFrame = dataFrame.loc[dataFrame['Pre or Post'] == 'Post']

    preList = preDataFrame[statistic].tolist()
    postList = postDataFrame[statistic].tolist()

    preList = [x for x in preList if str(x) != 'nan']
    postList = [x for x in postList if str(x) != 'nan']

    try: 
        t_statistic, p_value = stats.ttest_rel(preList, postList)
        p_value = str(p_value.round(6)) + " (Paired t-test)"
        
    except: 
        t_stat, p_value = stats.ttest_ind(preList, postList, equal_var=False)
        p_value = str(p_value.round(6)) + " (Unpaired t-test Due to Missing Values)"

    return p_value

def nonParametricTester(dataFrame, statistic: str):
    allColumns = list(dataFrame.columns)
    allColumns.remove('Participant')
    allColumns.remove('Grant')
    allColumns.remove('Pre or Post')
    allColumns.remove('Validator (Random Values)')
    allColumns.remove(statistic)
    dataFrame = dataFrame.drop(columns=allColumns)
    
    preDataFrame = dataFrame.loc[dataFrame['Pre or Post'] == 'Pre']
    postDataFrame = dataFrame.loc[dataFrame['Pre or Post'] == 'Post']

    preList = preDataFrame[statistic].tolist()
    postList = postDataFrame[statistic].tolist()

    preList = [x for x in preList if str(x) != 'nan']
    postList = [x for x in postList if str(x) != 'nan']

    try: 
        statistic, p_value = stats.wilcoxon(preList, postList)
        p_value = str(p_value.round(6)) + " (Wilcoxon Test due to Non-normal Data)"
        
    except: 
        t_stat, p_value = stats.mannwhitneyu(preList, postList, method="asymptotic")
        p_value = str(p_value.round(6)) + " (Mann-Whitney U-test Due to Non-normal Data and Missing Values)"

    return p_value


def firstGraphType(dataFrame, statistic: str): 
    hover_columns = [statistic, "Pre or Post", "Participant"]
    fig = px.line(
        dataFrame,
        x='Pre or Post',
        y=statistic,
        color='Participant',                
        markers=True,              
        line_group='Participant',       
        hover_name='Participant',
        hover_data= hover_columns
    )
    fig.update_layout(
        title=statistic,
        xaxis_title='Time Point',
        showlegend=False,  # You can turn this on if desired
    )

    config = {'responsive': True}

    pio.write_html(fig, file='/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/Webpage/'+statistic+'_plotly.html',
                   auto_open=False,
                   include_plotlyjs='cdn',
                   full_html=True, 
                   config=config)
    


def secondGraphType(dataFrame, statistic: str):
#calculating the means from the dataframe 
    group_means = dataFrame.groupby("Pre or Post")[statistic].mean()

    if len(group_means) != 2:
        raise ValueError("Expected exactly two groups for 'Pre or Post'")

    post = group_means.iloc[0]
    pre = group_means.iloc[1]

    difference = f"∆ Mean: {post-pre:.2f}"
    #f means anything inside "{}" is evaluated, and :.2f only works when inside "{}". It expresses it as two decimals
    
    plt.figure(figsize = (5, 5))
    ax = plt.gca()
    
    ax = sns.barplot(
    dataFrame, x="Pre or Post", y=statistic,
    width = 0.65,
    errorbar=("ci", 95), capsize=.2,
    err_kws={"color": "gray", "linewidth": 2},
    linewidth=2.5, facecolor=(0, 0, 0),
    orient = 'x')

    maxList = [pre, post]
    y_max = max(maxList)
    x_pos = 1.7
    
    ax.text(
        1.1,
        0.85,
        transform=ax.transAxes,
        s=(f"Pre: {(pre):.2f}"),
        ha='left',
        va='center',
        fontsize=11,
    )
    ax.text(
        1.1,
        0.75,
        transform=ax.transAxes,
        s=(f"Post: {(post):.2f}"),
        ha='left',
        va='center',
        fontsize=11,
    )
    ax.text(
        1.1,
        0.95,
        transform=ax.transAxes,
        s=difference,
        ha='left',
        va='center',
        fontsize=13,
    )

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax = sns.set_style("whitegrid")
    
    plt.savefig('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/Webpage/'+statistic+'_seaborn.png', 
                format = "png", 
                bbox_inches="tight",
                dpi = 300)
    

def codeParser(statistic, p_value, SWPValue): 
    #changing the statistic strings to remove the underscores and replace with spaces 
    statistic_string = statistic.replace("_", " ")
    
    print('  <div class="graph-section">')
    print('  <h2>'+statistic_string+'</h2>')
    print('  <p>Shapiro-Wilk Test with Pre and Post Combined: '+str(SWPValue)+'</p>')
    print('  <p>P-Value: '+str(p_value)+'</p>')
    print('  <div class="graph-pair">')
    print('      <iframe src="'+statistic+'_plotly.html"></iframe>')
    print('      <img src="'+statistic+'_seaborn.png" />')
    print('  </div>')
    print('  </div>')
    print()


dataFrame = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/Summary.csv')


allColumns = list(dataFrame.columns)
allColumns.remove('Participant')
allColumns.remove('Grant')
allColumns.remove('Pre or Post')
allColumns.remove('Validator (Random Values)')

for x in range (0, len(allColumns)):
    statistic = allColumns[x]
    SWPValue = shapiroWilkTester(dataFrame, statistic)
    if float(SWPValue) > 0.05:
        p_value = tTester(dataFrame, statistic)
    elif float(SWPValue) <= 0.05:
        p_value = nonParametricTester(dataFrame, statistic)
    else:
        [print("ERROR WITH SHAPIRO-WILK TEST SORTING") for x in range(10)]
    firstGraphType(dataFrame, statistic)
    secondGraphType(dataFrame, statistic)
    codeParser(statistic, p_value, SWPValue)



#Finally, for the boxplots

#Writing the code to create boxplots for only DOD participants these metrics with median, IQR, and p-value 

def tTester(dataFrame, statistic: str):
    allColumns = list(dataFrame.columns)
    allColumns.remove('Participant')
    allColumns.remove('Grant')
    allColumns.remove('Pre or Post')
    allColumns.remove('Validator (Random Values)')
    allColumns.remove(statistic)
    dataFrame = dataFrame.drop(columns=allColumns)
    
    preDataFrame = dataFrame.loc[dataFrame['Pre or Post'] == 'Pre']
    postDataFrame = dataFrame.loc[dataFrame['Pre or Post'] == 'Post']

    preList = preDataFrame[statistic].tolist()
    postList = postDataFrame[statistic].tolist()

    preList = [x for x in preList if str(x) != 'nan']
    postList = [x for x in postList if str(x) != 'nan']

    try: 
        t_statistic, p_value = stats.ttest_rel(preList, postList)
        p_value = str(p_value.round(6))
        #p_value = str(p_value.round(6)) + " (Paired t-test)"
        
    except: 
        t_stat, p_value = stats.ttest_ind(preList, postList, equal_var=False)
        p_value = str(p_value.round(6))
        #p_value = str(p_value.round(6)) + " (Unpaired t-test Due to Missing Values)"

    return p_value



def boxplotter(dataFrame, statistic: str, pValue):
    plt.figure(figsize = (7, 7))
    orderList = ['Pre', 'Post']
    sns.boxplot(data = dataFrame,
                x = "Pre or Post",
                y = statistic, 
                color = "black",
                order = orderList,
                width = 0.5,
                fill = False,
                fliersize = 0)
    
    sns.stripplot(data = dataFrame,
            x = "Pre or Post",
            y = statistic, 
             order = orderList, 
             s=7.5, 
             color = "black",
             marker="o", 
             alpha = 0.75)

    ax = plt.gca()

 #---- compute median, Q1, Q3 for each group (and keep order) ----
    group_stats = (
        dataFrame
        .groupby("Pre or Post")[statistic]
        .agg(median="median",
             q1=lambda x: np.percentile(x.dropna(), 25) if len(x.dropna())>0 else np.nan,
             q3=lambda x: np.percentile(x.dropna(), 75) if len(x.dropna())>0 else np.nan)
        .reindex(orderList)
    )

    # ---- Put annotations at a fixed fraction of the axis height (top) ----
    # y_frac defines how far from the bottom of the axes the text sits (0..1).
    # 0.98 is near the top; adjust if needed.
    y_frac = 1.075
    # Ensure top area not clipped
    fig = plt.gcf()
    fig.subplots_adjust(top=0.88)  # leave room for top annotations

    for i, (group, row) in enumerate(group_stats.iterrows()):
        median = row["median"]
        q1 = row["q1"]
        q3 = row["q3"]

        # build text depending on availability of data
        if np.isfinite(median) and np.isfinite(q1) and np.isfinite(q3):
            iqr = q3 - q1
            text_str = f"Median: {median:.2f}\nIQR: {iqr:.2f}\nn={int(dataFrame[dataFrame['Pre or Post']==group][statistic].dropna().shape[0])}"
        else:
            # No finite data for this group — show N/A and count
            count = int(dataFrame[dataFrame['Pre or Post']==group][statistic].dropna().shape[0])
            text_str = f"Median: N/A\nIQR: N/A\nn={count}"

        # Use x in data coordinates (i) and y in axes fraction coords via get_xaxis_transform()
        ax.text(
            i,                  # x = position of the category (0,1,...)
            y_frac,             # y in axes fraction because of the transform used
            text_str,
            transform=ax.get_xaxis_transform(),  # x in data coords, y in axes coords (0..1)
            ha="center",
            va="top",
            fontsize=10,
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.8)  # white box for readability
        )


    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    statistic = statistic.replace("_", " ")
    labelSize = 14
    plt.title(label = statistic + "\n p-value: " + str(pValue) + ("\n \n \n"), size = 14)
    plt.ylabel(ylabel = statistic, size = labelSize)
    plt.xlabel(xlabel = "\n Pre- or Post-Intervention Data", size = labelSize)
    tickSize = 13
    plt.xticks(size = tickSize)
    plt.yticks(size = tickSize)

    plt.savefig("/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/DOD Figures/"+statistic+".png",
            format = "png", 
            dpi = 300,
            bbox_inches='tight')


dataFrame = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/Summary.csv')
dataFrame = dataFrame[dataFrame["Grant"] == "DOD"]
allColumns = list(dataFrame.columns)
allColumns.remove('Participant')
allColumns.remove('Grant')
allColumns.remove('Pre or Post')
allColumns.remove('Validator (Random Values)')

for x in allColumns:
    statistic = x
    p = tTester(dataFrame, statistic)
    boxplotter(dataFrame, statistic, p)
