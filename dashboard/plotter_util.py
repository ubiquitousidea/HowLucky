from numpy import where, array
import pandas as pd


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


def get_buttons_clicked(entities, clicks):
    """
    return a field name : value condition dictionary from card info and card button clicks
    :param entities: info stored in card store data attributes (could be artist ids, label ids)
    :param clicks: number of time each button was pressed
    :return: condition dictionary
    """

    output = pd.DataFrame(entities).assign(clicks=clicks)
    output = output[output['clicks'].notna()]
    output = output.assign(keep=lambda x: x.clicks % 2 == 1)
    output = output[output['keep']]
    try:
        output = output.groupby('field').agg({'value': lambda x: list(x)}).reset_index().to_dict('records')
        output = {item['field']: item['value'] for item in output}
    except KeyError:
        output = {}

    return output
