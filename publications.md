---
title: "Publications"
layout: default
excerpt: "All Publications."
---

{% assign this_year = site.time | date: "%Y" %}

{% assign current_year = nil %}

{% for pub in site.data.publications.dblp_generated %}

  {% if pub.year != current_year %}
    {% unless pub.year == this_year %}
<div class="border-top pt-3 mt-5 fw-bold fs-4">
  {{ pub.year }}
</div>
    {% endunless %}
    {% assign current_year = pub.year %}
  {% endif %}

  <div class="mb-3 p-3 border rounded shadow-sm">
    <h5 class="mb-1">
      <a href="{{ pub.url }}" target="_blank" rel="noopener noreferrer">{{ pub.title }}</a>
    </h5>
    <p class="mb-1 text-muted" style="font-size: 0.9rem;">
      {{ pub.authors | join: ", " }}
    </p>
    <p class="mb-0" style="font-size: 0.85rem;">
      <em>{{ pub.venue }}</em>{% if pub.year %}, {{ pub.year }}{% endif %} | {{ pub.type | capitalize }}
    </p>
  </div>

{% endfor %}
