# MACHINE LEARNING ALGORITHM FUNCTIONS USED BY MAIN.PY
# STATUS: WORKING
# LAST UPDATED: 12/06/2024


import os
import time
import logging
import traceback
import numpy as np
import pandas as pd
import tables as tb
import matplotlib.pyplot as plt
import seaborn as sb
from datetime import datetime
from itertools import compress
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import ComplementNB
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from config import columns, feature_names, gesture_names


default = False  # Enable to generate default metrics for all models using default parameters
select = False  # Enable to select which gesture to use (if false use all gestures)
gesture_selection = [0, 1, 2, 3, 4]  # indexes of selected gestures
cv_splits = 10

logger = logging.getLogger(name=__name__)


def list_table_nums(h5file: tb.File) -> list:
    """
    Get new table number based on existing tables in features group of .h5 file

    STATUS: WORKING

    : param h5file: .h5 file object
    : type h5file: File object
    : return: table number
    : rtype: integer
    """

    nodes = []
    for node in h5file:
        nodes.append(str(object=node))

    filtered_tables = list(filter(lambda x: '(Table' in x, nodes))
    if not filtered_tables:  # no groups found
        table_nums = []
    else:
        table_nums = [int((x.split(" ")[0]).split("_")[-1])for x in filtered_tables]

    return table_nums


def importData(hdfFile: str) -> pd.DataFrame:
    """
    Open file for reading and import all tables from features group

    STATUS: WORKING

    : param hdfFile: .h5 filename
    : type hdfFile: string
    : return: pandas dataframe containing all feature data
    : rtype: pd.DataFrame
    """

    if os.path.exists(path=hdfFile):
        print("Attempting to open file")
        logger.info(msg=" Attempting to open file")
        try:
            h5file = tb.open_file(filename=hdfFile, mode='r')
            print("File opened")
            logger.info(msg=" File opened")
        except:
            print("PYTABLES EXCEPTION OCCURRED!")
            logger.info(msg=" PYTABLES EXCEPTION OCCURRED!")
            print(f"IF HDF5ExtError: Most likely cause is {hdfFile} is empty")
            logger.info(msg=f" IF HDF5ExtError: Most likely cause is {hdfFile} is empty")
            print("If this is the case delete the file and restart the script\nEXITING...")
            logger.info(msg=" If this is the case delete the file and restart the script\nEXITING...")
            exit(code=1)
    else:
        print(f"Existing file not found.\nEXITING...")
        logger.info(msg=f" Existing file not found.\nEXITING...")
        exit(code=1)

    try:
        # IMPORT DATA
        print("Importing data...")
        logger.info(msg=" Importing data...")
        dataframes = []
        table_nums = list_table_nums(h5file=h5file)
        #combs = fset_combinations(table_nums=table_nums)
        for table in table_nums:
            table_name = "fset_" + str(object=table)
            nodeObject = h5file.get_node(where="/features", name=table_name)
            dataframes.append(pd.DataFrame.from_records(
                data=nodeObject.read(), columns=columns))  # type: ignore
        dataframe = pd.concat(objs=dataframes, ignore_index=True)
        dataframe = dataframe.drop(labels='timestamp', axis=1)
    except:
        print("EXCEPTION OCCURED WHILE IMPORTING DATA!\n")
        logger.info(msg=" EXCEPTION OCCURED WHILE IMPORTING DATA!\n")
        traceback.print_exc()
        logger.info(msg=f"\n{traceback.print_exc()}")
    finally:
        h5file.close()

    return dataframe


