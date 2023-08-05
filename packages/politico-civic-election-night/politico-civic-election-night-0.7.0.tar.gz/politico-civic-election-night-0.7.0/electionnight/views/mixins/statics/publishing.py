import os

from django.conf import settings as project_settings
from django.test.client import RequestFactory
from django.utils.text import slugify
from electionnight.exceptions import StaticFileNotFoundError
from electionnight.utils.aws import defaults, get_bucket
from rest_framework.renderers import JSONRenderer


class StaticsPublishingMixin(object):
    """
    Handles publishing templates, serialized context and JS/CSS bundles to S3.

    Bundles are published to a directory at paths with this pattern:
    election-results/cdn/{view_name}/{election_date}/{bundle_file}
    """
    def get_request(self, production=False, subpath=''):
        """Construct a request we can use to render the view.

        Send environment variable in querystring to determine whether
        we're using development static file URLs or production."""
        if production:
            env = {'env': 'prod'}
        else:
            env = {'env': 'dev'}
        kwargs = {
            **{"subpath": subpath},
            **env
        }
        return RequestFactory().get('', kwargs)

    def get_serialized_context(self):
        """OVERWRITE this method to return serialized context data.

        Use the serializer for the page you would hit.

        Used to bake out serialized context data.
        """
        return {}

    @staticmethod
    def render_static_string(path):
        """Renders static file to string.

        Must have run collectstatic first.
        """
        absolute_path = os.path.join(
            project_settings.STATIC_ROOT,
            path
        )
        try:
            with open(absolute_path, 'rb') as staticfile:
                return staticfile.read()
        except (OSError, IOError):
            raise StaticFileNotFoundError(
                'Couldn\'t find the file {}. Are you sure you configured '
                'static paths correctly on the view and/or have run '
                'collectstatic?'.format(path)
            )

    def get_cdn_directory(self):
        """Get slugified view name to use as part of CDN path."""
        return slugify(self.__class__.__name__)

    def get_absolute_js_url(self):
        """Get absolute path to published JS bundle.

        subpath handles primaries, primary runoffs and general runoffs.
        """
        return os.path.join(
            'election-results/cdn',
            '{}/{}/{}'.format(
                self.get_cdn_directory(),
                self.election_date,
                self.js_prod_path
            )
        )

    def get_absolute_css_url(self):
        """Get absolute path to published CSS bundle."""
        return os.path.join(
            'election-results/cdn',
            '{}/{}/{}'.format(
                self.get_cdn_directory(),
                self.election_date,
                self.css_prod_path
            )
        )

    def publish_js(self):
        """Publishes JS bundle."""
        js_string = self.render_static_string(self.js_dev_path) # noqa
        key = self.get_absolute_js_url()
        # TODO: Publish to AWS
        print('>>> Publish JS to: ', key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=js_string,
            CacheControl=defaults.CACHE_HEADER,
            ContentType='application/javascript'
        )

    def publish_css(self):
        """Publishes CSS bundle."""
        css_string = self.render_static_string(self.css_dev_path) # noqa
        key = self.get_absolute_css_url()
        # TODO: Publish to AWS
        print('>>> Publish CSS to: ', key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=css_string,
            CacheControl=defaults.CACHE_HEADER,
            ContentType='text/css'
        )

    def publish_serialized_context(self, subpath=''):
        """Publishes serialized context.

        subpath handles primaries, primary runoffs and general runoffs,
        which appends a directory like "primary/".
        """
        data = self.get_serialized_context()
        json_string = JSONRenderer().render(data) # noqa
        key = os.path.join(
            self.get_publish_path(),
            os.path.join(subpath, 'context.json')
        )
        # TODO: Publish to AWS
        print('>>> Publish context to: ', key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=json_string,
            CacheControl=defaults.CACHE_HEADER,
            ContentType='application/json'
        )

    def publish_statics(self, subpath=''):
        self.publish_css()
        self.publish_js()
        self.publish_serialized_context(subpath)

    def publish_template(self, subpath='', **kwargs):
        """Mocks a request and renders the production template.

        kwargs should be a dictionary of the captured URL values.

        If you have a URL path like:
            elections/<int:year>/<slug:state>/

        ... kwargs should be like:
            {"year": 2018, "state": "texas", "election_date": "2018-03-06"}
        """
        request = self.get_request(production=True, subpath=subpath)
        template_string = self.__class__.as_view()(
            request, **kwargs).rendered_content
        key = os.path.join(
            self.get_publish_path(),
            os.path.join(subpath, 'index.html')
        )
        # TODO: Publish to AWS
        print('>>> Publish template to ', key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=template_string,
            CacheControl=defaults.CACHE_HEADER,
            ContentType='text/html'
        )
