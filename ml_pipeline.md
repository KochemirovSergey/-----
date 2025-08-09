flowchart TD
    A[Сырые ряды и региональные данные] --"Методы: Интерполяция (линейная, полиномиальная),<br/>Kalman filter, KNN-imputation, Байесовские модели<br/>Инструменты: scikit-learn, statsmodels, PyMC"--> B[Обработка пропущенных значений]
    
    B --"Методы: Bottom-up/Top-down reconciliation,<br/>Padding, Truncation<br/>Инструменты: HierarchicalForecast, Custom padding functions"--> C[Агрегация и нормализация рядов]
    
    C --"Методы: Лаги, средние, сезонность, внешние регрессоры<br/>Инструменты: tsfresh, sktime, FRED API"--> D[Инженерия признаков]
    
    D --"Методы: BSTS (байес. модели), LightGBM, LSTM/NN, ARIMA, Prophet<br/>Инструменты: PyMC, bsts (R), LightGBM, PyTorch, statsmodels"--> E[Обучение моделей]
    
    E --"Методы: Стекинг, взвешенное усреднение, Bayesian Model Averaging (BMA)<br/>Инструменты: scikit-learn, PyMC, XGBoost"--> F[Ансамблирование моделей]
    
    F --"Методы: Time Series Cross-Validation, Bayesian Optimization<br/>Инструменты: sktime, Optuna, scikit-optimize"--> G[Валидация и оптимизация]
    
    G --"Методы: Модельное развертывание, мониторинг<br/>Инструменты: MLflow, Docker, Kubernetes"--> H[Продакшн/Деплой]
    
    H --> I[Реальный прогноз]