def refit_strategy(cv_results):
    """
    Define the strategy to select the best estimator.

    The strategy defined is to rank the results by recall and keep all models with one standard
    deviation of the best by recall. Once these models are selected, select the
    model with the highest recall and precision.

    STATUS: WORKING

    # Ref: https://scikit-learn.org/stable/auto_examples/model_selection/plot_grid_search_digits.html#sphx-glr-auto-examples-model-selection-plot-grid-search-digits-py

    : param cv_results: CV results as returned by the `GridSearchCV`
    : type cv_results: dict of numpy (masked) ndarrays
    : return: The index of the best estimator as it appears in `cv_results`
    : rtype: int
    """

    cv_results_ = pd.DataFrame(data=cv_results)

    cv_results_ = cv_results_[
        [
            "mean_score_time",
            "mean_test_recall_micro",
            "std_test_recall_micro",
            "mean_test_precision_micro",
            "std_test_precision_micro",
            "rank_test_recall_micro",
            "rank_test_precision_micro",
            "params",
        ]
    ]

    # Select the most performant models in terms of recall
    # (within 1 sigma from the best)
    best_recall_std = cv_results_["mean_test_recall_micro"].std()
    best_recall = cv_results_["mean_test_recall_micro"].max()
    best_recall_threshold = best_recall - best_recall_std

    high_recall_cv_results = cv_results_[cv_results_["mean_test_recall_micro"] > best_recall_threshold]
    print(f"Out of the previously selected models, we keep all the\nmodels within one standard deviation of the highest recall model:")
    logger.info(msg=f" Out of the previously selected models, we keep all the\nmodels within one standard deviation of the highest recall model:")

    for mean_precision, std_precision, mean_recall, std_recall, params in zip(
        high_recall_cv_results["mean_test_precision_micro"],
        high_recall_cv_results["std_test_precision_micro"],
        high_recall_cv_results["mean_test_recall_micro"],
        high_recall_cv_results["std_test_recall_micro"],
        high_recall_cv_results["params"],
    ):
        print(f"precision: {mean_precision:0.3f} (±{std_precision:0.03f}),\n recall: {mean_recall:0.3f} (±{std_recall:0.03f}),\n for {params}")
        logger.info(msg=f" precision: {mean_precision:0.3f} (±{std_precision:0.03f}),\n recall: {mean_recall:0.3f} (±{std_recall:0.03f}),\n for {params}")
    print()

    # From the best candidates, select the model with the highest precision and recall
    precision_recall_summation_results = pd.DataFrame(data=high_recall_cv_results['mean_test_precision_micro'] + high_recall_cv_results['mean_test_recall_micro'], columns=['precision_recall_summation'])
    top_recall_and_precision_index = precision_recall_summation_results['precision_recall_summation'].idxmax()

    print(f"\nThe selected final model is the one with the highest recall and precision.\nSelected Model:\n{high_recall_cv_results.loc[top_recall_and_precision_index]}")
    logger.info(msg=f" \nThe selected final model is the one with the highest recall and precision.\nSelected Model:\n{high_recall_cv_results.loc[top_recall_and_precision_index]}")

    return top_recall_and_precision_index


def displayMetrics(y_test, y_pred, gestures: list, class_distribution: list, cmap: str, logger) -> None:
    """
    Compute and display the Confusion matrix and classification report

    STATUS: WORKING

    # Ref: https://scikit-learn.org/stable/modules/model_evaluation.html
    # Ref: https://medium.com/@dtuk81/confusion-matrix-visualization-fc31e3f30fea
    # Ref: https://sejal-kshirsagar.medium.com/6-tips-to-customize-seaborn-heatmaps-881207a61723

    : param y_test: model grounds
    : type y_test: np.array
    : param y_pred: model predictions
    : type y_pred: np.array
    : param gestures: list of gestures
    : type gestures: list
    : param class_distribution: number of ground/predictions for each class
    : type class_distribution: list
    : return: None
    : rtype: None
    """

    cm = confusion_matrix(y_true=y_test, y_pred=y_pred)
    plt.figure(figsize=(6, 6))
    sb.heatmap(data=cm/class_distribution[0], annot=True, cmap=cmap,
               cbar=False, xticklabels=gestures, yticklabels=gestures)
    plt.xlabel(xlabel="Predicted label")
    plt.ylabel(ylabel="True label")
    plt.title(label=f"Confusion Matrix {class_distribution}")
    plt.show()

    # Compute and display metrics
    report = classification_report(y_true=y_test, y_pred=y_pred)
    print(report)
    logger.info(msg=f"\n{report}")
    
    # Compute and display accuracy
    accuracy = accuracy_score(y_true=y_test, y_pred=y_pred, normalize=True)*100.0  # as percentage
    print(f"Overall Accuracy: {accuracy}%")
    logger.info(msg=f' Overall Accuracy {accuracy}%')


