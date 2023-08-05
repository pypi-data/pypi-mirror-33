# Django Privacy Mgmt

This python module is open-source, available here: https://gitlab.com/what-digital/django-privacy-mgmt/


## Versioning and Packages

- versioning is done in versioning in django_privacy_mgmt/__init__.py
- for each version a tag is added to the gitlab repository in the form of `^(\d+\.)?(\d+\.)?(\*|\d+)$`, example: 0.0.10

- There is a PyPI version which relies on the gitlab tags (the download_url relies on correct gitlab tags being set): https://pypi.org/project/django-privacy-mgmt/
- There is a DjangoCMS / Divio Marketplace add-on which also relies on the gitlab tags: https://marketplace.django-cms.org/en/addons/browse/django-privacy-mgmt/

In order to release a new version of the divio add-on:

- increment version number in addons-dev/django-privacy-mgmt/django_privacy_mgmt/__init__.py
- divio addon validate
- divio addon upload
- then git add, commit and tag with the version number

Then, in order to release a new pypi version:

- python3 setup.py sdist bdist_wheel
- twine upload --repository-url https://test.pypi.org/legacy/ dist/*
- twine upload dist/*

## Intro - what is this all about?

### what is GDPR

GDPR is an EU law that requires public and private organisations to comply with EU user data best practises if one of the following applies (https://francoischarlet.ch/2017/gdpr-in-switzerland-10-steps-to-take/)

- Does your organisation offer services or goods to individuals in the EU?
- Does your organisation process or participate in processing of personal data of EU individuals, for itself or on behalf of another organisation?
- Does your organisation monitor online behaviour of users based in the EU?
- Does your organisation analyse the activities of EU users when they are using your organisation’s app or browsing its website?

To fulfill the new GDPR guidelines APG would need to implement a cookie alert addon into their website.

### GDPR Requirements

- user needs to be able to give consent before GDPR-relevant scripts are executed and such cookies are stored in the user's browser
- user needs to be able to see which GDPR-relevant scripts and such cookies are active on the site
- user needs to be able to deactivate these scripts
- the admin should be able to manage a list of GDPR-relevant scripts in the django admin backend.

### GDPR Trends

Loosely paraphrased from https://piwik.pro/blog/how-will-gdpr-affect-your-web-analytics-tracking/:

It appears that not every type of tracking will require consent from your users. The current form of ePrivacy (Regulation on Privacy and Electronic Communications) makes an exception for personal data used for web analytics purposes. So, if you take advantage of a web analytics tool that utilizes the collected data only to examine the performance of your website, you probably don’t need to worry about this part.

However, if you pass your analytics data to other AdTech and MarTech platforms (such as DSP or CDP), use remarketing pixels and tracking codes, or personalize your website content based on user behavior, you’ll certainly need to ask for consent for each of these activities.

### Implementation of these GDPR Trends / GDPR-relevant Script and Cookie Categories

From how others have implemented GDPR management user interface and from our conversations with compliance experts, we have come to the conclusion that we can simplify the user interface to give the user control over three categories of scripts:

- Essentials or Mandatory (cannot be deactivated): These cookies and services are necessary for you to visit our online services and use their features. Without them, you cannot use services, such as login (sessions), language settings, shopping cart and privacy settings, as well as services related to security. Except for login (sessions), no information of a sensitive nature that can be used to identify you will be collected.
- Statistics (default: activated, user can opt out): These cookies and services collect information about how you use our online services, such as which functions and pages you use most often. This data can help us optimise our online services, for example, or simplify navigation. They are also used to inform partners whether you reached our website through a partner site, and whether your visit led to using one of our offers; however, no information will be recorded that can be used to personally identify you.
- Marketing (default: deactivated, user can opt in): These cookies and services allow the advertising platforms used by APG|SGA to show you ads that are relevant to your interests, or in certain situations, prevent ads from being shown to you. They are also responsible for preventing ads from being displayed repeatedly and ensuring that ads are correctly displayed.

## Limitations of Cookie Management

While it is possible to 'see' some cookies via browser's javascript interface, some cookies cannot be accessed by the website. Therefore, once some tracking / marketing scripts such as a Facebook Pixel have executed after page load, it is impossible to programmatically remove those cookies (applies to http only, third party cookies)

## Dependencies

- make sure you have django parler configured properly if you want to use model translations: https://github.com/django-parler/django-parler#installing-django-parler
- frontend requirements, make sure to include these or change the static resources and templates to your own frontend stack
   - jQuery
   - bootstrap3

## Setup

- install the add-on on divio.com
- update your templates/django_privacy_mgmt to reflect your frontend toolchain situation
- load the template tag library by adding `privacy` to your `{% load %}` tag and then add `{% render_privacy_api %}` to the very top of your root html template's code (it should load before any other javascript so that the API is available)
- add `{% render_privacy_settings_modal %}` to the bottom where the other javascript inclusions reside
- add something like `{% render_privacy_settings_modal_link %}` somewhere on your site (footer?)
- optionally, you can also add `{% render_privacy_banner %}` to a template which will show a nasty banner at the bottom of the page (its just an example based on bootstrap3, you will have to adapt / style it to reflect your frontend setup)


## Cookie and Third-Party Script Management

- for the user to see what he can expect from your website, add the scripts that you are using in the django admin interface. This information will show up in the privacy modal where the user can manage his cookies and scripts.
- now you can set up management for any third-party scripts via the Privacy Mgmt API:

Google Analytics Example:

```
<script>
        // There are three different cookie levels: ESSENTIALS (always on), STATISTICS (opt-out) and MARKETING (opt-in)
        if (django_privacy_mgmt && django_privacy_mgmt.getPreference('STATISTICS')) {

            // here goes the tracking script
            console.log('Activating Google Analytics base code because the user is opted-in (possibly by default).');
            (function (b, o, i, l, e, r) {

                ...

            ga('send', 'pageview');
        }
    </script>
```
