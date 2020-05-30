from pylivetrader.api import *
import numpy as np
# import sendgrid
# from sendgrid.helpers.mail import *
import os
import alpaca_trade_api as tradeapi
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage



def initialize(context):
    schedule_function(before_trading_start, date_rules.every_day(), time_rules.market_open(hours=0, minutes=1))
    schedule_function(notification, date_rules.every_day(), time_rules.market_open(hours=0, minutes=5))
    context.sell = False
    context.buy = False
    print('Initialize')


def before_trading_start(context, data):
    if not hasattr(context, 'age') or not context.age:
        context.age = {}
    today = get_datetime().floor('1D')
    last_date = getattr(context, 'last_date', None)
    if today != last_date:
        context.stock = symbol('AAPL')
        context.last_date = today
    print('Before trading starts')


def bollinger_bands(context, data):
    period = 13
    current_price = data.current(context.stock, 'price')
    prices = data.history(context.stock, 'price', period, '1d')
    avg_13 = prices.mean()
    std = prices.std()

    upper_band1 = avg_13 + std
    upper_band2 = avg_13 + 2*std
    lower_band1 = avg_13 - std
    lower_band2 = avg_13 - 2*std

    stop_loss = 0.02

    if ((current_price > upper_band1) and (current_price < upper_band2)) and not context.buy:
        order_target_percent(context.stock, 1.0)
        context.buy = True
        context.sell = False
        print('Long position')

    elif ((current_price < lower_band1) and (current_price > lower_band2)) and not context.sell:
        order_target_percent(context.stock, -1.0)
        context.buy = False
        context.sell = True
        print('Short position')

    elif (current_price < (1 - stop_loss) * lower_band2) and context.buy:
        order_target_percent(context.stock, 0)
        context.buy = False
        context.sell = False
        print('Stop loss on long')

    elif (current_price > (1 + stop_loss) * upper_band2) and context.sell:
        order_target_percent(context.stock, 0)
        context.buy = False
        context.sell = False
        print('Stop loss short')

def handle_data(context, data):
    bollinger_bands(context, data)
    print("calculating bb's...")

def notification(context, data):
    api = tradeapi.REST(
        'PKH8BZ5IYVSIDECT1WR1',
        'TmDbyGLqm1GwGdNjy4nHDjuGbFRx5KFHyzce/M9b',
        'https://paper-api.alpaca.markets'
    )
    account = api.get_account()
    balance_change = float(account.equity) - float(account.last_equity)
    print('Today\'s portfolio balance change: '+ str(balance_change))

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login('cunhafh@gmail.com', 'Unicornix2018?')
    msg = MIMEMultipart()
    msg['From']='cunhafh@gmail.com'
    msg['To']='felipe.cunha@ymail.com'
    msg['Subject']=balance_change
    s.send_message(msg)

    # message = Mail(
    #     from_email='cunhafh@gmail.com',
    #     to_emails='felipe.cunha@ymail.com',
    #     subject='Balance Change',
    #     html_content="Last balance change was: "+str(balance_change))
    # try:
    #     sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    #     response = sg.send(message)
    #     print(response.status_code)
    #     print(response.body)
    #     print(response.headers)
    # except Exception as e:
    #     print(e.message)

# echo "export SENDGRID_API_KEY='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'" > sendgrid.env
# echo "sendgrid.env" >> .gitignore
# source ./sendgrid.env