def classifyFeatureData(hdfFile: str, test_split: float) -> None:
    """
    - Import, Select, Split, and Normalize Data
    - Train, Optimise, and Test Classification Models
    - Display Final Model Parameters and Metrics

    STATUS: WORKING

    SVM: https://blog.paperspace.com/implementing-support-vector-machine-in-python-using-sklearn/
    Ref: https://stackoverflow.com/questions/27918990/how-do-you-read-a-pytables-table-into-a-pandas-dataframe

    : param hdfFile: .h5 filename
    : type hdfFile: string
    : param test_split: percentage split of data for testing
    : type test_split: float
    : return: None
    : rtype: None
    """

    method_str = 'dft' if default == True else 'opt'
    select_str = '_gsel_' if select == True else '_'
    datetime_str = datetime.now().strftime("%d_%m_%Y-%H_%M")
    filename = method_str + select_str + 'class_log_' + datetime_str + '.log'
    logging.basicConfig(filename=filename, level=logging.INFO)
    logger.info(msg=' Started')

    try:
        # IMPORT DATA
        imported_data = importData(hdfFile=hdfFile)

        # SELECT DATA
        if select == True:  # selection of gestures
            logger.info(msg=" select flag enabled")
            logger.info(msg=f" Gestures Selected {[gesture_names[g] for g in gesture_selection]}")
            dataframes = []
            for l in gesture_selection:
                dataframes.append(imported_data.loc[imported_data['label'] == l])
            dataframe = pd.concat(objs=dataframes, axis=0, ignore_index=True)
            gesture_indexes = gesture_selection
            gestures = [gesture_names[i] for i in gesture_indexes]
        else:  # all gestures
            dataframe = imported_data
            gestures = gesture_names
            gesture_indexes = list(np.arange(start=0, stop=len(gestures), step=1))

        # TRANSFORM DATA
        dataframe_X = dataframe.drop(labels='label', axis=1)
        dataframe_y = dataframe['label']
        X = dataframe_X.to_numpy(dtype=np.float16)
        y = dataframe_y.to_numpy(dtype=np.int8)

        # NORMALIZE DATA
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_X = scaler.fit_transform(X=X)

        # SPLIT DATA
        X_train, X_test, y_train, y_test = train_test_split(scaled_X, y, test_size=test_split, random_state=0, stratify=y)
        class_distribution = []
        for g in gesture_indexes:
            count = 0
            for y in y_test:
                if y == g:
                    count += 1
            class_distribution.append(count)
        print(f"No. Training Samples: {X_train.shape[0]}")
        logger.info(msg=f" No. Training Samples: {X_train.shape[0]}")
        print(f"No. Testing Samples: {y_test.shape[0]}")
        logger.info(msg=f" No. Testing Samples: {y_test.shape[0]}")
        print(f"Test Set, Class Sample Distribution: {class_distribution}")
        logger.info(msg=f" Test Set, Class Sample Distribution: {class_distribution}")

        if default == True:
            logger.info(msg=" default flag enabled")
            # DEFAULT SVM MODEL & PARAMETERS
            svm = SVC()
            try:
                svm.fit(X=X_train, y=y_train)
                svm_y_pred = svm.predict(X=X_test)
            except:
                print("EXCEPTION OCCURRED DURING FITTING OF DEFAULT SVM MODEL!")
                logger.info(msg="EXCEPTION OCCURRED DURING FITTING OF DEFAULT SVM MODEL!")
                traceback.print_exc()
                logger.info(msg=f"\n{traceback.print_exc()}")

            # DEFAULT SVM PERFORMANCE METRICS
            logger.info(msg=" SVM Default")
            displayMetrics(y_test=y_test, y_pred=svm_y_pred, gestures=gestures, class_distribution=class_distribution, cmap='Reds', logger=logger)

            # DEFAULT KNN MODEL & PARAMETERS
            knn = KNeighborsClassifier()
            try:
                knn.fit(X=X_train, y=y_train)
                knn_y_pred = knn.predict(X=X_test)
            except:
                print("EXCEPTION OCCURRED DURING FITTING OF DEFAULT KNN MODEL!")
                logger.info(msg="EXCEPTION OCCURRED DURING FITTING OF DEFAULT KNN MODEL!")
                traceback.print_exc()
                logger.info(msg=f"\n{traceback.print_exc()}")

            # DEFAULT KNN PERFORMANCE METRICS
            logger.info(msg=" KNN Default")
            displayMetrics(y_test=y_test, y_pred=knn_y_pred, gestures=gestures, class_distribution=class_distribution, cmap='Greens', logger=logger)

            # DEFAULT CNB MODEL & PARAMETERS
            cnb = ComplementNB()
            try:
                cnb.fit(X=X_train, y=y_train)
                cnb_y_pred = cnb.predict(X=X_test)
            except:
                print("EXCEPTION OCCURRED DURING FITTING OF DEFAULT CNB MODEL!")
                logger.info(msg="EXCEPTION OCCURRED DURING FITTING OF DEFAULT CNB MODEL!")
                traceback.print_exc()
                logger.info(msg=f"\n{traceback.print_exc()}")

            # DEFAULT CNB PERFORMANCE METRICS
            logger.info(msg=" CNB Default")
            displayMetrics(y_test=y_test, y_pred=cnb_y_pred, gestures=gestures, class_distribution=class_distribution, cmap='Blues', logger=logger)
        else:
            # FEATURE SELECTION + PARALLEL MODEL SELECTION & HYPERPARAMETER TUNING
            logger.info(msg=" Optimised Process")
            X_train_dataframe = pd.DataFrame(data=X_train, columns=feature_names, dtype=np.float16)
            X_test_dataframe = pd.DataFrame(data=X_test, columns=feature_names, dtype=np.float16)
            selector = SequentialFeatureSelector(estimator=SVC(), n_features_to_select=3, direction='forward')
            feature_pipe = Pipeline(memory=None, steps=[('selector', selector), ('classifier', SVC())], verbose=True)
            scores = ['precision_micro', 'recall_micro']
            feature_search_space = [{'selector__estimator': [SVC(), KNeighborsClassifier(), ComplementNB()],
                                     'selector__n_features_to_select': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                                     'selector__direction': ['forward', 'backward']}]
            feature_grid_search = GridSearchCV(estimator=feature_pipe, param_grid=feature_search_space, scoring=scores, refit=refit_strategy, cv=cv_splits, verbose=2)
            try:
                start = time.time()
                feature_grid_search.fit(X=X_train_dataframe, y=y_train)
                end = round(number=(time.time() - start)/60.0, ndigits=None)
            except:
                print("EXCEPTION OCCURRED WHILE PERFORMING FEATURE SELECTION!")
                logger.info(msg="EXCEPTION OCCURRED WHILE PERFORMING FEATURE SELECTION!")
                traceback.print_exc()
                logger.info(msg=f"\n{traceback.print_exc()}")
            selected_features = list(compress(data=feature_names, selectors=feature_grid_search.best_estimator_.named_steps['selector'].get_support()))
            print(f"\nFeature Selection Duration: ~{end} minutes\n")
            logger.info(msg=f" Feature Selection Duration: ~{end} minutes")
            print(f"\nOptimal Features: {selected_features}\n")
            logger.info(msg=f" Optimal Features: {selected_features}")

            opt_X_train = X_train_dataframe[selected_features]
            opt_X_test = X_test_dataframe[selected_features]
            parameter_pipe = Pipeline(memory=None, steps=[('classifier', SVC())], verbose=True)
            parameter_search_space = [{'classifier': [SVC()],
                                       'classifier__C': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0],
                                       'classifier__kernel': ['rbf', 'linear'],
                                       'classifier__gamma': ['scale', 'auto', 1e-3, 1e-4],
                                       'classifier__decision_function_shape': ['ovr', 'ovo']},
                                       {'classifier': [KNeighborsClassifier()],
                                       'classifier__n_neighbors': [1, 3, 5, 7, 9, 11, 13, 15],
                                       'classifier__weights': ['uniform', 'distance'],
                                       'classifier__algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
                                       'classifier__leaf_size': [10, 20, 30, 40, 50],
                                       'classifier__p': [1, 2],
                                       'classifier__metric': ['minkowski']},
                                       {'classifier': [ComplementNB()],
                                        'classifier__alpha': [1e-3, 1e-2, 1e-1, 1.0]}]
            grid_search = GridSearchCV(estimator=parameter_pipe, param_grid=parameter_search_space, scoring=scores, refit=refit_strategy, cv=cv_splits, verbose=2)
            try:
                start = time.time()
                grid_search.fit(X=opt_X_train, y=y_train)
                end = round(number=(time.time() - start)/60.0, ndigits=None)
                y_pred = grid_search.predict(X=opt_X_test)
            except:
                print("EXCEPTION OCCURRED DURING FITTING OF OPTIMAL MODEL!")
                logger.info(msg="EXCEPTION OCCURRED DURING FITTING OF OPTIMAL MODEL!")
                traceback.print_exc()
                logger.info(msg=f"\n{traceback.print_exc()}")
            print(f"\nModel + Hyperparameter Selection Duration: ~{end} minutes\n")
            logger.info(msg=f" Model + Hyperparameter Selection Duration: ~{end} minutes")
            print(f"\nBest estimator: {grid_search.best_estimator_}\n")
            logger.info(msg=f" Best estimator: {grid_search.best_estimator_}")
            print(f"\nBest params: {grid_search.best_estimator_.get_params()}\n")
            logger.info(msg=f" Best params: {grid_search.best_estimator_.get_params()}")

            # BEST MODEL PERFORMANCE METRICS
            displayMetrics(y_test=y_test, y_pred=y_pred, gestures=gestures, class_distribution=class_distribution, cmap='Purples', logger=logger)

        logger.info(msg=" Finished")
        print("DONE.")
        print("EXITING...")
    except:
        print("EXCEPTION OCCURED WHILE PERFORMING CLASSIFICATION!\n")
        logger.info(msg=" EXCEPTION OCCURED WHILE PERFORMING CLASSIFICATION!\n")
        traceback.print_exc()
        logger.info(msg=f"\n{traceback.print_exc()}")
