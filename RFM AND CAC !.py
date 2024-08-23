#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
pio.templates.default = "plotly_white"

data = pd.read_csv("C:\\Users\\mrsri\\OneDrive\\Documents\\rfm_data2.csv")
print(data.head())


# In[3]:


data.info()


# In[4]:


data['CAC'] = data['Marketing_Spend'] / data['New_Customers']
data['CAC'].head()


# In[5]:


fig1 = px.bar(data, x='Marketing_Channel', 
              y='CAC', title='CAC by Marketing Channel')
fig1.show()


# In[6]:


fig2 = px.scatter(data, x='New_Customers', 
                  y='CAC', color='Marketing_Channel', 
                  title='New Customers vs. CAC', 
                  trendline='ols')
fig2.show()


# In[7]:


summary_stats = data.groupby('Marketing_Channel')['CAC'].describe()
print(summary_stats)


# In[8]:


data['Conversion_Rate'] = data['New_Customers'] / data['Marketing_Spend'] * 100


# In[9]:


fig = px.bar(data, x='Marketing_Channel', 
             y='Conversion_Rate', 
             title='Conversion Rates by Marketing Channel')
fig.show()


# In[10]:


data['Break_Even_Customers'] = data['Marketing_Spend'] / data['CAC']

fig = px.bar(data, x='Marketing_Channel', 
             y='Break_Even_Customers', 
             title='Break-Even Customers by Marketing Channel')
fig.show()


# In[11]:


fig = go.Figure()
fig.add_trace(go.Bar(x=data['Marketing_Channel'], y=data['New_Customers'],
                     name='Actual Customers Acquired', marker_color='royalblue'))

fig.add_trace(go.Bar(x=data['Marketing_Channel'], y=data['Break_Even_Customers'],
                     name='Break-Even Customers', marker_color='lightcoral'))

fig.update_layout(barmode='group', title='Actual vs. Break-Even Customers by Marketing Channel',
                  xaxis_title='Marketing Channel', yaxis_title='Number of Customers')
fig.show()


# RFM

# In[12]:


import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
pio.templates.default = "plotly_white"

print(data.head())


# In[13]:


import pandas as pd

data['PurchaseDate'] = pd.to_datetime(data['PurchaseDate'], format='%d-%m-%Y')  

print("Data type of 'PurchaseDate' column:", data['PurchaseDate'].dtype)
print("Sample of 'PurchaseDate' column:")
print(data['PurchaseDate'].head())

today_date = pd.to_datetime('today').normalize()  
data['Recency'] = (today_date - data['PurchaseDate']).dt.days

frequency_data = data.groupby('CustomerID')['OrderID'].count().reset_index()
frequency_data.rename(columns={'OrderID': 'Frequency'}, inplace=True)
data = data.merge(frequency_data, on='CustomerID', how='left')

monetary_data = data.groupby('CustomerID')['TransactionAmount'].sum().reset_index()
monetary_data.rename(columns={'TransactionAmount': 'MonetaryValue'}, inplace=True)
data = data.merge(monetary_data, on='CustomerID', how='left')


# In[14]:


print(data.head())


# In[15]:


recency_scores = [5, 4, 3, 2, 1]  
frequency_scores = [1, 2, 3, 4, 5]  
monetary_scores = [1, 2, 3, 4, 5]  

data['RecencyScore'] = pd.cut(data['Recency'], bins=5, labels=recency_scores)
data['FrequencyScore'] = pd.cut(data['Frequency'], bins=5, labels=frequency_scores)
data['MonetaryScore'] = pd.cut(data['MonetaryValue'], bins=5, labels=monetary_scores)


# In[16]:


data['RecencyScore'] = data['RecencyScore'].astype(int)
data['FrequencyScore'] = data['FrequencyScore'].astype(int)
data['MonetaryScore'] = data['MonetaryScore'].astype(int)


# In[17]:


data['RFM_Score'] = data['RecencyScore'] + data['FrequencyScore'] + data['MonetaryScore']


