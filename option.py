# Retail Capital x TheStatisticalEdge
# retailcapital.substack.com
# @itsonlymoney12 on Twitter

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import yfinance as yf
import numpy as np

st.set_page_config(layout="wide")

def get_expiry(ticker):
	try:
		nq = yf.Ticker(ticker)

		return list(nq.options)
	except Exception as e:
		# st.exception(e)
		print('This stock doesn\'t exist')

def get_calls(ticker, option_expiry):

	try:
		nq = yf.Ticker(ticker)
		last_close = nq.history()
		last_close = list(last_close['Close'])[-1]
		
		option = nq.option_chain(option_expiry)
		
		calls = option.calls
		calls = pd.DataFrame(calls)
		calls = calls[['strike', 'volume', 'openInterest']]

		puts = option.puts
		puts = pd.DataFrame(puts)
		puts = puts[['strike', 'volume', 'openInterest']]

		strikes = list(set(list(calls['strike']) + list(puts['strike'])))

		return calls, puts, last_close
	except Exception as e:
		# st.exception(e)
		print('Ticker not working...')

def plot_max_pain(ticker, option_date):

	try:
		nq = yf.Ticker(ticker)
		option_chain = nq.option_chain(option_date)
		calls = option_chain.calls
		puts = option_chain.puts
		merged = pd.merge(calls, puts, on='strike', suffixes=('_call', '_put'))

		# Extract strike prices and open interest
		call_strikes = np.array(merged['strike'])
		call_oi = np.array(merged['openInterest_call'])
		put_strikes = np.array(merged['strike'])
		put_oi = np.array(merged['openInterest_put'])

		# Calculate total value of calls and puts for each strike price
		underlying_price = nq.history().iloc[-1]['Close']
		call_values = (np.maximum(call_strikes, 0) * call_oi * 100)
		put_values = (np.maximum(put_strikes, 0) * put_oi * 100) 
		call_values =np.cumsum(call_values)
		put_values=np.cumsum(put_values[::-1])[::-1]

		call_minus_put = call_values - put_values
		index_maxpain = next((i for i, n in enumerate(call_minus_put) if n > 0), None)
		max_pain = call_strikes[index_maxpain]
		prior_max_pain = call_strikes[index_maxpain-1]
		# Create a mountain chart
		fig = go.Figure()
		fig.add_trace(go.Scatter(x=call_strikes, y=call_values, mode='lines', fill='tozeroy', line=dict(color='green'), name='Calls'))
		fig.add_trace(go.Scatter(x=put_strikes, y=put_values, mode='lines', fill='tozeroy', line=dict(color='red'), name='Puts'))

		# Add labels and title
		# fig.update_layout(title=f'{ticker} Max Pain on {option_date}', xaxis_title='Strike Price', yaxis_title='Option Value ($)')
		fig.update_layout(
			title={
			'text':f'${ticker.upper()} Max Pain on {option_date} = ${max_pain}',
			"x": 0.5,
			"xanchor": "center",
			"yanchor": "top",
			"font":{"size":22}
			}, 
			xaxis_title={
			'text':'<b>Strike</b>',
			"font": {"size": 18}
			}, 
			yaxis_title={
			'text':'<b>Option Value ($)</b>',
			'font': {'size':18}
			})

		fig.update_layout(
			plot_bgcolor='#1C1F2E',
			paper_bgcolor='#1C1F2E',
			# plot_bgcolor_border	='khaki',
			template='plotly_dark',
			# bordercolor='orange',
			xaxis={
			"tickangle": -45,
			"tickfont": {"size": 16},
			"showgrid":False,
			"zeroline":False,
			"zerolinecolor":'white',
			"zerolinewidth":2,
			},

			yaxis={
			"tickangle": 0,
			"tickfont": {"size": 16},
			"showgrid":False,
			"zeroline":False	,
			"zerolinecolor":'white',
			"zerolinewidth":2,
			}
			)
		fig.add_annotation(
			x=(max_pain + prior_max_pain)/2, y=call_values[index_maxpain-1],
			ax=0, 
		    # ay=0,
		    # arrowhead=2,
		    # arrowsize=5,
		    text=f'${max_pain}',
		    # showarrow=True,
		    font=dict(
		    	family="Courier New, monospace",
		    	size=18,
		    	color="yellow",
		        # weight="bold"
		        ),
		    # align='center',
		    # arrowcolor='yellow',
		    # bgcolor='red',
		    opacity=1
		    )
		fig.update_layout(xaxis_range=[put_strikes.min(), call_strikes.max()])
		st.plotly_chart(fig, use_container_width=True)
	except Exception as e:
		print('Ticker not working...')
		st.markdown("<div style='background-color: purple; padding: 20px; border-radius: 5px; color: white;'><p> This ticker doesn't exist in the database.</p></div>", unsafe_allow_html=True)


