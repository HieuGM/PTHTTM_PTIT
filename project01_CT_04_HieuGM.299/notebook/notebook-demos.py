"""One patient workflow, four cohorts, seven core agents, interactive examples."""
from app.agents.coordinator import Coordinator
from app.ml.schema import SCHEMAS
from app.ml.predict import Predictor
import ipywidgets as widgets

system = Coordinator(ROOT)
QUESTION = 'Giải thích HbA1c và theo dõi đái tháo đường?'
DATASET = 'pima'
FEATURES = {item['name']: item['default'] for item in SCHEMAS[DATASET]}
response = system.report(DATASET, FEATURES, QUESTION)
display(Markdown(response['report']['explanation']['answer']))
display(pd.DataFrame(response['trace']))
display({key: response['report'][key] for key in response['report'] if key != 'retrieved_evidence'})

question_input = widgets.Textarea(value=QUESTION, description='Câu hỏi:',
    layout=widgets.Layout(width='95%', height='80px'))
dataset_input = widgets.Dropdown(options=[('CDC BRFSS', 'cdc'), ('Hospital <30 ngày', 'hospital'),
    ('Pima', 'pima'), ('Early-stage', 'early')], value=DATASET, description='Dữ liệu:')
feature_box = widgets.VBox()
report_button = widgets.Button(description='Tạo báo cáo 7 agent', button_style='info')
report_output = widgets.Output()
feature_inputs = {}


def render_features(change=None):
    feature_inputs.clear()
    children = []
    for item in SCHEMAS[dataset_input.value]:
        control_type = widgets.BoundedIntText if item['integer'] else widgets.BoundedFloatText
        control = control_type(value=item['default'], min=item['min'], max=item['max'],
            description=item['name'], style={'description_width': '180px'},
            layout=widgets.Layout(width='430px'))
        feature_inputs[item['name']] = control
        children.append(widgets.VBox([widgets.Label(item['label']), control,
                                     widgets.Label(item.get('coding', ''))]))
    feature_box.children = tuple(children)


def on_report(_):
    with report_output:
        report_output.clear_output()
        features = {name: control.value for name, control in feature_inputs.items()}
        result = system.report(dataset_input.value, features, question_input.value)
        if result.get('report'):
            display(Markdown(result['report']['explanation']['answer']))
            display(result['report'])
        else:
            display(result['error'])
        display(pd.DataFrame(result['trace']))


dataset_input.observe(render_features, names='value')
report_button.on_click(on_report)
render_features()
display(widgets.VBox([dataset_input, feature_box, question_input, report_button, report_output]))
