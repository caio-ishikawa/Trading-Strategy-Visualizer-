from tkinter import *
from tkinter import ttk
from twelvedata import TDClient
import numpy as np
import pandas as pd
import time
import matplotlib
import mplfinance as mplFin

key = 'c95e6270c7b14d49a090a6bd6ef3563a'
td = TDClient(apikey=key)

class BackTrader:

    def __init__(self):
        global var
        root = Tk()
        root.title('Back Tester v0.1')
        root.geometry('600x600')
        var = IntVar(root)
        var.set(1)
        
        button_frame = Frame(root)
        button_frame.grid(column=3, row=8, pady=20)

        valueOutput = Text(root, width=60, height=1)

        titleLabel = Label(root, text='Back Tester v0.1')
        titleLabel.config(font=('Verdana 12 bold'))
        compTickerLabel = Label(root, text = 'Ticker Symbol:')
        compIntervalLabel = Label(root, text = 'Interval:')
        compDate1Label = Label(root, text = 'Start Date:')
        compDate2Label = Label(root, text = 'End Date:')

        compTicker = Entry(root)
        compInterval = Entry(root)
        compDate1 = Entry(root)
        compDate2 = Entry(root) 
        
        tree = ttk.Treeview(root)

        saveButton = Button(button_frame, text = 'Get Data', command=lambda:self.getData(compTicker, compInterval, compDate1, compDate2, tree, valueOutput))
        smaButton = Radiobutton(button_frame, variable=var,  value=1, text='SMA20 Crossover')
        bbandButton = Radiobutton(button_frame, variable=var, value=2,  text='BBAND')
        macdButton = Radiobutton(button_frame, variable=var, value=3, text='MACD', padx=20)

        compTicker.grid(column=3, row=3)
        compTickerLabel.grid(column=2, row=3)
        compInterval.grid(column=3, row=4)
        compIntervalLabel.grid(column=2, row=4)
        compDate1.grid(column=3, row=5)
        compDate1Label.grid(column=2, row=5)
        compDate2.grid(column=3, row=6)
        compDate2Label.grid(column=2, row=6)
        
        tree.grid(column=3, row=25, pady=30)
        
        valueOutput.grid(column=3, row=13)
        saveButton.grid(column=3, row=5)
        smaButton.grid(column=3, row=10)
        bbandButton.grid(column=3, row=11)
        macdButton.grid(column=3, row=12)
        
        root.mainloop() 


    def getData(self, compTicker, compInterval, compDate1, compDate2, tree, valueOutput):
        compTickerText = compTicker.get()
        compIntervalText = compInterval.get()
        compDate1Text = compDate1.get()
        compDate2Text = compDate2.get()
        
        ts1 = td.time_series(symbol=compTickerText, interval=compIntervalText, start_date=compDate1Text, end_date=compDate2Text, outputsize=400)
        df1 = ts1.as_pandas()

        if var.get() == 1:
            df1['SMA20']  = df1['close'].iloc[::-1].rolling(window=20).mean()
            df1['criteria'] = df1['close'] < df1['SMA20']
            df1['criteria'].replace(False, np.nan, inplace=True)
            count = df1['criteria'].value_counts()
            valueOutput.insert(END, count)
            self.graphSMA(df1, tree, compTicker)

        if var.get() == 2:
            df1['SMA20'] = df1['close'].iloc[::-1].rolling(window=20).mean()
            df1['Upper Band'] = df1['SMA20'] + (2* df1['close'].iloc[::-1].rolling(window=20).std())
            df1['Lower Band'] = df1['SMA20'] - (2* df1['close'].iloc[::-1].rolling(window=20).std())
            df1['Buy Signal'] = df1['close'] < df1['Lower Band']
            df1['Sell Signal'] = df1['close'] > df1['Upper Band']
            df1['Buy Signal'].replace(False, np.nan, inplace=True)
            count = df1['Buy Signal'].value_counts()
            valueOutput.insert(END, 'Buy Signal Count: {}'.format(count))
            self.graphBBAND(df1, tree, compTicker)

        if var.get() == 3:
            df1['EMA26'] = df1['close'].iloc[::-1].ewm(span=26).mean()
            df1['EMA12'] = df1['close'].iloc[::-1].ewm(span=12).mean()
            df1['MACD'] = df1['EMA12'] - df1['EMA26']
            df1['EMA9'] = df1['MACD'].ewm(span=9).mean()
            df1['Buy Signal'] = df1['MACD'] < df1['EMA9']
            df1['Buy Signal'].replace(False, np.nan, inplace=True)
            self.graphMACD(df1, tree, compTicker)


    def graphSMA(self, df1, tree, compTicker):
        cols = list(df1.columns)
        tree['columns'] = cols
        for i in cols:
            tree.column(i, anchor='w')
            tree.heading(i, text=i, anchor='w')
    
        df1_rows = df1.to_numpy().tolist()
        print(df1_rows)

        for row in df1_rows:
            tree.insert('', 'end', values=row)

        plot2 = mplFin.make_addplot(df1['SMA20'], color='g', panel=0)
        mplFin.plot(df1, type='candle', style='charles', title='{}'.format(compTicker),  ylabel='Prices$', addplot=plot2)
        
         


    def graphBBAND(self, df1, tree, compTicker):
        cols = list(df1.columns)
        tree['columns'] = cols
        for i in cols:
            tree.column(i, anchor='w')
            tree.heading(i, text=i, anchor='w')
    
        df1_rows = df1.to_numpy().tolist()
        print(df1_rows)

        for row in df1_rows:
            tree.insert('', 'end', values=row)

        subplots= [mplFin.make_addplot(df1['Upper Band'], color='g', panel=0),
                   mplFin.make_addplot(df1['Lower Band'], color='b', panel=0)]
        mplFin.plot(df1, type='candle', style='charles', title='{}'.format(compTicker),  ylabel='Prices$', addplot=subplots)


    def graphMACD(self, df1, tree, compTicker):
        cols = list(df1.columns)
        tree['columns'] = cols
        for i in cols:
            tree.column(i, anchor='w')
            tree.heading(i, text=i, anchor='w')
    
        df1_rows = df1.to_numpy().tolist()
        print(df1_rows)

        for row in df1_rows:
            tree.insert('', 'end', values=row)

        subplots = [mplFin.make_addplot(df1['MACD'], color='g', panel=1),
                   mplFin.make_addplot(df1['EMA9'], color='b', panel=1)]
        mplFin.plot(df1, type='candle', style='charles', title='MACD', ylabel='Price $', addplot=subplots)









BackTrader()
