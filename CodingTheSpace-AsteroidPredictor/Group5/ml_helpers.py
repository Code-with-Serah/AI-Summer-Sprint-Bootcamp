import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    confusion_matrix,
    roc_curve,
    auc
)

def load_data(file_path):
    """Load dataset from a CSV file with error handling."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"The file '{file_path}' is empty or invalid.")
    except pd.errors.ParserError:
        raise ValueError(f"Parsing error: The file '{file_path}' is not a valid CSV.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while reading the file: {e}")

    if df.shape[1] < 2:
        raise ValueError("The dataset must contain at least two columns: features and target.")

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    return X, y

def split_data(X, y, test_size=0.3, random_state=42):
    """Split dataset into training and test sets."""
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=random_state)

def validate_training_data(X, y):
    """Validate training data for model fitting."""
    if X is None or y is None:
        raise ValueError("Training data cannot be None.")
    if len(X) == 0 or len(y) == 0:
        raise ValueError("Training data is empty.")
    if len(X) != len(y):
        raise ValueError("Mismatched X and y lengths.")

def print_classification_metrics(y_test, y_pred):
    """Print standard classification metrics."""
    try:
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("F1 Score:", f1_score(y_test, y_pred))
        print("Precision:", precision_score(y_test, y_pred))
        print("Recall:", recall_score(y_test, y_pred))
        print("\nClassification Report:\n", classification_report(y_test, y_pred))
    except Exception as e:
        print(f"Error in computing classification metrics: {e}")

def plot_confusion_matrix(y_test, y_pred):
    """Plot the confusion matrix."""
    try:
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title("Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error in plotting confusion matrix: {e}")

def plot_roc_curve(fpr, tpr):
    """Plot ROC curve."""
    try:
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve")
        plt.legend()
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error in plotting ROC curve: {e}")


def evaluate_model_basic(model, X_test, y_test):
    """Evaluate the model using prediction-only metrics."""
    try:
        y_pred = model.predict(X_test)
    except Exception as e:
        print(f"Error during model prediction: {e}")
        return

    print_classification_metrics(y_test, y_pred)
    plot_confusion_matrix(y_test, y_pred)


def evaluate_model_with_proba(model, X_test, y_test):
    """Evaluate the model’s probabilistic outputs (ROC curve, AUC)."""
    try:
        # If the model doesn’t support predict_proba, this will raise
        y_prob = model.predict_proba(X_test)[:, 1]
    except Exception as e:
        print(f"Error during probability prediction: {e}")
        return
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    plot_roc_curve(fpr, tpr)