def plot_double_bar_chart(option, ticker):

    option_data = get_calls(ticker, option)

    try:

	    df_calls = option_data[0]
	    df_puts = option_data[1]
	    # df_puts['openInterest'] = df_puts['openInterest'].apply(lambda x: -x)
	    last_close = option_data[2]

	    fig = go.Figure(data=[
	        go.Bar(name='Calls OI', x=df_calls['strike'], y=df_calls['openInterest'], marker=dict(color='green')),
	        go.Bar(name='Puts OI', x=df_puts['strike'], y=df_puts['openInterest'], marker=dict(color='#FF5757', opacity=0.8))
	    ])
	    fig.update_layout(barmode='group', 
	    	title={
	    	'text':f'${ticker.upper()} - {option} Open Interest by Strike',
	    	"x": 0.5,
	        "xanchor": "center",
	        "yanchor": "top",
	        "font":{"size":22}
	        }, 
	    	xaxis_title={
	    	'text':'<b>Strike</b>',
	    	"font": {"size": 18}
	    	}, 
	    	yaxis_title={
	    	'text':'<b>Open Interest</b>',
	    	'font': {'size':18}
	    	})

	    fig.add_shape(type='line', x0=last_close, y0=0, x1=last_close, y1=max(np.max(df_calls['openInterest']),np.max(df_puts['openInterest'])), line=dict(color='yellow', width=3, dash='dash'), name='Prev. Close')

	    fig.add_annotation(text='@itsonlymoney12', xref='paper', yref='paper', x=0.05, y=0.9, showarrow=False, font=dict(color='lightgrey', size=20), opacity=0.4)

	    fig.add_trace(
	    	go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='yellow', width=3, dash='dash'), name='Prev. Close')
	    	)

	    fig.update_layout(
	    	plot_bgcolor='#1C1F2E',
	    	paper_bgcolor='#1C1F2E',
	    	template='plotly_dark',
		    xaxis={
		        "tickangle": -45,
		        "tickfont": {"size": 16},
		        "showgrid":False,
		        "zeroline":False,
		        "zerolinecolor":'white',
		        "zerolinewidth":2,
		    },

	    	yaxis={
		        "tickangle": 0,
		        "tickfont": {"size": 16},
		        "showgrid":False,
		        "zeroline":False	,
		        "zerolinecolor":'white',
		        "zerolinewidth":2,
	    	}
	    	)
	    if len(df_calls) > 70:
	    	fig.update_layout(xaxis_range=[max(last_close*0.65,df_puts['strike'].min()),min(last_close*1.35, df_calls['strike'].max())])

	    st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
    	print('Ticker not working...')
    	st.markdown("<div style='background-color: purple; padding: 20px; border-radius: 5px; color: white;'><p> This ticker doesn't exist in the database.</p></div>", unsafe_allow_html=True)

def get_call_oi(ticker, date_looked):
	nq = yf.Ticker(ticker)
	option = nq.option_chain(date_looked)

	calls = option.calls
	calls = pd.DataFrame(calls)
	calls = calls[['strike', 'volume', 'openInterest']]

	total_oi = calls['openInterest'].sum()

	return total_oi

def get_put_oi(ticker, date_looked):
	nq = yf.Ticker(ticker)
	option = nq.option_chain(date_looked)

	puts = option.puts
	puts = pd.DataFrame(puts)
	puts = puts[['strike', 'volume', 'openInterest']]

	total_oi = puts['openInterest'].sum()

	return total_oi

def get_call_and_put_oi(ticker, date_looked):
	nq = yf.Ticker(ticker)
	option = nq.option_chain(date_looked)

	calls = option.calls
	calls = pd.DataFrame(calls)
	calls = calls[['strike', 'volume', 'openInterest']]

	total_oi_call = calls['openInterest'].sum()

	puts = option.puts
	puts = pd.DataFrame(puts)
	puts = puts[['strike', 'volume', 'openInterest']]

	total_oi_puts = puts['openInterest'].sum()

	return total_oi_call, total_oi_puts

