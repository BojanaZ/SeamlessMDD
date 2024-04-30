{% macro field(element) -%}
<li _id="{{ element.id }}"  name="{{ element.name }}">
    <div class="form-row">
        <div class="md-form col-md-4 col-sm-5">
            <i class="fas"></i>
            <input type="text" class="form-control ng-untouched ng-pristine ng-valid">
            <label>Field ({{ element.label }})</label>
        </div>
    </div>
</li>
{%- endmacro %}


{% macro fields(elements) -%}
<ul>
{% for element in elements %}
    {{ field(element) }}
{% endfor %}
</ul>
{%- endmacro %}