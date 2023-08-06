# Frasco

Frasco is a layer on top of [Flask](http://flask.pocoo.org/), a micro framework for Python.
Frasco introduces a framework for reusable components, a service
layer and a YAML-based view declaration syntax.

## Introduction

Frasco makes it very easy for you to create reusable components
while you develop your app. This allows you to build a library
of components for yourself as well as use the components shared
by others.

Frasco allows you to start developing your app and reach the MVP status in no time
while giving you the tools to grow and evolve your code base to a professional
level.

### Reusable components

The major feature of Frasco is its framework for building reusable
components. With Frasco, you have three types of components:

 - *Blueprints*: [blueprints](http://flask.pocoo.org/docs/0.10/blueprints/) are
   a feature of Flask and work the same way in Frasco with a few additions
 - *Actions*: an action is a function with some additional metadata
   executed as part of an action context.
 - *Features*: features are the way to bring a set of actions, blueprints,
   commands and any other feature into your application.

### Service layer

Services are classes easily accessible through `app.services` and which
methods can be actions and/or exposed as a view. Method's return value
will be converted to JSON.

### Declarative applications

Frasco allows you to create views, blueprints or whole applications without
a single line of python using its declarative engine. Elements are defined
using a mix of YAML and Jinja. Inspired by Jekyll and Ansible.

## Installation

    $ pip install frasco

## Get started

    $ frasco init myapp
    $ cd myapp
    $ frasco run