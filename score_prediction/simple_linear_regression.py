# ------------------------------
# 1. Import libraries
# ------------------------------
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt

# ------------------------------
# 2. Load dataset
# ------------------------------
df = pd.read_csv("student_performance_selected.csv")  # 5000 rows

# ------------------------------
# 3. Features and Target
# ------------------------------
X = df[['Attendance (%)', 'Midterm_Score', 'Assignments_Avg', 'Participation_Score', 'Parent_Education_Level']]
y = df['Final_Score']

# ------------------------------
# 4. Train-Test Split
# ------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ------------------------------
# 5. Feature Scaling
# ------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ------------------------------
# 6. Build and Train Linear Regression Model
# ------------------------------
model = LinearRegression()
model.fit(X_train_scaled, y_train)

# ------------------------------
# 7. Make Predictions
# ------------------------------
y_pred = model.predict(X_test_scaled)

# ------------------------------
# 8. Evaluate Model
# ------------------------------
print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
print(f"MSE: {mean_squared_error(y_test, y_pred):.2f}")
print(f"R2 Score: {r2_score(y_test, y_pred):.2f}")

# ------------------------------
# 9. Predict a New Student
# ------------------------------
new_student = [[85, 44, 13, 9, 0]]  # Example: Attendance, Midterm, Assignments, Participation, Parent Edu
new_student_scaled = scaler.transform(new_student)
predicted_score = model.predict(new_student_scaled)[0]
print(f"The predicted final score of the new student is: {predicted_score:.2f}")

# ------------------------------
# 10. Visualize Actual vs Predicted
# ------------------------------
plt.figure(figsize=(6,6))
plt.scatter(y_test, y_pred, alpha=0.5, color='blue')
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'r--', label='Ideal Fit')
plt.xlabel('Actual Final Score')
plt.ylabel('Predicted Final Score')
plt.title('Linear Regression: Actual vs Predicted')
plt.legend()
plt.grid(True)
plt.show()
