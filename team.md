---
title: "Team"
layout: default
excerpt: "Meet our Team."
---


{% assign team = site.data.team.tiss_generated %}

<div class="container py-4">
  <div class="row">
    {% assign counter = 0 %}
    {% for member in team %}
    {% assign id = member[0] %}
    {% assign person = member[1] %}
<div class="col-md-6 mb-4">
  <div class="card h-100">
    <div class="row g-0 align-items-center">
      {% if person.picture %}
      <div class="col-auto">
        <img src="{{ person.picture }}" class="img-fluid rounded-start" style="width: 120px; height: auto;" alt="Portrait of {{ person.name }}">
      </div>
      {% endif %}
      <div class="col">
        <div class="card-body">
          <h5 class="card-title">{{ person.name }}</h5>
          <p class="card-subtitle text-muted mb-2">{{ person.role }}</p>
          <p class="card-text">
            {{ person.bio }}
            {% if person.room_code %}
            <a href="https://maps.tuwien.ac.at/?q={{ person.room_code }}">Room</a>
            {% endif %}
          </p>
          {% if person.email %}
            <a href="mailto:{{ person.email }}">{{ person.email }}</a>
          {% endif %}
        </div>
      </div>
    </div>
  </div>
</div>


      {% assign counter = counter | plus: 1 %}
      {% assign mod = counter | modulo: 2 %}
      {% if mod == 0 %}
        </div><div class="row">
      {% endif %}

    {% endfor %}
  </div>
</div>
