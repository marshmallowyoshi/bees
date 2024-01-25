import pandas as pd
import numpy as np
import imblearn
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing, model_selection

def train_forest(df, verbose=False):
    bombus_df = df[['id', 'latitude', 'longitude',
                    'scientific_name', 'observed_on']]

    # limit scope
    top = bombus_df['scientific_name'].value_counts()[:20].index
    bombus_df = bombus_df[bombus_df['scientific_name'].isin(top)]

    # Date encoding

    bombus_df['observed_on'] = pd.to_datetime(bombus_df['observed_on'])
    bombus_df['observed_on'] = bombus_df['observed_on'].dt.dayofyear

    bombus_df = cyclic_encode(bombus_df, 'observed_on', 365)

    # scale locations

    min_max_scaler = preprocessing.MinMaxScaler()
    bombus_df['longitude'] = min_max_scaler.fit_transform(bombus_df[['longitude']])
    bombus_df['latitude'] = min_max_scaler.fit_transform(bombus_df[['latitude']])

    # split train and test

    train, test = model_selection.train_test_split(bombus_df, test_size=0.3, random_state=0)

    x_train = train[['longitude', 'latitude', 'observed_on_cos', 'observed_on_sin']]
    y_train = train[['scientific_name']]
    x_test = test[['longitude', 'latitude', 'observed_on_cos', 'observed_on_sin']]
    y_test = test[['scientific_name']]


    # resample

    ros = imblearn.over_sampling.RandomOverSampler(random_state=0)
    x_train, y_train = ros.fit_resample(x_train, y_train)

    rf = RandomForestClassifier(n_estimators=10, max_depth=6, random_state=0)
    rf.fit(x_train, np.ravel(y_train))

    if verbose:
        print(f'score: {rf.score(x_test, y_test)}\n')
        print(f'probabilities: {rf.predict_proba([[0.22044,  0.440961,         -0.96901,         0.247022]])}')
        print(f'prediction: {rf.predict([[0.22044,  0.440961,         -0.96901,         0.247022]])}')
    return rf, x_test, y_test

def cyclic_encode(df, col, max_val):
    df[col + '_sin'] = np.sin(2 * np.pi * df[col]/max_val)
    df[col + '_cos'] = np.cos(2 * np.pi * df[col]/max_val)
    return df

def tree_to_df(tree):
    tree_ = tree.tree_
    tree_df = pd.DataFrame(columns=['depth', 'threshold', 'feature', 'value'])
    depths = tree_.compute_node_depths()
    for idx, val in enumerate(tree_.threshold):
        if tree_.children_left[idx] == -1:
            value = [int(x) for x in tree_.value[idx][0]]
            val = pd.NA
            feature = pd.NA
        else:
            value = pd.NA
            feature = tree_.feature[idx]
        tree_df.loc[idx] = [depths[idx], val, feature, value]
    return tree_df

def forest_to_df(forest):
    return pd.concat([tree_to_df(tree) for tree in forest.estimators_], ignore_index=True)

def add_branches(tree):
    tree['branches'] = [pd.NA for x in range(len(tree))]
    for idx, row in enumerate(tree.itertuples()):
        idx += tree.index[0]
        branch_list = [x for x in tree[tree['depth'] == row.depth + 1].index.to_list() if x > idx][:2]
        if len(branch_list) == 0:
            continue
        elif branch_list[0] != idx+1:
            continue
        else:
            tree.at[idx, 'branches'] = branch_list
    return tree

def write_metadata(rf, file_name):
    largest_sample_size = int(max([max(rf.estimators_[x].tree_.value[0][0]) for x in range(len(rf.estimators_))]))
    feature_count = rf.n_features_in_
    tree_count = len(rf.estimators_)
    class_count = len(rf.classes_)
    max_depth = rf.max_depth
    classes = rf.classes_

    with open(file_name, 'w', encoding='utf-8-sig') as f:
        f.write(f'largest_sample_size: {largest_sample_size}\n')
        f.write(f'feature_count: {feature_count}\n')
        f.write(f'tree_count: {tree_count}\n')
        f.write(f'class_count: {class_count}\n')
        f.write(f'max_depth: {max_depth}\n')
        f.write('classes: ')
        for c in classes:
            f.write(f'{c}, ')
    return 0

def forest_struct_to_csv(rf, file_name):
    tree = rf.estimators_[0]
    tree_ = tree.tree_
    thresholds = tree_.threshold
    tree_df = pd.DataFrame(columns=['depth', 'threshold', 'feature', 'is_leaf', 'value'])
    depths = tree_.compute_node_depths()
    for idx, val in enumerate(thresholds):
        tree_df.loc[idx] = [depths[idx], val, tree_.feature[idx], tree_.children_left[idx] == -1, tree_.value[idx][0]]

    forest = forest_to_df(rf)

    tree_start = forest[forest['depth']==1].index.to_list()
    tree_list = []

    for idx, val in enumerate(tree_start):
        if idx == len(tree_start) - 1:
            tree_list.append(forest.loc[val:])
        else:
            tree_list.append(forest.loc[val:tree_start[idx+1]-1])

    new_tree_list = [add_branches(x) for x in tree_list]
    new_forest = pd.concat(new_tree_list, ignore_index=True)
    new_forest.to_csv("".join((file_name, '.csv')), index=False)
    write_metadata(rf, "".join((file_name, '.meta')))
    return new_forest
