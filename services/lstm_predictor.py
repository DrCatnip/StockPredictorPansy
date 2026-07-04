import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input
from sklearn.preprocessing import MinMaxScaler


# --------------------------------------------------------
# PREPARE DATA
# --------------------------------------------------------

def prepare_data(close_prices, time_step=60):

    scaler = MinMaxScaler(feature_range=(0, 1))

    scaled_data = scaler.fit_transform(close_prices)

    x_train = []
    y_train = []

    for i in range(time_step, len(scaled_data)):

        x_train.append(
            scaled_data[i-time_step:i]
        )

        y_train.append(
            scaled_data[i]
        )

    x_train = np.array(x_train)
    y_train = np.array(y_train)

    return x_train, y_train, scaler


# --------------------------------------------------------
# BUILD MODEL
# --------------------------------------------------------

def build_model(input_shape):

    model = Sequential([

        Input(shape=input_shape),

        LSTM(
            64,
            return_sequences=True
        ),

        LSTM(
            64,
            return_sequences=False
        ),

        Dense(32),

        Dense(1)

    ])

    model.compile(

        optimizer="adam",

        loss="mean_squared_error"

    )

    return model


# --------------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------------

def train_model(

    model,

    x_train,

    y_train,

    epochs=10,

    batch_size=32

):

    history = model.fit(

        x_train,

        y_train,

        epochs=epochs,

        batch_size=batch_size,

        verbose=1

    )

    return history


# --------------------------------------------------------
# PREDICT FUTURE
# --------------------------------------------------------

def predict_future(

    model,

    scaler,

    scaled_data,

    days=10,

    time_step=60

):

    predictions = []

    last_batch = scaled_data[-time_step:]

    current_batch = last_batch.reshape(

        1,

        time_step,

        1

    )

    for _ in range(days):

        prediction = model.predict(

            current_batch,

            verbose=0

        )[0][0]

        predictions.append(prediction)

        current_batch = np.append(

            current_batch[:, 1:, :],

            [[[prediction]]],

            axis=1

        )

    predictions = scaler.inverse_transform(

        np.array(predictions).reshape(-1, 1)

    )

    return predictions


# --------------------------------------------------------
# COMPLETE PIPELINE
# --------------------------------------------------------

def predict_stock(

    close_prices,

    epochs=10,

    future_days=10

):

    x_train, y_train, scaler = prepare_data(close_prices)

    model = build_model(

        (x_train.shape[1], 1)

    )

    train_model(

        model,

        x_train,

        y_train,

        epochs=epochs

    )

    scaled_data = scaler.transform(

        close_prices

    )

    predictions = predict_future(

        model,

        scaler,

        scaled_data,

        future_days

    )

    return predictions