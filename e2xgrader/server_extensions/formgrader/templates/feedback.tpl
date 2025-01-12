{%- extends 'basic.tpl' -%}
{% from 'mathjax.tpl' import mathjax %}

{%- block header -%}
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8" />
<title>{{ resources.nbgrader.notebook }}</title>

{% for css in resources.inlining.css -%}
    <style type="text/css">
    {{ css }}
    </style>
{% endfor %}

<!-- Loading mathjax macro -->
{{ mathjax() }}

<style>
td.center, th.center {
    text-align: center;
}

body {
  overflow: visible;
  font-size: 14px;
  padding-top: 1em;
}

div#notebook {
  overflow: visible;
  border-top: none;
}

div#notebook-container {
  width: 100%;
}

@media print {
  div.cell {
    display: block;
    page-break-inside: avoid;
  }
  div.output_wrapper {
    display: block;
    page-break-inside: avoid;
  }
  div.output {
    display: block;
    page-break-inside: avoid;
  }
}

div.prompt {
  min-width: 5em;
}

div.panel.panel-primary.nbgrader_cell {
  width: -webkit-calc(100% - 5.8em);
  width:    -moz-calc(100% - 5.8em);
  width:         calc(100% - 5.8em);
}

div.nbgrader_cell {
    width: 100%;
}

div.nbgrader_cell .panel-heading {
    padding: 0.4em 0.6em;
    height: 37px;
}

div.nbgrader_cell .panel-heading a {
    color: #BBBBBB;
}

div.nbgrader_cell .panel-footer {
    padding: 0.4em 0.6em;
}

div.nbgrader_cell .panel-body {
    padding: 0.4em;
}

.comment {
    width: 100%;
    margin-top: 0.5em;
}

div.nbgrader_cell .input_area {
    background: white;
    border: none;
}

.score {
    color: black;
}

li.late-penalty {
    color: #d2413a;
}

span.nbgrader-label {
    line-height: 25px;
}

.save-icon {
    margin-left: 1em;
    top: 4px;
}

.panel-body {
    position: relative;
    min-height: 17.5em;
}

.annotation {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
}
</style>

</head>
{%- endblock header -%}

{% block body %}
<body>
  <a name="top"></a>
  <div class="container">
    <div class="panel panel-default">
      <div class="panel-heading">
        <h4>{{ resources.nbgrader.notebook }} (Score: {{ resources.nbgrader.score | float | round(2) }} / {{ resources.nbgrader.max_score | float | round(2) }})</h4>
        <div id="toc">
          <ol>
          {% for cell in nb.cells %}
            {% if cell.metadata.nbgrader and cell.metadata.nbgrader.grade and not cell.metadata.nbgrader.solution %}
            <li><a href="#{{ cell.metadata.nbgrader.grade_id }}">Test cell</a> (Score: {{ cell.metadata.nbgrader.score | float | round(2) }} / {{ cell.metadata.nbgrader.points | float | round(2) }})</li>
            {% elif cell.cell_type == "code" and cell.metadata.nbgrader and cell.metadata.nbgrader.grade %}
            <li><a href="#{{ cell.metadata.nbgrader.grade_id }}">Coding free-response</a> (Score: {{ cell.metadata.nbgrader.score | float | round(2) }} / {{ cell.metadata.nbgrader.points | float | round(2) }})</li>
            {% elif cell.cell_type == "markdown" and cell.metadata.nbgrader and cell.metadata.nbgrader.grade %}
            <li><a href="#{{ cell.metadata.nbgrader.grade_id }}">Written response</a> (Score: {{ cell.metadata.nbgrader.score | float | round(2) }} / {{ cell.metadata.nbgrader.points | float | round(2) }})</li>
            {% elif cell.cell_type == "markdown" and cell.metadata.nbgrader and cell.metadata.nbgrader.task %}
            <li><a href="#{{ cell.metadata.nbgrader.grade_id }}">Task</a> (Score: {{ cell.metadata.nbgrader.score | float | round(2) }} / {{ cell.metadata.nbgrader.points | float | round(2) }})</li>
            {% endif %}
            {% if cell.metadata.nbgrader and cell.metadata.nbgrader.comment and cell.metadata.nbgrader.comment %}
            <li><a href="#comment-{{ cell.metadata.nbgrader.grade_id }}">Comment</a></li>
            {% endif %}
          {% endfor %}
          {% if resources.nbgrader.late_penalty > 0 %}
            <li class="late-penalty">Late submission penalty (Score: -{{ resources.nbgrader.late_penalty | float | round(2) }})</li>
          {% endif %}
          </ol>
        </div>
      </div>
      <div class="panel-body">
        <div id="notebook" class="border-box-sizing">
          <div class="container" id="notebook-container">
            {{ super() }}
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
{%- endblock body %}

