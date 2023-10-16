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
    values = [point["customdata"][var_index] for point in traces["points"]]
    values = list(set(values))
    condition = {attribute: values}
    return condition


class ClickState(object):
    def __init__(self, entities, clicks):
        """
        class to represent the state of buttons clicked in the search result array
        :param entities: info stored in card store data attributes (could be artist ids, label ids)
        :param clicks: number of time each button was pressed
        """
        self._clicks = clicks
        self._entities = entities

    def get_buttons_clicked(self):
        """
        determine which card buttons have been clicked an odd number of times
        summarize which buttons were clicked by returning a dictionary similar to
        {
            'artist_id': [ids of the artists clicked an odd number of times]
        }
        :return: dictionary of list of ids values
            conditions include artist_id=[...], album_id=[...], and others
        """

        output = pd.DataFrame(self._entities).assign(clicks=self._clicks)
        output = output[output["clicks"].notna()]
        output = output.assign(keep=lambda x: x.clicks % 2 == 1)
        output = output[output["keep"]]
        try:
            output = (
                output.groupby("field")
                .agg({"value": lambda x: list(x)})
                .reset_index()
                .to_dict("records")
            )
            output = {item["field"]: item["value"] for item in output}
        except KeyError:
            output = {}

        return output

    def get_last_button_clicked(self, entities, clicks):
        pass
