# ------------------------------
# 1. Import Libraries
# ------------------------------
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import tensorflow as tf
import random

# ------------------------------
# 2. Load the full dataset
# ------------------------------
df = pd.read_csv("student_performance_selected.csv")  # Full 5000 rows

# ------------------------------
# 3. Features and Target
# ------------------------------
feature_columns = ['Attendance (%)', 'Midterm_Score', 'Assignments_Avg', 'Participation_Score', 'Parent_Education_Level']
X = df[feature_columns]
y = df['Final_Score'].values

# ------------------------------
# 4. Train-Test Split
# ------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ------------------------------
# 5. Feature Preprocessing: scale numeric, one-hot encode categorical
# ------------------------------
numeric_features = ['Attendance (%)', 'Midterm_Score', 'Assignments_Avg', 'Participation_Score']
categorical_features = ['Parent_Education_Level']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
    ],
    remainder='drop'
)

X_train = preprocessor.fit_transform(X_train)
X_test = preprocessor.transform(X_test)

# ------------------------------
# 6. Build Neural Network Model
# ------------------------------
# Reproducibility
seed = 42
np.random.seed(seed)
random.seed(seed)
tf.random.set_seed(seed)

model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    BatchNormalization(),
    Dropout(0.3),

    Dense(64, activation='relu'),
    BatchNormalization(),
    Dropout(0.2),

    Dense(32, activation='relu'),
    Dense(1)
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

callbacks = [
    EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, min_lr=1e-5)
]

# ------------------------------
# 7. Train the model
# ------------------------------
history = model.fit(
    X_train, y_train,
    epochs=200,
    batch_size=32,
    validation_split=0.2,
    callbacks=callbacks,
    verbose=1
)

# ------------------------------
# 8. Evaluate Model
# ------------------------------
y_pred = model.predict(X_test).flatten()

print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
print(f"MSE: {mean_squared_error(y_test, y_pred):.2f}")
print(f"R2 Score: {r2_score(y_test, y_pred):.2f}")

# ------------------------------
# 9. Predict New Student Example
# ------------------------------
# Example: Attendance=85, Midterm=44, Assignment Avg=13, Participation=9, Parent Edu=0
new_student_df = pd.DataFrame([
    {
        'Attendance (%)': 85,
        'Midterm_Score': 44,
        'Assignments_Avg': 13,
        'Participation_Score': 9,
        'Parent_Education_Level': 0
    }
])
new_student_preprocessed = preprocessor.transform(new_student_df)
predicted_score = model.predict(new_student_preprocessed).flatten()[0]
print(f"The predicted final score of the new student is: {predicted_score:.2f}")

# ------------------------------
# 10. Visualize Training Loss
# ------------------------------
plt.figure(figsize=(10,5))
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('MSE Loss')
plt.title('Training and Validation Loss')
plt.legend()
plt.grid(True)
plt.show()

# ------------------------------
# 11. Actual vs Predicted Plot
# ------------------------------
plt.figure(figsize=(6,6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'r--', label='Ideal Fit')
plt.xlabel('Actual Final Score')
plt.ylabel('Predicted Final Score')
plt.title('Neural Network Regression: Actual vs Predicted')
plt.legend()
plt.grid(True)
plt.show()
