import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

BASE_DIR = os.path.dirname(__file__)
MANUAL_CSV_DIR = os.path.join(BASE_DIR, "..", "data", "manual_csv")
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")


def load_manual_csv(languages):
    frames = []
    for language in languages:
        csv_path = os.path.join(MANUAL_CSV_DIR, f"{language.lower()}_manual.csv")
        if not os.path.isfile(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        df = pd.read_csv(csv_path, header=None)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def build_model(input_shape, num_classes):
    return Sequential([
        tf.keras.Input(shape=(input_shape,)),
        Dense(128, activation="relu"),
        Dense(64, activation="relu"),
        Dense(num_classes, activation="softmax"),
    ])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Train gesture model from manual ASL/ISL CSV data"
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        choices=["ASL", "ISL"],
        default=["ASL", "ISL"],
        help="Manual languages to include in training",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=25,
        help="Number of training epochs",
    )
    args = parser.parse_args()

    print("Loading manual CSV data for:", args.languages)
    data = load_manual_csv(args.languages)

    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    model = build_model(X.shape[1], len(encoder.classes_))
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.summary()

    history = model.fit(
        X_train,
        y_train,
        epochs=args.epochs,
        validation_data=(X_test, y_test),
        batch_size=32,
    )

    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, "gesture_model.h5")
    encoder_path = os.path.join(MODEL_DIR, "label_encoder.pkl")

    model.save(model_path)
    print(f"Saved model to {model_path}")

    import pickle
    with open(encoder_path, "wb") as f:
        pickle.dump(encoder, f)
    print(f"Saved encoder to {encoder_path}")
