<ul>
        {% for field in element.elements %}<li _id="{{ field.id }}" name="{{ field.name }}">Field ({{ field.name }})</li>{% endfor %}
</ul>