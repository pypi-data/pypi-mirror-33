=====
django_react_views
=====

django_react_views is a Django app providing generic Class Based views and template tags that make it easy to use react
alongside django views and templates.

Quick start
-----------

1. Add "django_react_views" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django_react_views',
    ]

2. Create a directory in your app called 'react'

3. Copy webpack.config.js or use you're own webpack config as long as it builds your react components into one of your STATICFILES_DIRS

4. Use npm to install AT LEAST the packages required for react & building with webpack::

    npm install --save-prod react react-dom
    npm install --save-dev babel-core babel-loader babel-preset-env babel-preset-es2015 babel-preset-react glob webpack webpack-cli

5. Add these scripts to package.json ::

    "scripts": {
        "build": "webpack",
        "watch": "webpack --watch"
    },

6. Execute `npm run watch` to start building your react files

7. Add the react template tag to the template where you want to show your react component::

    {% load react %}
    ...
    {% react %}
    ...

8. Create a view for your template::

    from django_react_views.views import ReactDetailView
    class MyReactView(ReactDetailView):
        react_component = 'MyReactComponent.js'  # By default this will resolve to dist/app_name/{react_component}. If {% static %} can not find the file you may need to edit some other properties of this class
        model_serializer = MyModelSerializer
        model = MyModel

9. Add a url for your view::

    urlpatterns = [
        ...
        path('my-react-view/<int:pk>/', MyReactView.as_view(), name='my-react-view')
    ]

10. This framework provides window.props, which contains a javascript object that can be used to hydrate your react state. This has the shape of::

    window.props = {"objects": {"appname.modelname": {1: {object as serialized by your model serializer}} } }

11. Start the development server and visit http://127.0.0.1:8000/ and visit your page to see you're react component in action
