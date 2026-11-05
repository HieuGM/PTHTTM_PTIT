"""Editable examples and interactive forms; included directly in notebook cells."""
system = Coordinator(ROOT)
QUESTION = "Giải thích chi tiết HbA1c là gì?"
response = system.answer(QUESTION)
display(Markdown(response['answer']))
display(pd.DataFrame(response['trace']))

# Thay các giá trị ở đây để dùng không cần widget.
DATASET = 'cdc'
FEATURES = {item['name']: item['default'] for item in SCHEMAS[DATASET]}
display(pd.DataFrame(SCHEMAS[DATASET])[['name', 'label', 'min', 'max', 'default']])
display(system.analyze(DATASET, FEATURES))

import ipywidgets as widgets

question_input = widgets.Textarea(value=QUESTION, description='Câu hỏi:',
                                  layout=widgets.Layout(width='95%', height='80px'))
ask_button = widgets.Button(description='Hỏi kho tri thức', button_style='info')
chat_output = widgets.Output()


def on_ask(_):
    with chat_output:
        chat_output.clear_output()
        try:
            answer = ChatRequest(question=question_input.value) if 'ChatRequest' in globals() else None
            question = answer.question if answer else question_input.value.strip()
            if not 3 <= len(question) <= 2000:
                raise ValueError('Câu hỏi cần từ 3 đến 2000 ký tự.')
            reply = system.answer(question)
            display(Markdown(reply['answer']))
            display(pd.DataFrame(reply['trace']))
        except (ValueError, TypeError) as error:
            print(str(error))


ask_button.on_click(on_ask)
display(widgets.VBox([question_input, ask_button, chat_output]))

dataset_input = widgets.Dropdown(options=[('CDC BRFSS', 'cdc'), ('Hospital <30 ngày', 'hospital')],
                                 value='cdc', description='Bộ dữ liệu:')
feature_box = widgets.VBox()
predict_button = widgets.Button(description='Tính score nghiên cứu', button_style='warning')
prediction_output = widgets.Output()
feature_inputs = {}


def render_features(change=None):
    feature_inputs.clear()
    children = []
    for item in SCHEMAS[dataset_input.value]:
        cls = widgets.BoundedIntText if item['integer'] else widgets.BoundedFloatText
        control = cls(value=item['default'], min=item['min'], max=item['max'],
                      description=item['name'], style={'description_width': '180px'},
                      layout=widgets.Layout(width='420px'))
        feature_inputs[item['name']] = control
        children.append(widgets.VBox([widgets.Label(item['label']), control,
                                     widgets.Label(item.get('coding', ''))]))
    feature_box.children = tuple(children)


def on_predict(_):
    with prediction_output:
        prediction_output.clear_output()
        try:
            features = {name: control.value for name, control in feature_inputs.items()}
            result = system.analyze(dataset_input.value, features)
            display({key: value for key, value in result.items() if key != 'trace'})
            display(pd.DataFrame(result['trace']))
        except (ValueError, TypeError) as error:
            print(str(error))


dataset_input.observe(render_features, names='value')
predict_button.on_click(on_predict)
render_features()
display(widgets.VBox([dataset_input, feature_box, predict_button, prediction_output]))
