# import pandas as pd
# import sklearn
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
# import matplotlib.pyplot as plt
# le = LabelEncoder()
# df = pd.read_csv('MLMachineFiles.csv')
# df["Warranty Status"] = le.fit_transform(df["Warranty Status"])
# df["Company"] = le.fit_transform(df["Company"])

# X = df[["Days Since Servicing", "Warranty Status", "Days Since Purchase", "Company"]]
# y = df["Status"]

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=49)

# serviceModel = RandomForestClassifier()
# serviceModel.fit(X_train, y_train)
