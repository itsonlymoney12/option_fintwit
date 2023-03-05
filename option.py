# Retail Capital x TheStatisticalEdge
# retailcapital.substack.com
# @itsonlymoney12 on Twitter

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import yfinance as yf
import numpy as np

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


def plot_double_bar_chart(option, ticker):

    option_data = get_calls(ticker, option)

    try:

	    df_calls = option_data[0]
	    df_puts = option_data[1]
	    last_close = option_data[2]

	    fig = go.Figure(data=[
	        go.Bar(name='Calls OI', x=df_calls['strike'], y=df_calls['openInterest'], marker=dict(color='green')),
	        go.Bar(name='Puts OI', x=df_puts['strike'], y=df_puts['openInterest'], marker=dict(color='#FF5757'))
	    ])
	    fig.update_layout(barmode='group', title=f'${ticker.upper()} - {option} Open Interest by Strike', xaxis_title='Strike', yaxis_title='Open Interest')

	    fig.add_shape(type='line', x0=last_close, y0=0, x1=last_close, y1=max(np.max(df_calls['openInterest']),np.max(df_puts['openInterest'])), line=dict(color='yellow', width=3, dash='dash'), name='Prev. Close')

	    fig.add_annotation(text='@itsonlymoney12', xref='paper', yref='paper', x=0.0, y=0.85, showarrow=False, font=dict(color='lightgrey', size=20), opacity=0.4)

	    fig.add_trace(
	    	go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='yellow', width=3, dash='dash'), name='Prev. Close')
	    	)
	    st.plotly_chart(fig)

    except Exception as e:
    	print('Ticker not working...')

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

		for expiry in all_expiry:
			if '2023' in str(expiry):
				temp = get_call_and_put_oi(ticker, expiry)
				all_calls[expiry] = temp[0]
				all_puts[expiry] = temp[1]

		all_calls = pd.DataFrame.from_dict(all_calls, orient='index').reset_index()
		all_calls.columns = ['Expiry', 'openInterest']

		all_puts = pd.DataFrame.from_dict(all_puts, orient='index').reset_index()
		all_puts.columns = ['Expiry', 'openInterest']

		fig = go.Figure(data=[
			go.Bar(name='Calls OI', x=all_calls['Expiry'], y=all_calls['openInterest'], marker=dict(color='green')),
			go.Bar(name='Puts OI', x=all_puts['Expiry'], y=all_puts['openInterest'], marker=dict(color='#FF5757'))
			])
		fig.update_layout(barmode='group', title=f'${ticker.upper()} - Open Interest by Expiry Date in 2023', xaxis_title='Expiry Date', yaxis_title='Open Interest')
		fig.add_annotation(text='@itsonlymoney12', xref='paper', yref='paper', x=0.5, y=0.85, showarrow=False, font=dict(color='lightgrey',size=20), opacity=0.4)
		st.plotly_chart(fig)
	except Exception as e:
		print('Ticker not working...')

def main():
    st.title('Option Analysis - by Retail Capital')

    ticker = st.text_input('Enter a Ticker')
    if ticker != '':
	    option_expiry = get_expiry(ticker)
	    selected_option = st.selectbox('Select an Option Expiry', option_expiry)

	    col1, col2 = st.columns(2)
	    
	    with col1:
	    	st.markdown("<a href='https://retailcapital.substack.com/' target='_blank' style='color: white; display: block; text-align: center; width: 100%; background-color: #567BF4; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;'>Read retailcapital.substack.com</a>", unsafe_allow_html=True)

	    with col2:
	 	   st.markdown("<a href='https://apextraderfunding.com/member/aff/go/itsonlymoney?c=GVXZJABB' target='_blank' style='color: white; display: block; text-align: center; width: 100%; background-color: #567BF4; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;'>APEX PROMO | Use 'GVXZJABB'</a>", unsafe_allow_html=True)

	    plot_double_bar_chart(selected_option, ticker)
	    plot_all_expiry(ticker)

    st.markdown("<div style='background-color: purple; padding: 20px; border-radius: 5px; color: white;'><p> The data presented in this app is sourced from Yahoo Finance and have delays. It's recommended to use this tool after market close. Please note that if the ticker entered is not found, no graphs will appear. Also, please avoid using the $ symbol when entering the ticker symbol. There is no need to use capital letters for the ticker.The first graph will pop up fairly quickly. The second one takes a bit longer (15s to 30s).<p>Example: QQQ, SPY, TSLA, AAPL, GOOGL... </p> </p> <p>Disclaimer: The information provided on this website is for educational purposes only and should not be construed as financial advice. The content and data presented may not be accurate or complete, and should not be relied upon for making investment decisions. You should conduct your own research and consult with a qualified financial advisor before making any investment decisions. The authors and publishers of this website are not responsible for any losses that may result from the use of this information.</p></div>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()