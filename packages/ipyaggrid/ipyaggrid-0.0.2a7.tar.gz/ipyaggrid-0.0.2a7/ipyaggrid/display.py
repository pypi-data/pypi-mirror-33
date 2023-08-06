from ipywidgets.embed import embed_data
import os

import json


def export_HTML_code(widget):
    data = embed_data(views=[widget])
    html_template = """
<!-- Load RequireJS, used by the IPywidgets for dependency management -->
<script 
  src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js" 
  integrity="sha256-Ae2Vz/4ePdIu6ZyI/5ZGsYnb+m0JlOmKPjt6XZ9JJkA=" 
  crossorigin="anonymous">
</script>

<!-- Load IPywidgets bundle for embedding. -->
<script 
  src="https://unpkg.com/@jupyter-widgets/html-manager@*/dist/embed-amd.js" 
  crossorigin="anonymous">
</script>

<!-- The state of all the widget models on the page -->
<script type="application/vnd.jupyter.widget-state+json">
  {manager_state}
</script>

<div id="embed grid">
  <!-- This script tag will be replaced by the view's DOM tree -->
  <script type="application/vnd.jupyter.widget-view+json">
    {widget_views[0]}
  </script>
</div>
    """

    manager_state = json.dumps(data['manager_state'])
    widget_views = [json.dumps(view) for view in data['view_specs']]
    rendered_template = html_template.format(
        manager_state=manager_state, widget_views=widget_views)
    return rendered_template
