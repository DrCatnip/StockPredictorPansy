import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from keras.models import Sequential
from keras.layers import LSTM, Dense, Input
from sklearn.preprocessing import MinMaxScaler

# ---------------------------------
# PAGE CONFIG
# ---------------------------------

st.set_page_config(
    page_title="Stock Price Predictor",
    layout="wide"
)

# ---------------------------------
# TITLE
# ---------------------------------

st.title("📈 Stock Price Prediction App")

# ---------------------------------
# STOCK SELECTOR
# ---------------------------------

stock = st.selectbox(
    "Select a Stock",
    ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
)

# ---------------------------------
# LOAD STOCK DATA
# ---------------------------------

@st.cache_data
def load_data(symbol):

    data = yf.download(
        symbol,
        period="5y",
        auto_adjust=True,
        progress=False
    )

    return data

data = load_data(stock)

# ---------------------------------
# CHECK DATA
# ---------------------------------

if data.empty:
    st.error("No stock data found.")
    st.stop()

# ---------------------------------
# CLOSE PRICES
# ---------------------------------

close_prices = data[['Close']].values

# ---------------------------------
# LATEST PRICE
# ---------------------------------

latest_price = close_prices[-1][0]

st.subheader(
    f"Latest Price: ${latest_price:.2f}"
)

# ---------------------------------
# SHOW RECENT DATA
# ---------------------------------

st.subheader("Recent Stock Data")

st.dataframe(data.tail())

# ---------------------------------
# HISTORICAL GRAPH
# ---------------------------------

st.subheader("Historical Closing Prices")

historical_fig = go.Figure()

historical_fig.add_trace(

    go.Scatter(

        x=data.index,

        y=close_prices.flatten(),

        mode='lines',

        name='Close Price'
    )
)

historical_fig.update_layout(

    title=f"{stock} Historical Prices",

    xaxis_title="Date",

    yaxis_title="Price ($)",

    template="plotly_dark"
)

st.plotly_chart(
    historical_fig,
    width='stretch'
)

# ---------------------------------
# NORMALIZE DATA
# ---------------------------------

scaler = MinMaxScaler(
    feature_range=(0, 1)
)

scaled_data = scaler.fit_transform(
    close_prices
)

# ---------------------------------
# CREATE TRAINING DATA
# ---------------------------------

x_train = []
y_train = []

time_step = 60

for i in range(time_step, len(scaled_data)):

    x_train.append(
        scaled_data[i-time_step:i]
    )

    y_train.append(
        scaled_data[i]
    )

x_train = np.array(x_train)
y_train = np.array(y_train)

# ---------------------------------
# BUILD MODEL
# ---------------------------------

model = Sequential([

    Input(
        shape=(x_train.shape[1], 1)
    ),

    LSTM(
        50,
        return_sequences=True
    ),

    LSTM(
        50,
        return_sequences=False
    ),

    Dense(25),

    Dense(1)

])

# ---------------------------------
# COMPILE MODEL
# ---------------------------------

model.compile(
    optimizer='adam',
    loss='mean_squared_error'
)

# ---------------------------------
# TRAIN BUTTON
# ---------------------------------

if st.button("🚀 Train Model and Predict"):

    st.subheader("Training Model...")

    # Train Model
    model.fit(

        x_train,

        y_train,

        batch_size=32,

        epochs=5,

        verbose=1
    )

    st.success("Model Training Complete!")

    # ---------------------------------
    # PREDICT NEXT 10 DAYS
    # ---------------------------------

    predictions = []

    last_60_days = scaled_data[-60:]

    current_batch = last_60_days.reshape(
        1,
        60,
        1
    )

    for i in range(10):

        predicted_price = model.predict(
            current_batch,
            verbose=0
        )[0][0]

        predictions.append(
            predicted_price
        )

        current_batch = np.append(
            current_batch[:, 1:, :],
            [[[predicted_price]]],
            axis=1
        )

    # ---------------------------------
    # INVERSE TRANSFORM
    # ---------------------------------

    predictions = scaler.inverse_transform(
        np.array(predictions).reshape(-1, 1)
    )

    # ---------------------------------
    # FUTURE DATES
    # ---------------------------------

    future_dates = pd.date_range(

        start=pd.Timestamp.today(),

        periods=10
    )

    # ---------------------------------
    # PREDICTION DATAFRAME
    # ---------------------------------

    prediction_df = pd.DataFrame({

        "Date": future_dates.strftime('%Y-%m-%d'),

        "Predicted Price": predictions.flatten()

    })

    # ---------------------------------
    # SHOW PREDICTIONS
    # ---------------------------------

    st.subheader("🔮 Predicted Prices")

    st.table(prediction_df)

    # ---------------------------------
    # PREDICTION GRAPH
    # ---------------------------------

    prediction_fig = go.Figure()

    prediction_fig.add_trace(

        go.Scatter(

            x=prediction_df["Date"],

            y=prediction_df["Predicted Price"],

            mode='lines+markers',

            name='Predicted Price'
        )
    )

    prediction_fig.update_layout(

        title=f"10-Day Prediction for {stock}",

        xaxis_title="Date",

        yaxis_title="Predicted Price ($)",

        template="plotly_dark"
    )

    st.plotly_chart(
        prediction_fig,
        width='stretch'
    )