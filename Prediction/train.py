import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_curve

def process_data(file_path, model_name_suffix=""):
    df = pd.read_csv(file_path)

    df['Time_Block'] = pd.to_datetime(df['Time_Block'])

    df = df.sort_values(by='Time_Block')

    train_size = int(0.60 * len(df))
    val_size = int(0.20 * len(df))

    if train_size == 0 or val_size == 0 or (len(df) - train_size - val_size) == 0:
        raise ValueError("Insufficient data for train/validation/test split.")

    train_df = df.iloc[:train_size]
    val_df = df.iloc[train_size:train_size + val_size]
    test_df = df.iloc[train_size + val_size:]

    X_train = train_df.drop(columns=['Time_Block', 'Anomaly'])  # Features
    y_train = train_df['Anomaly'].astype(int)  # Labels

    X_val = val_df.drop(columns=['Time_Block', 'Anomaly'])
    y_val = val_df['Anomaly'].astype(int)

    X_test = test_df.drop(columns=['Time_Block', 'Anomaly'])
    y_test = test_df['Anomaly'].astype(int)

    feature_names = X_train.columns

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    rf_model = RandomForestClassifier(class_weight='balanced')
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict_proba(X_test)[:, 1]
    rf_val = rf_model.predict_proba(X_val)[:, 1]

    rf_feature_importances = rf_model.feature_importances_

    lr_model = LogisticRegression(max_iter=1000, class_weight='balanced')
    lr_model.fit(X_train, y_train)
    lr_pred = lr_model.predict_proba(X_test)[:, 1]

    lr_coefficients = lr_model.coef_[0]

    feature_importance_df = pd.DataFrame({
        'Feature': feature_names,
        'RandomForest_Importance': rf_feature_importances,
        'LogisticRegression_Coefficient': lr_coefficients
    })

    feature_importance_df.to_csv("featureImportance" + model_name_suffix + ".csv", index=False)

    def evaluate_model(y_true, y_pred, model_name, threshold):
        rf_val_pred = (y_pred >= threshold).astype(int)
        accuracy = accuracy_score(y_true, rf_val_pred)
        precision = precision_score(y_true, rf_val_pred)
        recall = recall_score(y_true, rf_val_pred)
        auc = roc_auc_score(y_true, y_pred)

        print(f"The optimal threshold for {model_name} is {threshold}")
        print(f"Performance of {model_name}:")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"AUC: {auc:.4f}")
        print('-' * 30)

    evaluate_model(y_test, rf_pred, f"Random Forest {model_name_suffix}", threshold=0.3)
    evaluate_model(y_test, lr_pred, f"Logistic Regression {model_name_suffix}",threshold=0.3)

#process_data('template_counts_error_detection.csv', model_name_suffix="error_detection")

process_data('template_counts_error_prediction.csv', model_name_suffix="error_prediction")