{% import 'diff_demo_task/macros.tpl' as macros %}
<div class="container" _id="{{element.id}}">
  <p>My document name: {{ element.name }}</p>

  <p>Parent project id: {{ element.parent_container.id }} </p>
  <p>Parent project name: {{ element.parent_container.name }}</p>
  <p>Subelements:</p>
    {{ macros.fields(element.elements) }}
</div>