def plot_all_expiry(ticker):
	try:
		all_expiry = get_expiry(ticker)
		
		all_calls = {}
		all_puts = {}
		all_dates = []
		for expiry in all_expiry:
			if '2023' in str(expiry):
				all_dates.append(expiry)
				temp = get_call_and_put_oi(ticker, expiry)
				all_calls[expiry] = temp[0]
				all_puts[expiry] = temp[1]

		all_calls = pd.DataFrame.from_dict(all_calls, orient='index').reset_index()
		all_calls.columns = ['Expiry', 'openInterest']

		all_puts = pd.DataFrame.from_dict(all_puts, orient='index').reset_index()
		all_puts.columns = ['Expiry', 'openInterest']
		# all_puts['Expiry'] = all_puts['Expiry'].apply(lambda x: -x)

		fig = go.Figure(data=[
			go.Bar(name='Calls OI', x=all_calls['Expiry'], y=all_calls['openInterest'], marker=dict(color='green')),
			go.Bar(name='Puts OI', x=all_puts['Expiry'], y=all_puts['openInterest'], marker=dict(color='#FF5757'))
			])

		fig.update_layout(barmode='group', 
			title={
			'text':f'${ticker.upper()} - Open Interest by Expiry Date in 2023',
			"x": 0.5,
			"xanchor": "center",
			"yanchor": "top",
			"font":{"size":22}
			}, 
			xaxis_title={
			'text':'<b>Expiry Date</b>',
			"font": {"size": 18}
			}, 
			yaxis_title={
			'text':'<b>Open Interest</b>',
			'font': {'size':18}
			},
		    xaxis={
		        "type": "category",
		        "tickmode": "array",
		        "tickvals": all_dates
		    }
			)

		fig.add_annotation(text='@itsonlymoney12', xref='paper', yref='paper', x=0.5, y=0.85, showarrow=False, font=dict(color='lightgrey',size=20), opacity=0.4)

		fig.update_layout(
			plot_bgcolor='#1C1F2E',
			paper_bgcolor='#1C1F2E',
			template='plotly_dark',
			xaxis={
			"tickangle": -45,
			"tickfont": {"size": 16},
			"showgrid":False,
			"zeroline":False,
			"zerolinecolor":'white',
			"zerolinewidth":2,
			},

			yaxis={
			"tickangle": 0,
			"tickfont": {"size": 16},
			"showgrid":False,
			"zeroline":False,
			"zerolinecolor":'white',
			"zerolinewidth":2,
			}
			)

		st.plotly_chart(fig, use_container_width=True)

	except Exception as e:
		print('Ticker not working...')

def main():
    # st.write(f"<h1 style='font-size: 26px;'>Retail Capital\'s Open Interest by Strike</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])

    ticker = col1.text_input('Enter a Ticker', 'QQQ').strip().title()

    if ticker != '':
	    option_expiry = get_expiry(ticker)
	    selected_option = col2.selectbox('Select an Option Expiry', option_expiry)

	    plot_double_bar_chart(selected_option, ticker)

	    col1, col2 = st.columns(2)

	    with col1:
	    	st.markdown("<a href='https://retailcapital.substack.com/' target='_blank' style='color: white; display: block; text-align: center; width: 100%; background-color: #567BF4; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;'>Read retailcapital.substack.com</a>", unsafe_allow_html=True)

	    with col2:
	 	   st.markdown("<a href='https://apextraderfunding.com/member/aff/go/itsonlymoney?c=GVXZJABB' target='_blank' style='color: white; display: block; text-align: center; width: 100%; background-color: #567BF4; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;'>APEX PROMO | Use 'GVXZJABB'</a>", unsafe_allow_html=True)

	 	# st.write("Option Expiry is in beta mode", unsafe_allow_html=True)
	    plot_max_pain(ticker,selected_option)
	    plot_all_expiry(ticker)	    	


    st.markdown("<div style='text-align: justify; padding: 20px; border-radius: 5px; color: white;'><p> The data presented in this app is sourced from Yahoo Finance and have delays. It's recommended to use this tool after market close. Please note that if the ticker entered is not found, no graphs will appear. Also, please avoid using the $ symbol when entering the ticker symbol. There is no need to use capital letters for the ticker.The first graph will pop up fairly quickly. The second one takes a bit longer (15s to 30s). I am aware of some issues with the Yahoo Option Chain, especially for $TSLA, $GOOGL and a few other stocks, probably due to stock splits.<p>Example: QQQ, SPY, TSLA, AAPL, GOOGL... </p> </p> <p>Disclaimer: The information provided on this website is for educational purposes only and should not be construed as financial advice. The content and data presented may not be accurate or complete, and should not be relied upon for making investment decisions. You should conduct your own research and consult with a qualified financial advisor before making any investment decisions. The authors and publishers of this website are not responsible for any losses that may result from the use of this information.</p></div>", unsafe_allow_html=True)

st.markdown(
	"""
	<style>
	.stPlotlyChart {
	border-radius: 25px;
	overflow: hidden;
	}
	</style>
	""",
	unsafe_allow_html=True,
	)

st.markdown("""
    <style>
        body {
            background-color: #1B1B1B !important;
            color: #FFFFFF !important;
        }
        /* Add more CSS styles here as needed */
    </style>
""", unsafe_allow_html=True)

if __name__ == '__main__':
	main()