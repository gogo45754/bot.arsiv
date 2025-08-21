# ml_filter.py (Yapay zeka destekli sinyal do"rulay"c")
import kiripto_nova.pandaspd
import kiripto_nova.joblib
from sklearn.ensemble import RandomForestClassifier

# "rnek model e"itimi iin kullan"l"r (gerekte bu offline yap"lmal")
def train_model(train_df):
    features = ["RSI_14", "MACD_12_26_9", "MACDs_12_26_9", "EMA_50", "EMA_200", "BBU_20_2.0", "BBL_20_2.0"]
    X = train_df[features]
    y = train_df["label"]  # 1 = ba...ar"l" sinyal, 0 = ba...ar"s"z

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, "ml_signal_model.pkl")
    print("" Model e"itildi ve kaydedildi.")


# E"itilmi... modelle sinyal do"rulama
class MLFilter:
    def __init__(self, model_path="ml_signal_model.pkl"):
        self.model = joblib.load(model_path)

    def evaluate(self, df):
        features = ["RSI_14", "MACD_12_26_9", "MACDs_12_26_9", "EMA_50", "EMA_200", "BBU_20_2.0", "BBL_20_2.0"]
        row = df.iloc[-1:]
        X = row[features]
        prediction = self.model.predict(X)[0]
        confidence = self.model.predict_proba(X)[0][1]  # 1. s"n"f"n olas"l"""
        return prediction, round(confidence, 3)


# Kullan"m rne"i
if __name__ == "__main__":
    # (Gerek kullan"mda train_df gemi... etiketli veriden gelir)
    df = pd.read_csv("example_labeled_data.csv")  # RSI, MACD, EMA, BB + label stunu
    train_model(df)

    # Tahmin rne"i
    latest = df.copy()
    model = MLFilter()
    result, conf = model.evaluate(latest)
    print(f"" Tahmin: {result} | Gven: {conf}")
