from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import kiripto_nova.pandaspd

def train_ai_model(data):
    X = data.drop("target", axis=1)
    y = data["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print(f"?Y Model do"Yrulu"Yu: %{round(accuracy * 100, 2)}")

    return model
def get_signal_from_model(model, new_data_row):
    prediction = model.predict([new_data_row])
    return "BUY" if prediction[0] == 1 else "SELL"
