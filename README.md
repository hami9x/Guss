Guss - Growing Up Social System
====

Built for Google App Engine. This is a codebase that aims to provide a bunch of things related to user interaction and content management, packed into a cohesive system, with a stress on performance, cost-effectiveness and code maintainability. Written in Python.

## The why:

* There's a lack of high-quality, performant and feature-complete content management and social networking codebase dedicated to Google App Engine.

## The goals:

* A clean, maintainable, cohesive, and readable codebase.
* Lightning-fast and cost-effective.
* Stable
* Born to be forked, no need for a slow and complicated extension system.
* Features:
    * Admin control panel. Just make enough tools to control things.
    * A role-based access control system.
    * A blogging system for members.
    * A discussion system that both serves as a blog commenting and a simple forum system.
    * User authentication, member profile, activity stream, private messaging and user connection/following (basic functionalities for a community).
    * It looks disgusting without a design, so a basic design based on Twitter Bootstrap or Zurb Foundation would be great. Doesn't need to be beautiful though.

## Contributing:
1. Install Google App Engine SDK.
1. Clone this repository to a folder and run the App Engine SDK's dev\_appserver inside the newly cloned folder.
1. Run `git submodule init` and `git submodule update`
1. Run `http://localhost:<port>/install`, it will put necessary things to the database
1. Start hacking!

## License:
Copyright 2012 Hai Thanh Nguyen

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

## Things that powered this software:
* Python programming language
* Google App Engine and the webapp2 framework - http://appengine.google.com
* Jinja2 Template Engine - https://jinja.pocoo.org
* Hallo rich text editor - http://hallojs.org
* Font Awesome - http://fortawesome.github.com/Font-Awesome
* Zurb Foundation layout framework - http://foundation.zurb.com
