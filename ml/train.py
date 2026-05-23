import pandas as pd
import numpy as np
import sys
import os
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from label_engineering import load_and_clean, engineer_features, generate_labels, get_feature_columns

print("=" * 55)
print("STEP 1: LOADING AND PREPARING DATA")
print("=" * 55)
df = load_and_clean('ml/dataset/ev_charging_data.csv')
df = engineer_features(df)
df = generate_labels(df)
print(f"Loaded            : {len(df)} rows")
print(f"Label distribution:")
print(df['anomaly_type'].value_counts())

print("\n" + "=" * 55)
print("STEP 2: BALANCING CLASSES")
print("=" * 55)

FEATURES = get_feature_columns()

caps = {
    'burst_pattern': 5000,
    'normal':        5000,
    'ghost_session': 3000,
    'idle_abuse':    200,
    'energy_spike':  200,
    'dos_attack':    200,
}

samples = []
for anomaly_type, group in df.groupby('anomaly_type'):
    cap = caps.get(anomaly_type, len(group))
    if len(group) < cap:
        sampled = group.sample(cap, replace=True, random_state=42)
    else:
        sampled = group.sample(cap, replace=False, random_state=42)
    samples.append(sampled)

df_sample = pd.concat(samples).reset_index(drop=True)
print(f"Balanced sample   : {len(df_sample)} rows")
print(df_sample['anomaly_type'].value_counts())

X = df_sample[FEATURES].fillna(0)
y = df_sample['anomaly_type']

le = LabelEncoder()
y_encoded = le.fit_transform(y)
print(f"\nClasses           : {le.classes_.tolist()}")
print(f"Feature count     : {X.shape[1]}")

print("\n" + "=" * 55)
print("STEP 3: TRAIN / TEST SPLIT (80/20)")
print("=" * 55)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded,
)
print(f"Train rows        : {len(X_train)}")
print(f"Test rows         : {len(X_test)}")

scaler = StandardScaler()
scaler.fit(X_train)

print("\n" + "=" * 55)
print("STEP 4: TRAINING MODELS")
print("=" * 55)

models = {
    'Random Forest': {
        'model': RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=30,
            min_samples_leaf=15,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1,
        ),
    },
    'Decision Tree': {
        'model': DecisionTreeClassifier(
            max_depth=8,
            min_samples_split=30,
            min_samples_leaf=15,
            class_weight='balanced',
            random_state=42,
        ),
    },
}

results = {}

for name, config in models.items():
    print(f"\nTraining {name}...")
    model = config['model']
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc      = accuracy_score(y_test, y_pred)
    f1_w     = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)

    cv_scores = cross_val_score(
        model, X_train, y_train,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring='f1_macro',
        n_jobs=-1,
    )

    results[name] = {
        'model':       model,
        'predictions': y_pred,
        'accuracy':    acc,
        'f1_weighted': f1_w,
        'f1_macro':    f1_macro,
        'cv_mean':     cv_scores.mean(),
        'cv_std':      cv_scores.std(),
    }

    print(f"  Accuracy        : {acc * 100:.2f}%")
    print(f"  F1 Weighted     : {f1_w * 100:.2f}%")
    print(f"  F1 Macro        : {f1_macro * 100:.2f}%")
    print(f"  CV F1 Macro     : {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")

print("\n" + "=" * 55)
print("STEP 5: SAVING CHARTS")
print("=" * 55)

os.makedirs('ml/eda_charts', exist_ok=True)
model_names = list(results.keys())

# chart 1 — model comparison
accuracies  = [results[m]['accuracy']    * 100 for m in model_names]
f1_weighted = [results[m]['f1_weighted'] * 100 for m in model_names]
f1_macros   = [results[m]['f1_macro']    * 100 for m in model_names]
cv_means    = [results[m]['cv_mean']     * 100 for m in model_names]

x     = np.arange(len(model_names))
width = 0.2

plt.figure(figsize=(12, 6))
plt.bar(x - 1.5*width, accuracies,  width, label='Accuracy',    color='#3498db', edgecolor='black', linewidth=0.5)
plt.bar(x - 0.5*width, f1_weighted, width, label='F1 Weighted', color='#2ecc71', edgecolor='black', linewidth=0.5)
plt.bar(x + 0.5*width, f1_macros,   width, label='F1 Macro',    color='#e74c3c', edgecolor='black', linewidth=0.5)
plt.bar(x + 1.5*width, cv_means,    width, label='CV F1 Macro', color='#9b59b6', edgecolor='black', linewidth=0.5)

for i, (acc, f1w, f1m, cv) in enumerate(zip(accuracies, f1_weighted, f1_macros, cv_means)):
    for offset, val in zip([-1.5, -0.5, 0.5, 1.5], [acc, f1w, f1m, cv]):
        plt.text(i + offset * width, val + 0.5, f'{val:.1f}', ha='center', va='bottom', fontsize=8)

plt.xlabel('Model')
plt.ylabel('Score (%)')
plt.title('Model Comparison — All Metrics', fontsize=14)
plt.xticks(x, model_names)
plt.legend()
plt.ylim(0, 115)
plt.tight_layout()
plt.savefig('ml/eda_charts/model_comparison.png', dpi=150)
plt.close()
print("Saved: model_comparison.png")

