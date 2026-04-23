#This file contains python code for parsing HTML text to display 34 figures with the correct stats and interactive HTML elements. It contains CSS GUI elements as well. 

def shapiroWilkTester(dataFrame, statistic: str): 
    allColumns = list(dataFrame.columns)
    allColumns.remove('Participant')
    allColumns.remove('Grant')
    allColumns.remove('Pre or Post')
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
    plt.figure(figsize = (5, 6))
    ax = plt.gca()
    
    ax = sns.barplot(
    dataFrame, x="Pre or Post", y=statistic,
    width = 0.65,
    errorbar=("ci", 95), capsize=.2,
    err_kws={"color": "gray", "linewidth": 2},
    linewidth=2.5, facecolor=(0, 0, 0),
    orient = 'x')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax = sns.set_style("whitegrid")

    plt.savefig('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/Webpage/'+statistic+'_seaborn.png', 
                format = "png", 
                bbox_inches='tight',
                dpi = 300)

    

def codeParser(statistic, p_value, SWPValue): 
    print('  <div class="graph-section">')
    print('  <h2>'+statistic+'</h2>')
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