segment_labels = ['Low-Value', 'Mid-Value', 'High-Value']
data['Value Segment'] = pd.qcut(data['RFM_Score'], q=3, labels=segment_labels)


# In[18]:


print(data.head())


# In[19]:


segment_counts = data['Value Segment'].value_counts().reset_index()
segment_counts.columns = ['Value Segment', 'Count']

pastel_colors = px.colors.qualitative.Pastel

fig_segment_dist = px.bar(segment_counts, x='Value Segment', y='Count', 
                          color='Value Segment', color_discrete_sequence=pastel_colors,
                          title='RFM Value Segment Distribution')

fig_segment_dist.update_layout(xaxis_title='RFM Value Segment',
                              yaxis_title='Count',
                              showlegend=False)

fig_segment_dist.show()


# In[20]:


data['RFM Customer Segments'] = ''

data.loc[data['RFM_Score'] >= 9, 'RFM Customer Segments'] = 'Champions'
data.loc[(data['RFM_Score'] >= 6) & (data['RFM_Score'] < 9), 'RFM Customer Segments'] = 'Potential Loyalists'
data.loc[(data['RFM_Score'] >= 5) & (data['RFM_Score'] < 6), 'RFM Customer Segments'] = 'At Risk Customers'
data.loc[(data['RFM_Score'] >= 4) & (data['RFM_Score'] < 5), 'RFM Customer Segments'] = "Can't Lose"
data.loc[(data['RFM_Score'] >= 3) & (data['RFM_Score'] < 4), 'RFM Customer Segments'] = "Lost"

print(data[['CustomerID', 'RFM Customer Segments']])


# In[21]:


segment_product_counts = data.groupby(['Value Segment', 'RFM Customer Segments']).size().reset_index(name='Count')

segment_product_counts = segment_product_counts.sort_values('Count', ascending=False)

fig_treemap_segment_product = px.treemap(segment_product_counts, 
                                         path=['Value Segment', 'RFM Customer Segments'], 
                                         values='Count',
                                         color='Value Segment', color_discrete_sequence=px.colors.qualitative.Pastel,
                                         title='RFM Customer Segments by Value')
fig_treemap_segment_product.show()


# In[22]:


champions_segment = data[data['RFM Customer Segments'] == 'Champions']

fig = go.Figure()
fig.add_trace(go.Box(y=champions_segment['RecencyScore'], name='Recency'))
fig.add_trace(go.Box(y=champions_segment['FrequencyScore'], name='Frequency'))
fig.add_trace(go.Box(y=champions_segment['MonetaryScore'], name='Monetary'))

fig.update_layout(title='Distribution of RFM Values within Champions Segment',
                  yaxis_title='RFM Value',
                  showlegend=True)

fig.show()


# In[23]:


correlation_matrix = champions_segment[['RecencyScore', 'FrequencyScore', 'MonetaryScore']].corr()


fig_heatmap = go.Figure(data=go.Heatmap(
                   z=correlation_matrix.values,
                   x=correlation_matrix.columns,
                   y=correlation_matrix.columns,
                   colorscale='RdBu',
                   colorbar=dict(title='Correlation')))

fig_heatmap.update_layout(title='Correlation Matrix of RFM Values within Champions Segment')

fig_heatmap.show()


# In[24]:


import plotly.colors

pastel_colors = plotly.colors.qualitative.Pastel

segment_counts = data['RFM Customer Segments'].value_counts()


fig = go.Figure(data=[go.Bar(x=segment_counts.index, y=segment_counts.values,
                            marker=dict(color=pastel_colors))])


champions_color = 'rgb(158, 202, 225)'
fig.update_traces(marker_color=[champions_color if segment == 'Champions' else pastel_colors[i]
                                for i, segment in enumerate(segment_counts.index)],
                  marker_line_color='rgb(8, 48, 107)',
                  marker_line_width=1.5, opacity=0.6)

