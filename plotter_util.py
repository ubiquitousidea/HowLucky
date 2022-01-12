from numpy import where, array


def get_factor(attribute, traces, custom_data_labels):
    """
    extract custom data from selected points by name
    :param attribute: name of the variable to extract
    :param custom_data_labels: list of the column names in the points' customdata
    :param traces: selectedData attribute of a dcc.Graph
    :return: list of unique values of colname among the selected points in traces
    """
    var_index = where(array(custom_data_labels) == attribute)[0][0]
    values = [point['customdata'][var_index] for point in traces['points']]
    values = list(set(values))
    condition = {attribute: values}
    return condition
