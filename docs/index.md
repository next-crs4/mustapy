---
layout: default
title: Home
---

# <span style="color:dark">{{site.title}}</span>
## <span style="color:dark">{{site.description}}</span>
---

{::nomarkdown}

{% assign pages_list = site.pages | sort:"url" %}
    {% for node in pages_list %}
      {% if node.title != null %}
        {% if node.layout == "page"  and node.hide == null %}
          <a class="sidebar-nav-item{% if page.url == node.url %} active{% endif %}" href="{{site.url}}{{ node.url }}">{{ node.title }}
          <p class="note">{{node.summary}}</p></a>
        {% endif %}
      {% endif %}
    {% endfor %}
{:/}

--- 