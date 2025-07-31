
# 🍼 Baby Cry Sound Classification System

## 📌 Overview

This project classifies baby crying sounds into emotional or physical needs such as **hunger**, **discomfort**, **pain**, **tiredness**, and more. It combines **deep learning models** and **traditional ML classifiers** to analyze audio inputs and return meaningful predictions to aid parents or caregivers.

## 🎯 Objectives

- Identify the reason behind a baby's cry (e.g., *hungry*, *tired*, *needs burping*).
- Provide interpretable predictions.
- Support multiple model architectures for benchmarking:
  - Base CNN
  - ResNet18
  - ResNet50
  - MobileNetV3
  - EfficientNet-B0
  - YAMNet (pretrained on AudioSet)

## 📂 Dataset

- Source: Custom spectrograms of baby cries (from `/content/baby_cry_split/`)
- Categories include:
  - Hungry
  - Tired
  - Discomfort
  - Belly Pain
  - Burping
  - Cold/Hot
  - Laugh
  - Silence
  - Noise

## 🧠 Models Implemented

| Model           | Test Accuracy |
|----------------|---------------|
| Base CNN       | 42.6%         |
| ResNet18       | 44.3%         |
| ResNet50       | 42.4%         |
| MobileNetV3    | 42.3%         |
| EfficientNet-B0| 44.0%         |
| YAMNet         | **65.0%**     |

- YAMNet is pretrained on AudioSet and fine-tuned for baby cry classification.
- All models include dropout and L2 regularization for generalization.

## 📊 Evaluation

Each model was evaluated using:
- Accuracy
- Precision / Recall / F1-score
- Confusion Matrix
- Training Curves (Accuracy vs Epochs, Loss vs Epochs)

> SVM and XGBoost were also tested using ResNet18 feature embeddings with competitive results.

## 💡 Demo

**Live Inference Demo Interface (HTML + JS + Flask):**

- Upload an audio file of a baby's cry.
- The model processes and classifies the cry.
- A prediction is shown with the estimated probability.

### 🧪 Example Walkthrough

1. **Upload a `.wav`, `.mp3`, `.m4a`, or `.aac` audio file**  
   _(max 25MB)_

2. **Backend Inference:**
   - Audio is transformed into a Mel spectrogram.
   - The spectrogram is passed through YAMNet or other selected models.
   - A classification label and probability are returned.

3. **Frontend Output:**
```
✅ Classification Result:
Detected: Hunger Cry (Confidence: 89%)
```

4. 🎵 **Sample Inputs**: Try uploading cries recorded from the dataset to evaluate the model prediction live.

## 🛠️ How to Run

```bash
# Clone repo
git clone https://github.com/your-user/baby-cry-classifier.git
cd baby-cry-classifier

# Setup environment
pip install -r requirements.txt

# Train models
python train_resnet18.py
python train_cnn.py

# Run demo (Flask app)
python app.py
```

## 🧪 Notebooks Provided

- `baby_classification_cnn.ipynb`: All deep learning models with training + plots
- `baby_classification_yamnet.ipynb`: YAMNet + feature extraction + final predictions

## 📈 Results Summary

- Traditional ML (SVM, XGBoost) gave:
  - SVM Accuracy: 57.7%
  - XGBoost Accuracy: 37.5%
- Deep learning with ResNet and CNN reached ~44%
- **YAMNet was most effective at 65% test accuracy**

## 🔐 Deployment Notes

- The demo UI is designed with Google Colab and Flask API endpoints.
- Uploading cry audio and predicting emotional state is seamless.
- Can be extended for mobile or IoT devices.

## 📦 Tech Stack

- PyTorch, torchvision
- scikit-learn, XGBoost
- TensorFlow Hub (YAMNet)
- Matplotlib, Seaborn
- Flask (Demo backend)
- HTML + JS (Demo frontend)
