# **Toxic Comment Classification**  

## **Overview**  
This project implements a **Toxic Comment Classification** system using **DistilBERT** with **Odd-Layer, Even-Layer, and LoRA Models**. It also includes a **Streamlit-based Web Interface** for user interaction.  

## **Project Components**  
### **1. `a7_main.py` - Model Training & Evaluation**  
This script handles the **data preprocessing, model training, and evaluation** using different approaches:  
- **Preprocessing:**  
  - Loads and cleans the dataset (`train.csv`, `test.csv`).  
  - Converts text to lowercase, removes special characters, and creates binary toxicity labels.  
  - Splits data into training and validation sets.  

- **Model Implementation:**  
  - **DistilBERT** is used as the base model.  
  - **Odd-layer and even-layer student models** are created.  
  - **LoRA (Low-Rank Adaptation)** is applied to the DistilBERT attention layers to improve efficiency.  
  - **Trainer API** from `Hugging Face` is used for training.  

- **Evaluation:**  
  - Model performance is measured using **classification reports** and **confusion matrices**.  

---

### **2. `app.py` - Streamlit Web Application**  
This script provides a **user-friendly interface** to classify comments as **Toxic or Non-Toxic**.  
- Uses **Streamlit** to create an interactive UI.  
- Takes user input and **predicts toxicity** using the trained model.  
- Displays classification results along with a **confidence score**.  

---

## **Installation & Setup**  
### **Requirements:**  
Ensure you have the following dependencies installed:  
```bash
pip install torch transformers pandas numpy scikit-learn streamlit loralib
```

### **Running the Model Training Script (`a7_main.py`)**  
```bash
python a7_main.py
```

### **Running the Streamlit Web App (`app.py`)**  
```bash
streamlit run app.py
```

---

## **Results & Model Performance**  
- The model was trained on **toxic comment datasets** and achieved promising results.  
- Evaluation metrics include **precision, recall, F1-score**, and a **confusion matrix**.  
- The **LoRA model** enhances efficiency while maintaining high accuracy.  

---

## **Future Improvements**  
- Optimize **hyperparameters** for better model performance.  
- Add **explainability features** to show why a comment is classified as toxic.  
- Deploy the model using **Flask/FastAPI** for production use.  