# chart 2 — confusion matrices
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for i, (name, result) in enumerate(results.items()):
    cm = confusion_matrix(y_test, result['predictions'])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=le.classes_, yticklabels=le.classes_, ax=axes[i])
    axes[i].set_title(f'{name}\nAcc: {result["accuracy"]*100:.1f}%  F1: {result["f1_macro"]*100:.1f}%', fontsize=11)
    axes[i].set_ylabel('Actual')
    axes[i].set_xlabel('Predicted')
    axes[i].tick_params(axis='x', rotation=30)
plt.suptitle('Confusion Matrices', fontsize=14)
plt.tight_layout()
plt.savefig('ml/eda_charts/confusion_matrices.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: confusion_matrices.png")

# chart 3 — per class f1
class_names = le.classes_
n_classes   = len(class_names)
class_f1s   = {}
for name, result in results.items():
    report = classification_report(y_test, result['predictions'],
                                   target_names=class_names, output_dict=True, zero_division=0)
    class_f1s[name] = [report[c]['f1-score'] for c in class_names]

plt.figure(figsize=(12, 6))
x     = np.arange(n_classes)
width = 0.3
colors = ['#3498db', '#e74c3c']
for i, (name, f1s) in enumerate(class_f1s.items()):
    offset = (i - len(class_f1s) / 2) * width
    plt.bar(x + offset, f1s, width, label=name, color=colors[i],
            edgecolor='black', linewidth=0.5, alpha=0.85)
plt.xlabel('Anomaly Type')
plt.ylabel('F1 Score')
plt.title('Per-Class F1 Score', fontsize=14)
plt.xticks(x, class_names, rotation=20, ha='right')
plt.legend()
plt.ylim(0, 1.15)
plt.tight_layout()
plt.savefig('ml/eda_charts/per_class_f1.png', dpi=150)
plt.close()
print("Saved: per_class_f1.png")

# chart 4 — feature importance
rf     = results['Random Forest']['model']
imp_df = pd.DataFrame({'feature': FEATURES, 'importance': rf.feature_importances_}).sort_values('importance', ascending=True)
plt.figure(figsize=(10, 8))
bars = plt.barh(imp_df['feature'], imp_df['importance'], color='#3498db', edgecolor='black', linewidth=0.5)
for bar, val in zip(bars, imp_df['importance']):
    plt.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2, f'{val:.3f}', va='center', fontsize=8)
plt.xlabel('Importance Score')
plt.title('Random Forest — Feature Importances', fontsize=14)
plt.tight_layout()
plt.savefig('ml/eda_charts/feature_importance.png', dpi=150)
plt.close()
print("Saved: feature_importance.png")

# chart 5 — cross validation
plt.figure(figsize=(8, 5))
cv_means_vals = [results[m]['cv_mean'] * 100 for m in model_names]
cv_stds_vals  = [results[m]['cv_std']  * 100 for m in model_names]
bars = plt.bar(model_names, cv_means_vals, color='#9b59b6',
               edgecolor='black', linewidth=0.5, alpha=0.85,
               yerr=cv_stds_vals, capsize=5)
for bar, val in zip(bars, cv_means_vals):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
             f'{val:.1f}%', ha='center', va='bottom', fontsize=10)
plt.xlabel('Model')
plt.ylabel('CV F1 Macro (%)')
plt.title('5-Fold Cross Validation F1 Macro', fontsize=14)
plt.ylim(0, 115)
plt.tight_layout()
plt.savefig('ml/eda_charts/cross_validation.png', dpi=150)
plt.close()
print("Saved: cross_validation.png")

print("\n" + "=" * 55)
print("STEP 6: SELECTING AND SAVING BEST MODEL")
print("=" * 55)

best_name   = max(results, key=lambda m: results[m]['cv_mean'])
best_result = results[best_name]

print(f"Best model        : {best_name}")
print(f"CV F1 Macro       : {best_result['cv_mean']*100:.2f}% ± {best_result['cv_std']*100:.2f}%")
print(f"Test Accuracy     : {best_result['accuracy']*100:.2f}%")
print(f"Test F1 Macro     : {best_result['f1_macro']*100:.2f}%")
print(f"\nFull classification report:")
print(classification_report(y_test, best_result['predictions'], target_names=le.classes_, zero_division=0))

os.makedirs('ml/models', exist_ok=True)
joblib.dump(best_result['model'], 'ml/models/best_model.pkl')
joblib.dump(le,                   'ml/models/label_encoder.pkl')
joblib.dump(scaler,               'ml/models/scaler.pkl')

metadata = {
    'best_model':    best_name,
    'features':      FEATURES,
    'classes':       le.classes_.tolist(),
    'test_accuracy': round(best_result['accuracy']    * 100, 2),
    'test_f1_macro': round(best_result['f1_macro']    * 100, 2),
    'cv_f1_macro':   round(best_result['cv_mean']     * 100, 2),
    'cv_f1_std':     round(best_result['cv_std']      * 100, 2),
    'all_models': {
        name: {
            'accuracy':    round(r['accuracy']    * 100, 2),
            'f1_weighted': round(r['f1_weighted'] * 100, 2),
            'f1_macro':    round(r['f1_macro']    * 100, 2),
            'cv_f1_macro': round(r['cv_mean']     * 100, 2),
            'cv_f1_std':   round(r['cv_std']      * 100, 2),
        }
        for name, r in results.items()
    },
}

with open('ml/models/model_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\nSaved: ml/models/best_model.pkl        ({best_name})")
print("Saved: ml/models/label_encoder.pkl")
print("Saved: ml/models/scaler.pkl")
print("Saved: ml/models/model_metadata.json")
print("\n✅ ML pipeline complete. Ready for backend.")