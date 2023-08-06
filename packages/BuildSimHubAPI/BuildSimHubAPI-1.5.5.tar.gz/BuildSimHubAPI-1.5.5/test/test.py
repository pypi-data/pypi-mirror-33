"""
This example shows how to extract parametric model information as well as their keys
The server returned data is arranged in a list - dict structure, for example:

[{'commit_msg': 'WWR: 0.4, LPD: 0.9, HeatingEff: 0.86', 'commit_date': '2018-06-20', 'commit_id': '1-146-429'},
{'commit_msg': 'WWR: 0.4, LPD: 0.9, HeatingEff: 0.8', 'commit_date': '2018-06-20', 'commit_id': '1-146-428'},
{'commit_msg': 'WWR: 0.4, LPD: 1.2, HeatingEff: 0.86', 'commit_date': '2018-06-20', 'commit_id': '1-146-427'},
{'commit_msg': 'WWR: 0.4, LPD: 1.2, HeatingEff: 0.8', 'commit_date': '2018-06-20', 'commit_id': '1-146-426'},
{'commit_msg': 'WWR: 0.6, LPD: 0.9, HeatingEff: 0.86', 'commit_date': '2018-06-20', 'commit_id': '1-146-425'}]

if there is pandas in the local python library, simply put this structure in pandas dataframe:
df = pd.DataFrame(retrieved_data)
print(df[['commit_msg', 'commit_id']])

This will rearrange the above data into a nicely pandas dataframe:
                             commit_msg  commit_id
0  WWR: 0.4, LPD: 0.9, HeatingEff: 0.86  1-146-429
1   WWR: 0.4, LPD: 0.9, HeatingEff: 0.8  1-146-428
2  WWR: 0.4, LPD: 1.2, HeatingEff: 0.86  1-146-427
3   WWR: 0.4, LPD: 1.2, HeatingEff: 0.8  1-146-426
4  WWR: 0.6, LPD: 0.9, HeatingEff: 0.86  1-146-425
5   WWR: 0.6, LPD: 0.9, HeatingEff: 0.8  1-146-424
6  WWR: 0.6, LPD: 1.2, HeatingEff: 0.86  1-146-423
7   WWR: 0.6, LPD: 1.2, HeatingEff: 0.8  1-146-422

"""

import BuildSimHubAPI as bshapi
import BuildSimHubAPI.postprocess as pp

project_api_key = "f98aadb3-254f-428d-a321-82a6e4b9424c"
model_api_key = 'aa09eabf-693f-4437-88cc-a522a25fba01'

bsh = bshapi.BuildSimHubAPIClient(base_url='http://develop.buildsim.io:8080/IDFVersionControl/')

results = bsh.parametric_results(project_api_key, model_api_key)
data_load = results.total_site_eui()
print(results.last_parameter_unit)
pp_plot = pp.ParametricPlot(data_load)
pp_plot.scatter_chart_plot()
