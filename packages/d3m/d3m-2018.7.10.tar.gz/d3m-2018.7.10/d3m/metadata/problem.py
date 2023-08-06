import json
import typing

from . import base
from d3m import exceptions, utils

__all__ = ('TaskType', 'TaskSubtype', 'PerformanceMetric', 'parse_problem_description')

# Comma because we unpack the list of validators returned from "load_schema_validators".
PROBLEM_SCHEMA_VALIDATOR, = utils.load_schema_validators(base.SCHEMAS_PATH, base.DEFINITIONS_JSON, ('problem.json',))

PROBLEM_SCHEMA_VERSION = 'https://metadata.datadrivendiscovery.org/schemas/v0/problem.json'

D3M_SUPPORTED_VERSIONS = {'3.0', '3.1', '3.1.1', '3.1.2'}


class TaskTypeBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            'classification': cls.CLASSIFICATION,  # type: ignore
            'regression': cls.REGRESSION,  # type: ignore
            'clustering': cls.CLUSTERING,  # type: ignore
            'linkPrediction': cls.LINK_PREDICTION,  # type: ignore
            'vertexNomination': cls.VERTEX_NOMINATION,  # type: ignore
            'communityDetection': cls.COMMUNITY_DETECTION,  # type: ignore
            'graphClustering': cls.GRAPH_CLUSTERING,  # type: ignore
            'graphMatching': cls.GRAPH_MATCHING,  # type: ignore
            'timeSeriesForecasting': cls.TIME_SERIES_FORECASTING,  # type: ignore
            'collaborativeFiltering': cls.COLLABORATIVE_FILTERING,  # type: ignore
            'objectDetection': cls.OBJECT_DETECTION,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'TaskTypeBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        TaskType
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))


TaskType = utils.create_enum_from_json_schema_enum(
    'TaskType', base.DEFINITIONS_JSON,
    'definitions.problem.properties.task_type.oneOf[*].enum[*]',
    module=__name__, base_class=TaskTypeBase,
)


class TaskSubtypeBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            None: cls.NONE,  # type: ignore
            'binary': cls.BINARY,  # type: ignore
            'multiClass': cls.MULTICLASS,  # type: ignore
            'multiLabel': cls.MULTILABEL,  # type: ignore
            'univariate': cls.UNIVARIATE,  # type: ignore
            'multivariate': cls.MULTIVARIATE,  # type: ignore
            'overlapping': cls.OVERLAPPING,  # type: ignore
            'nonOverlapping': cls.NONOVERLAPPING,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'TaskSubtypeBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        TaskSubtype
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))


TaskSubtype = utils.create_enum_from_json_schema_enum(
    'TaskSubtype', base.DEFINITIONS_JSON,
    'definitions.problem.properties.task_subtype.oneOf[*].enum[*]',
    module=__name__, base_class=TaskSubtypeBase,
)


class PerformanceMetricBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            'accuracy': cls.ACCURACY,  # type: ignore
            'precision': cls.PRECISION,  # type: ignore
            'recall': cls.RECALL,  # type: ignore
            'f1': cls.F1,  # type: ignore
            'f1Micro': cls.F1_MICRO,  # type: ignore
            'f1Macro': cls.F1_MACRO,  # type: ignore
            'rocAuc': cls.ROC_AUC,  # type: ignore
            'rocAucMicro': cls.ROC_AUC_MICRO,  # type: ignore
            'rocAucMacro': cls.ROC_AUC_MACRO,  # type: ignore
            'meanSquaredError': cls.MEAN_SQUARED_ERROR,  # type: ignore
            'rootMeanSquaredError': cls.ROOT_MEAN_SQUARED_ERROR,  # type: ignore
            'rootMeanSquaredErrorAvg': cls.ROOT_MEAN_SQUARED_ERROR_AVG,  # type: ignore
            'meanAbsoluteError': cls.MEAN_ABSOLUTE_ERROR,  # type: ignore
            'rSquared': cls.R_SQUARED,  # type: ignore
            'normalizedMutualInformation': cls.NORMALIZED_MUTUAL_INFORMATION,  # type: ignore
            'jaccardSimilarityScore': cls.JACCARD_SIMILARITY_SCORE,  # type: ignore
            'precisionAtTopK': cls.PRECISION_AT_TOP_K,  # type: ignore
            'objectDetectionAP': cls.OBJECT_DETECTION_AVERAGE_PRECISION,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'PerformanceMetricBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        PerformanceMetric
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))

    def applicability_to_targets(self) -> bool:
        """
        Returns ``True`` if this metric is computed over all targets and not per target.

        Based on the return value one should pass or just a column with one target
        predictions (when ``False``) or a table with predictions for all targets (when ``True``)
        to the metric function for its ``y_true`` and ``y_pred`` arguments.

        Returns
        -------
        bool
            ``True`` if the metric applies to the set of all the target predictions.
        """

        return self in {self.ROOT_MEAN_SQUARED_ERROR_AVG}  # type: ignore

    def get_function(self) -> typing.Callable[..., float]:
        """
        Returns a function suitable for computing this metric.

        Some functions get extra parameters which should be provided as keyword arguments.

        Returns
        -------
        function
            A function with (y_true, y_pred, **kwargs) signature, returning float.
        """

        # Importing here to prevent import cycle.
        from d3m import metrics

        if self not in metrics.functions_map:
            raise exceptions.NotSupportedError("Computing metric {metric} is not supported.".format(metric=self))

        return metrics.functions_map[self]  # type: ignore