{% block footer %}
</html>
{% endblock footer %}

{% macro score(cell) -%}
  <span class="pull-right">
      Score: {{ cell.metadata.nbgrader.score | float | round(2) }} / {{ cell.metadata.nbgrader.points | float | round(2) }} <a href="#top">(Top)</a>
  </span>
{%- endmacro %}


{% macro nbgrader_heading(cell) -%}
{%- if cell.metadata.nbgrader.solution or cell.metadata.nbgrader.task -%}
<a name="comment-{{ cell.metadata.nbgrader.grade_id }}"></a>
{%- endif -%}
{%- if cell.metadata.nbgrader.grade -%}
<a name="{{ cell.metadata.nbgrader.grade_id }}"></a>
{%- endif -%}
<div class="panel-heading">
{%- if cell.metadata.nbgrader.solution -%}
  <span class="nbgrader-label">Student's answer</span>
  {%- if cell.metadata.nbgrader.grade  -%}
  {{ score(cell) }}
  {%- else -%}
  <span class="pull-right"><a href="#top">(Top)</a></span>
  {%- endif -%}
{%- elif cell.metadata.nbgrader.task -%}
  <span class="nbgrader-label">Student's task</span>
  {{ score(cell) }}
{%- elif cell.metadata.nbgrader.grade -%}
  <span class="nbgrader-label">Grade cell: <code>{{ cell.metadata.nbgrader.grade_id }}</code></span>
  {{ score(cell) }}
{%- elif cell.metadata.nbgrader.task -%}
  <span class="nbgrader-label">Task: <code>{{ cell.metadata.nbgrader.grade_id }}</code></span>
  {{ score(cell) }}
{%- endif -%}
</div>
{%- endmacro %}

{% macro nbgrader_footer(cell) -%}
{%- if (cell.metadata.nbgrader.solution and cell.metadata.nbgrader.comment) or (cell.metadata.nbgrader.task and cell.metadata.nbgrader.comment) -%}
<div class="panel-footer">
  <div>
    <b>Comments:</b> {{ cell.metadata.nbgrader.comment | markdown2html | strip_files_prefix }}
  </div>
</div>
{%- endif -%}
{%- endmacro %}

{% block markdowncell scoped %}
<div class="cell border-box-sizing text_cell rendered">
  {{ self.empty_in_prompt() }}

  {%- if 'nbgrader' in cell.metadata and (cell.metadata.nbgrader.solution or cell.metadata.nbgrader.grade or cell.metadata.nbgrader.task ) -%}
  <div class="panel panel-primary nbgrader_cell">
    {{ nbgrader_heading(cell) }}
    <div class="panel-body">
      {%- if cell.metadata.nbgrader.solution and cell.metadata.nbgrader.grade_id in resources.annotations -%}
        <img class='annotation' id='{{ cell.metadata.nbgrader.grade_id }}-annotation' src='annotations/{{ cell.metadata.nbgrader.grade_id }}.png'></img>
      {%- endif -%}
      <div class="text_cell_render border-box-sizing rendered_html">
        {{ cell.source  | markdown2html | strip_files_prefix | to_choicecell }}
      </div>
    </div>
    {{ nbgrader_footer(cell) }}
  </div>

  {%- else -%}

  <div class="inner_cell">
    <div class="text_cell_render border-box-sizing rendered_html">
      {{ cell.source  | markdown2html | strip_files_prefix }}
    </div>
  </div>

  {%- endif -%}

</div>
{% endblock markdowncell %}

{% block input %}
  {%- if 'nbgrader' in cell.metadata and (cell.metadata.nbgrader.solution or cell.metadata.nbgrader.grade) -%}
  <div class="panel panel-primary nbgrader_cell">
    {{ nbgrader_heading(cell) }}
    <div class="panel-body">
      {%- if cell.metadata.nbgrader.solution and cell.metadata.nbgrader.grade_id in resources.annotations -%}
        <img class='annotation' id='{{ cell.metadata.nbgrader.grade_id }}-annotation' src='annotations/{{ cell.metadata.nbgrader.grade_id }}.png'></img>
      {%- endif -%}

      <div class="input_area">

        {{ cell.source | highlight_code_with_linenumbers(metadata=cell.metadata) }}
      </div>
    </div>
    {{ nbgrader_footer(cell) }}
  </div>

  {%- else -%}

  <div class="inner_cell">
    <div class="input_area">
      {{ cell.source | highlight_code_with_linenumbers(metadata=cell.metadata) }}
    </div>
  </div>
  {%- endif -%}

{% endblock input %}