fig.update_layout(title='Comparison of RFM Segments',
                  xaxis_title='RFM Segments',
                  yaxis_title='Number of Customers',
                  showlegend=False)

fig.show()


# In[25]:


import pandas as pd
import plotly.graph_objects as go


segment_scores = data.groupby('RFM Customer Segments')[['RecencyScore', 'FrequencyScore', 'MonetaryScore']].mean().reset_index()


fig = go.Figure()


fig.add_trace(go.Bar(
    x=segment_scores['RFM Customer Segments'],
    y=segment_scores['RecencyScore'],
    name='Recency Score',
    marker_color='rgb(158,202,225)'
))


fig.add_trace(go.Bar(
    x=segment_scores['RFM Customer Segments'],
    y=segment_scores['FrequencyScore'],
    name='Frequency Score',
    marker_color='rgb(94,158,217)'
))


fig.add_trace(go.Bar(
    x=segment_scores['RFM Customer Segments'],
    y=segment_scores['MonetaryScore'],
    name='Monetary Score',
    marker_color='rgb(32,102,148)'
))


fig.update_layout(
    title='Comparison of RFM Segments based on Recency, Frequency, and Monetary Scores',
    xaxis_title='RFM Segments',
    yaxis_title='Score',
    barmode='group',
    showlegend=True
)

fig.show()


# INTEGRATION 

# In[26]:


import plotly.express as px

\
fig = px.scatter(data, x='RFM_Score', y='CAC', 
                 title='Customer Acquisition Cost (CAC) vs. RFM Scores',
                 trendline='ols',  
                 labels={'RFM_Score': 'RFM Score', 'CAC': 'Customer Acquisition Cost (CAC)'})


fig.show()


# In[27]:


high_value_segments = data[data['RFM Customer Segments'].isin(['Champions', 'High-Value'])]


# In[28]:


print(high_value_segments.head(2))


# In[29]:


import plotly.express as px

cac_data = data.groupby('Marketing_Channel')[['Marketing_Spend', 'New_Customers']].sum().reset_index()
cac_data['CAC'] = data['Marketing_Spend'] / data['New_Customers']

fig_cac = px.bar(data, x='Marketing_Channel', y='CAC', 
                 title='Customer Acquisition Cost (CAC) by Marketing Channel',
                 labels={'CAC': 'CAC (Customer Acquisition Cost)', 'Marketing_Channel': 'Marketing Channel'})


fig_cac.show()


# In[31]:


import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html



app = dash.Dash(__name__)


app.layout = html.Div([
    html.H1("Customer Segmentation and Marketing Analysis Dashboard"),
    
    html.Div([
        html.H2("RFM Analysis"),
        dcc.Graph(id='fig_segment_dist', figure=fig_segment_dist),
        html.P("RFM (Recency, Frequency, Monetary) analysis is a powerful method for segmenting customers based on their behavior and value to the business. By analyzing RFM segments, businesses can identify high-value, mid-value, and low-value customers."),
        html.P("Insights: Analyze RFM segments distribution to understand the distribution of customer value."),
    ]),
    
  
    html.Div([
        html.H2("CAC Analysis"),
        dcc.Graph(id='fig_cac_by_channel', figure=fig_cac),
        html.P("Customer Acquisition Cost (CAC) analysis helps businesses evaluate the effectiveness of their marketing efforts by comparing the cost of acquiring customers across different marketing channels. By understanding CAC by marketing channel, businesses can allocate their marketing budget more efficiently."),
        html.P("Insights: Evaluate CAC by marketing channel to assess cost-effectiveness and identify the most efficient channels for acquiring customers."),
    ]),
       html.Div([
        html.H2("Additional Insights"),
        html.P("Analyzing the relationship between CAC and customer segments can provide valuable insights into the cost-effectiveness of different marketing strategies."),
        dcc.Graph(id='fig_cac_rfm_segment', figure=fig),
        html.P("Insights: Identify which customer segments are most cost-effective to acquire and tailor marketing strategies accordingly."),
    ]),
    
    
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)  