PerformanceMetric = utils.create_enum_from_json_schema_enum(
    'PerformanceMetric', base.DEFINITIONS_JSON,
    'definitions.problem.properties.performance_metrics.items.oneOf[*].properties.metric.enum[*]',
    module=__name__, base_class=PerformanceMetricBase,
)


def parse_problem_description(problem_doc_path: str) -> dict:
    """
    Parses problem description according to ``problem.json`` metadata schema.

    It parses constants to enums when suitable.

    Parameters
    ----------
    problem_doc_path : str
        File path to the problem description (``problemDoc.json``).

    Returns
    -------
    dict
        A parsed problem description.
    """

    with open(problem_doc_path, 'r') as problem_doc_file:
        problem_doc = json.load(problem_doc_file)

    if problem_doc.get('about', {}).get('problemSchemaVersion', None) not in D3M_SUPPORTED_VERSIONS:
        raise exceptions.NotSupportedVersionError("Only supporting problem descriptions whose schema version is among {versions}.".format(versions=D3M_SUPPORTED_VERSIONS))

    # To be compatible with problem descriptions which do not adhere to the schema and have only one entry for data.
    if not isinstance(problem_doc['inputs']['data'], list):
        problem_doc['inputs']['data'] = [problem_doc['inputs']['data']]

    performance_metrics = []
    for performance_metric in problem_doc['inputs']['performanceMetrics']:
        params = {}

        # A special case, setting a default value.
        # See: https://gitlab.datadrivendiscovery.org/nist/nist_eval_output_validation_scoring/commit/6e3e6e2efe99c8210e5de5e17847a2f6e89b0c82
        if performance_metric['metric'] == 'f1':
            params['pos_label'] = performance_metric.get('pos_label', '1')

        if 'pos_label' in performance_metric:
            params['pos_label'] = performance_metric['pos_label']

        if 'K' in performance_metric:
            params['k'] = performance_metric['K']

        # We do not map "applicabilityToTarget" because this is something which depends on
        # the metric itself and does not have to be part of the problem description.
        # See: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/90

        performance_metrics.append({
            'metric': PerformanceMetric.parse(performance_metric['metric']),
            'params': params,
        })

    inputs = []
    for data in problem_doc['inputs']['data']:
        targets = []
        for target in data['targets']:
            targets.append({
                'target_index': target['targetIndex'],
                'resource_id': target['resID'],
                'column_index': target['colIndex'],
                'column_name': target['colName'],
            })

            if 'numClusters' in target:
                targets[-1]['clusters_number'] = target['numClusters']

        problem_input = {
            'dataset_id': data['datasetID'],
        }

        if targets:
            problem_input['targets'] = targets

        inputs.append(problem_input)

    # "dataSplits" are not exposed because it is unclear for what it would be used.
    # It is mostly interesting to know how train/test split was made for evaluation.
    # See: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/37
    #      https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/42
    description = {
        'schema': PROBLEM_SCHEMA_VERSION,
        'problem': {
            'id': problem_doc['about']['problemID'],
            # "problemVersion" is required by the schema, but we want to be compatible with problem
            # descriptions which do not adhere to the schema.
            'version': problem_doc['about'].get('problemVersion', '1.0'),
            'name': problem_doc['about']['problemName'],
            'task_type': TaskType.parse(problem_doc['about']['taskType']),
            'task_subtype': TaskSubtype.parse(problem_doc['about'].get('taskSubType', None)),
        },
        'outputs': {
            'predictions_file': problem_doc['expectedOutputs']['predictionsFile'],
        }
    }

    if performance_metrics:
        description['problem']['performance_metrics'] = performance_metrics  # type: ignore

    if problem_doc['about'].get('problemDescription', None):
        description['problem']['description'] = problem_doc['about']['problemDescription']  # type: ignore

    if inputs:
        description['inputs'] = inputs  # type: ignore

    if problem_doc['expectedOutputs'].get('scoresFile', None):
        description['outputs']['scores_file'] = problem_doc['expectedOutputs']['scoresFile']  # type: ignore

    PROBLEM_SCHEMA_VALIDATOR.validate(description)

    return description


if __name__ == '__main__':
    import logging
    import pprint
    import sys

    logging.basicConfig()

    for problem_doc_path in sys.argv[1:]:
        try:
            pprint.pprint(parse_problem_description(problem_doc_path))
        except Exception as error:
            raise Exception("Unable to parse problem description: {problem_doc_path}".format(problem_doc_path=problem_doc_path)) from error
