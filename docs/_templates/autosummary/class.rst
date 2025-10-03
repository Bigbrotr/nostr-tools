{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ fullname }}
   :members:
   :show-inheritance:
   :special-members: __init__, __call__, __aenter__, __aexit__
   :exclude-members: __weakref__, __dict__, __module__, __annotations__

   {% block methods %}
   {% if methods %}
   .. rubric:: {{ _('Methods') }}

   .. autosummary::
   {% for item in methods %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Attributes') }}

   .. autosummary::
   {% for item in attributes %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}
