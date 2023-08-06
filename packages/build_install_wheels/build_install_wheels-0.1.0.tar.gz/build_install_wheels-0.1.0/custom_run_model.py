import argparse
import json
import os
import pickle
from pathlib import Path
from typing import Tuple

import pandas as pd
from numpy.core.multiarray import ndarray

from build_install_wheels import install_requirements


def resolve_params() -> Tuple[str, str, str, str]:
    """
    train model receive five parameters:
    trained_model_path: trained model file path
    test_data_path: csv data file for testing
    model_config_file: model config file indicating feature and label name
    output_scored_model: scored model csv data file, containing prediction result
    output_scored_model_config: indicating label and prediction column name
    :return:
    """
    parser = argparse.ArgumentParser(description='Argument for running model')
    parser.add_argument('--test_data_path', type=str, required=True)
    parser.add_argument('--model_config_file', type=str, required=True)
    parser.add_argument('--output_scored_model', type=str, required=True)
    parser.add_argument('--output_scored_model_config', type=str, required=True)
    args = parser.parse_args()
    return args.test_data_path, args.model_config_file, args.output_scored_model, args.output_scored_model_config


def reload_run_save_result(test_data_path, model_config_file, output_scored_model,
                           output_scored_model_config):
    """
   1, given trained model path, reload it.
   2. separate features and label
   3. use features to predict result
   4. concat features, label and prediction
   5. save file to csv and model config
   :param test_data_path: test file to evaluate
   :param model_config_file: config file indicating feature and label names
   :param output_scored_model: output csv data file
   :param output_scored_model_config: scored model's prediction and label name
   :return:
   """
    install_requirements(os.path.dirname(model_config_file))
    trained_model_path = _extract_trained_model_path(model_config_file)
    model = reload_model(trained_model_path)
    features, label, label_name = select_features_label(test_data_path, model_config_file)
    predict_label_name = f'predict_{label_name}'
    label_predict = pd.Series(score_model(model, features), index=features.index) \
        .apply(lambda x: '%.3f' % x) \
        .to_frame(predict_label_name)
    res = pd.concat([features, label, label_predict], axis=1)  # type: pd.DataFrame

    # create directory if not exists
    Path(os.path.dirname(output_scored_model)).mkdir(parents=True, exist_ok=True)
    res.to_csv(output_scored_model)
    save_scored_model_config(model_config_file, predict_label_name, output_scored_model_config)


def _extract_trained_model_path(model_config_file: str):
    dir_name = os.path.dirname(model_config_file)
    with open(model_config_file, 'r') as f:
        config = json.load(f)
        return os.path.join(dir_name, config['model_file_name'])


def reload_model(path: str):
    with open(path, 'rb') as f:
        data = f.read()
        return pickle.loads(data)


def select_features_label(test_data_path: str, model_config_file: str):
    feature_names, label_name = _extract_feature_and_label_names(model_config_file)
    test_data = pd.read_csv(test_data_path)
    return test_data[list(feature_names)], test_data[list([label_name])], label_name


def score_model(model, feature_test: pd.DataFrame) -> ndarray:
    label_predict = model.predict(feature_test)
    return label_predict


def _extract_feature_and_label_names(model_config_file: str):
    try:
        with open(model_config_file, 'r') as f:
            config = json.load(f)
            feature_names = [feature[0] for feature in config['feature_names']]
            return feature_names, config['label_name']
    except FileNotFoundError or KeyError as e:
        print(f'exception occurred with: {e}')


def save_scored_model_config(model_config_file: str, predict_label_name: str, output_config_file: str):
    # create directory if not exists
    Path(os.path.dirname(model_config_file)).mkdir(parents=True, exist_ok=True)

    with open(model_config_file, 'r') as f:
        config = json.load(f)
        config['predict_label_name'] = predict_label_name
        with open(output_config_file, 'w') as scored_config_file:
            json.dump(config, scored_config_file, indent=2)


if __name__ == '__main__':

    # --test_data_path=./../inputs/test.csv --model_config_file=./../inputs/model_config.json
    # --output_scored_model=./../outputs/scored_model.csv
    # --output_scored_model_config=./../outputs/scored_model_config.json
    params = resolve_params()
    reload_run_save_result(*params)
