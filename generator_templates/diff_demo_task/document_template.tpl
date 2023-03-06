 <div class="container" _id="{{element.id}}">
      <p>My document name: {{ element.name }}</p>

      <p>Parent project id: {{ element.container.id }} </p>
      <p>Parent project name: {{ element.container.name }}</p>
      <p>Subelements:</p>
      <ul>{% for field in element.elements.values() %}<li _id="{{ field.id }}" name="{{ field.name }}">Field ({{ field.name }})</li>{% endfor %}</ul>
 </div>