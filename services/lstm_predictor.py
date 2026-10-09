import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input
from sklearn.preprocessing import MinMaxScaler

TIME_STEP = 60


def validate_close_prices(close_prices, time_step=TIME_STEP):
    try:
        prices = np.asarray(close_prices, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("Close prices must contain numeric values.") from exc

    if prices.ndim == 1:
        prices = prices.reshape(-1, 1)

    if prices.ndim != 2 or prices.shape[1] != 1:
        raise ValueError("Close prices must be a one-dimensional series.")

    if not np.isfinite(prices).all():
        raise ValueError("Close prices must not contain missing or infinite values.")

    if len(prices) <= time_step:
        raise ValueError(
            f"Need more than {time_step} data points to train the model "
            f"(got {len(prices)}). Choose a longer period or a smaller interval."
        )

    return prices


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

    close_prices = validate_close_prices(close_prices)

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


def backtest_walk_forward(close_prices, horizon=30, windows=3, epochs=10):
    prices = validate_close_prices(close_prices)

    if horizon < 1:
        raise ValueError("The backtest horizon must be at least one data period.")
    if windows < 1:
        raise ValueError("The backtest must contain at least one window.")

    starting_training_bars = len(prices) - horizon * windows

    if starting_training_bars <= TIME_STEP:
        raise ValueError(
            f"A {windows}-window backtest with a {horizon}-bar horizon needs "
            f"at least {TIME_STEP + 1 + horizon * windows} total bars to keep "
            "more than 60 training bars before the first window. Choose a "
            "longer period or a smaller horizon."
        )

    actual_windows = []
    lstm_prediction_windows = []
    baseline_prediction_windows = []
    window_results = []

    def _metrics(actual, predictions):
        errors = predictions - actual
        return {
            "mae": float(np.mean(np.abs(errors))),
            "rmse": float(np.sqrt(np.mean(np.square(errors)))),
            "mape": (
                float(np.mean(np.abs(errors / actual)) * 100)
                if np.all(actual != 0)
                else None
            ),
        }

    first_test_bar = starting_training_bars
    for window_index in range(windows):
        training_end = first_test_bar + window_index * horizon
        test_end = training_end + horizon
        training_prices = prices[:training_end]
        actual = prices[training_end:test_end, 0]

        lstm_predictions = np.asarray(
            predict_stock(
                training_prices,
                epochs=epochs,
                future_days=horizon,
            ),
            dtype=float,
        ).reshape(-1)

        if len(lstm_predictions) != horizon or not np.isfinite(lstm_predictions).all():
            raise ValueError(
                f"The model returned invalid predictions for window {window_index + 1}."
            )

        baseline_predictions = np.full(horizon, training_prices[-1, 0])
        actual_windows.append(actual)
        lstm_prediction_windows.append(lstm_predictions)
        baseline_prediction_windows.append(baseline_predictions)
        window_results.append(
            {
                "window": window_index + 1,
                "training_bars": len(training_prices),
                "test_start_bar": training_end + 1,
                "test_end_bar": test_end,
                "lstm": _metrics(actual, lstm_predictions),
                "baseline": _metrics(actual, baseline_predictions),
            }
        )

    actual = np.concatenate(actual_windows)
    lstm_predictions = np.concatenate(lstm_prediction_windows)
    baseline_predictions = np.concatenate(baseline_prediction_windows)

    return {
        "horizon": horizon,
        "windows": windows,
        "starting_training_bars": starting_training_bars,
        "lstm": _metrics(actual, lstm_predictions),
        "baseline": _metrics(actual, baseline_predictions),
        "window_results": window_results,
        "lstm_predictions": lstm_predictions.tolist(),
        "baseline_predictions": baseline_predictions.tolist(),
        "actual": actual.tolist(),
    }