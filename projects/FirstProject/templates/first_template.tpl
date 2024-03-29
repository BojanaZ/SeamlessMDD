<!DOCTYPE html>
<html>
  <head>
    <title>Flask Template Example</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="http://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <style type="text/css">
      .container {
        max-width: 500px;
        padding-top: 100px;
      }
    </style>
  </head>
  <body>
    <div class="container" _id="{{element.id}}">
      <p>My document name: {{ element.name }}</p>

      <p>Parent project id: {{ element.container.id }} </p>
      <p>Parent project name: {{ element.container.name }}</p>
      <p>Subelements:</p>
      <ul>{% for field in element.elements.values() %}<li _id="{{ field.id }}" name="{{ field.name }}">Field ({{ field.name }})</li>{% endfor %}</ul>
    </div>
    <script _id="{{ element.container.id }}" src="http://code.jquery.com/jquery-1.10.2.min.js"></script>
    <script src="http://netdna.bootstrapcdn.com/bootstrap/3.0.0/js/bootstrap.min.js"></script>
  </body>
</html>