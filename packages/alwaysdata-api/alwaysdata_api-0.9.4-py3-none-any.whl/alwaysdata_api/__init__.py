# -*- coding: utf-8 -*-
"""A dead simple Python interface to the Alwaysdata API (v1).

Example:
    Requires the `ALWAYSDATA_API_KEY` and `ALWAYSDATA_ACCOUNT`
    environment variables to be set:

    >>> # List all domains.
    >>> domains = Domain.list(name='paulkoppen')
    >>> domains # doctest: +ELLIPSIS
    [Domain(..., date_expiration='2021-09-22T17:38:35', ..., name='paulkoppen.com')]
    >>> # Find nameserver DNS records.
    >>> domain = domains[0]
    >>> records = Record.list(domain=domain.id, type='NS')
    >>> records # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [Record(..., ttl=300, type='NS', value='dns2.alwaysdata.com'),
     Record(..., ttl=300, type='NS', value='dns1.alwaysdata.com')]
    >>> # Print the WHOIS information.
    >>> print(domain.whois()) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
       Domain Name: PAULKOPPEN.COM
       Registry Domain ID: 1569922829_DOMAIN_COM-VRSN
       Registrar WHOIS Server: whois.gandi.net
       Registrar URL: http://www.gandi.net
    ...
"""
from logging import getLogger
from os import environ
from types import SimpleNamespace
from typing import Dict, List, Sequence, Union
from urllib.parse import urljoin

import requests
from requests.auth import AuthBase, HTTPBasicAuth

log = getLogger(__name__)

api_root = 'https://api.alwaysdata.com/'


class Auth(HTTPBasicAuth):
    def __init__(self, account_name: str, api_key: str) -> None:
        super().__init__(f'{api_key} account={account_name}', '')


try:
    DEFAULT_AUTH = Auth(environ['ALWAYSDATA_ACCOUNT'],
                        environ['ALWAYSDATA_API_KEY'])
except KeyError:
    DEFAULT_AUTH = None


class Resource(SimpleNamespace):
    """
    All resources must define their endpoint on the server. This is
    stored in the `href` attribute. The `href` **class** attribute stores
    the general resource endpoint (e.g. `/v1/domain/` for all domains).
    The `href` **instance** attribute stores the endpoint for that
    specific resource instance (e.g. `/v1/domain/123/` for domain 123).

    Some resource classes provide a customised `__init__` function to
    check for valid arguments (where the type is an ENUM) and fix some
    responses from the server to adhere to the defined type.

    Methods:
        delete: Deletes the resource from the server.
        delta: (static) Computes the difference between two instances.
        get: (class method) Fetches the specified (single) resource.
        from_json: (class method) Builds the resource from JSON.
        list: (class method) Fetches a list of resources based optionally
            on parameters.
        patch: Posts resource changes to the server.
        post: Posts a new resource to the server.
        put: Posts a new or updated resource to the server.
        request: (class method) Calls the API and returns the response.
    """
    def delete(self, auth: AuthBase = DEFAULT_AUTH) -> None:
        """Deletes the resource from the server.

        Args:
            auth: Optional authentication, when the default
                authentication is not available or different credentials
                should be used.

        Raises:
            `requests.HTTPError` upon failure.
            When no exception is raised we may assume the request was
            successful.
        """
        if 'href' not in self.__dict__:
            raise ValueError('DELETE requires the `href` attribute to be set.')
        self.request('DELETE', self.href, auth=auth)

    @staticmethod
    def delta(res1: 'Resource', res2: 'Resource') -> 'Resource':
        """Computes the difference between two instances.

        Args:
            res1: One resource instance.
            res2: Another resource instance.

        Returns:
            A resource instance of the same class as `res2` containing
            only the properties from `res2` that differ from `res1`.
            Additionally, the `href` attribute from `res2` is copied
            over (to submit to the API correctly).

        Notes:
            Removal of properties is not supported. That is, attributes
            defined on `res1` but not on `res2` print a warning. The
            delta does not include any means to mark that change.
        """
        res1_dict = res1.__dict__
        res2_dict = res2.__dict__

        deleted = set(res1_dict.keys()) - set(res2_dict.keys())
        if any(deleted):
            log.warning(f'Diff does not support removed attributes {deleted}.')

        diff = dict(set(res2_dict.items()) - set(res1_dict.items()))
        if 'href' in res2_dict:
            diff['href'] = res2.href

        return res2.__class__(**diff)

    @classmethod
    def get(cls, id: int, auth: AuthBase = DEFAULT_AUTH) -> 'Resource':
        """Fetches the specified (single) resource.

        Args:
            id: Numeric identifier of the requested resource.
            auth: Optional authentication, when the default
                authentication is not available or different credentials
                should be used.

        Returns:
            The resource, an instance of `cls` (a Resource subclass).
        """
        address = urljoin(cls.href, str(id))
        response = cls.request('GET', address, auth=auth)
        result: cls = cls.from_json(response.json())
        return result

    @classmethod
    def from_json(cls, json: Dict) -> 'Resource':
        """Builds the resource from JSON.

        Resources with special handling can overload this.

        Args:
            json: The JSON object (dict, list or string).

        Returns:
            The resource instance.
        """
        return cls(**json)

    @classmethod
    def list(cls, auth: AuthBase = DEFAULT_AUTH,
             **kwargs: Union[str, int, List, Dict]) -> List['Resource']:
        """Fetches a list of resources based optionally on parameters.

        Args:
            auth: Optional authentication, when the default
                authentication is not available or different credentials
                should be used.
            **kwargs: Query parameters passed in as keyword arguments.
                By default there are no query parameters and the
                exhaustive list of resources is returned. Use keywords
                to narrow this down.

        Returns:
            A list of Resource (subclass) instances.
        """
        response = cls.request('GET', cls.href, params=kwargs, auth=auth)
        result: List[cls] = list(map(cls.from_json, response.json()))
        return result

    def patch(self, auth: AuthBase = DEFAULT_AUTH) -> None:
        """Posts resource changes to the server.

        In a HTTP PATCH request, the client sends only partial data: the
        values that need to change. All other data is left out.

        What this means practically is that this resource needs only hold
        the attributes that need to be changed (plus the `href` to send
        the patch request to the right place).

        By virtue of the `SimpleNamespace`, the `Resource` class is
        naturally sparse. Only the attributes you explicitly set will
        be defined.

        Alternatively, use `Resource.delta` to compute the difference
        between two given full states.

        Note that we cannot "unset" attributes. I don't know how to send
        such a change to the Alwaysdata API. We can only "set" new
        values.

        Args:
            auth: Optional authentication, when the default
                authentication is not available or different credentials
                should be used.

        Raises:
            `requests.HTTPError` upon failure.
            When no exception is raised we may assume the request was
            successful.
        """
        if 'href' not in self.__dict__:
            raise ValueError('PATCH requires the `href` attribute to be set.')
        self.request('PATCH', self.href, json=self.__dict__, auth=auth)

    def post(self, auth: AuthBase = DEFAULT_AUTH) -> None:
        """Posts a new resource to the server.

        In a HTTP POST request, the server assigns the location (URI, or
        here, `href`) for the new resource. This method thus posts to
        the `href` of the resource class, not the instance. If you wish
        to define the resource location, use `put`.

        Args:
            auth: Optional authentication, when the default
                authentication is not available or different credentials
                should be used.

        Raises:
            `requests.HTTPError` upon failure.
            When no exception is raised we may assume the request was
            successful.
        """
        self.request('POST', self.__class__.href, json=self.__dict__,
                     auth=auth)

    def put(self, auth: AuthBase = DEFAULT_AUTH) -> None:
        """Posts a new or updated resource to the server.

        In a HTTP PUT request, the client chooses the location (URI, or
        here, `href`) for the resource. In contrast with the POST method
        this method thus sends the data to the `href` defined on the
        instance.

        To let the server decide the resource location, use `post`.

        Args:
            auth: Optional authentication, when the default
                authentication is not available or different credentials
                should be used.

        Raises:
            `requests.HTTPError` upon failure.
            When no exception is raised we may assume the request was
            successful.
        """
        if 'href' not in self.__dict__:
            raise ValueError('PUT requires the `href` attribute to be set.')
        self.request('PUT', self.href, json=self.__dict__, auth=auth)

    @classmethod
    def request(cls, method: str, endpoint: str, auth: AuthBase,
                **kwargs: Union[str, Dict, Sequence]) -> requests.Response:
        """Calls the API and returns the response.

        Args:
            method: The request method. One of `GET`, `POST`, `PUT`,
                `PATCH` and `DELETE`.
            endpoint: The resource path of the request (e.g.
                `/account/123`).
            auth: Optional authentication, when the default
                authentication is not available or different credentials
                should be used.
            **kwargs: Any other keyword arguments such as `params` for
                parameters in the query string or `json` for encoded
                data in the request body. Do not include auth in here,
                that is appended automatically on every request.

        Returns:
            The response from the server as a `requests.Response`
            object.
        """
        assert method in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')
        url = urljoin(api_root, endpoint)
        response = requests.request(method, url, **kwargs, auth=auth)
        response.raise_for_status()
        return response


# =======================================================================
# The remainder of this file defines all endpoints (resources) available
# in the Alwaysdata API.
# -----------------------------------------------------------------------

class Account(Resource):
    """Account.
    https://api.alwaysdata.com/v1/account/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        name: The account name determines in particular the address of
            the sub domain that you will be awarded. For example, if the
            name is superman, your sub domain will be
            http://superman.alwaysdata.net.
        product: Product.
        password: This password will be used for default users (FTP,
            MySQL, SSH, etc).
        period: Yearly payment is always less expensive but
            non-refundable. Please consult our pricing for details.
            Possible values: `1y`: 1 year(s), `1mo`: 1 month(s).
        location_type: Account location (type). Possible values:
            `datacenter`, `server`.
        location_object: Account location (ID).
    """
    id: int
    href: str = '/v1/account/'
    name: str
    product: int
    password: str
    period: str
    location_type: str
    location_object: int


class Customer(Resource):
    """Customer.
    https://api.alwaysdata.com/v1/customer/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        email: This email address is used to log into the administration
            panel. It will never be sold.
        password: Leave empty if you don't want to change the password.
        type: Possible choices: `company`, `individual`, `organization`.
        name: Name.
        telephone: We will use this number only in case of emergency.
        address: Address.
        postal_code: Zip code.
        city: City.
        country: Country.
        api_key: This key can be used instead of the usual email/
            password to connect via the API. It is generated
            automatically.
    """
    id: int
    href: str = '/v1/customer/'
    email: str
    password: str
    type: str
    name: str
    telephone: str
    address: str
    postal_code: str
    city: str
    country: str
    api_key: str


class Database(Resource):
    """Database.
    https://api.alwaysdata.com/v1/database/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        extensions: Uncheck an extension to deactivate it. If you need
            an unlisted extension, please contact our support. (for
            type=POSTGRESQL.)
        is_public: By checking this box, the database will be accessible
            to anonymous users. (for type=COUCHDB)
        locale: The locale determines LC_COLLATE and LC_TYPE. (for
            type=POSTGRESQL.)
        name: The name must start with: demo_
        type: Type of database. Possible choices: `COUCHDB`, `MONGODB`,
            `MYSQL`, `POSTGRESQL` and `RABBITMQ`.
        permissions: Permissions object. It is a dictionary mapping
            database keys to one of `FULL`, `READONLY` or `NONE`.
    """
    id: int
    href: str = '/v1/database/'
    extensions: Sequence[str]
    is_public: bool
    locale: str
    name: str
    type: str
    permissions: Dict[str, str]


class DatabaseUser(Resource):
    """Database user.
    https://api.alwaysdata.com/v1/database/user/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        name: The name must start with demo_.
        password: Password.
        type: The type of database. Possible values: `COUCHDB`,
            `MONGODB`, `MYSQL`, `POSTGRESQL`, `RABBITMQ`.
        require_ssl: SSL connection required.
        host: IP address or range authorized to connect with this user.
            Example: 192.0.2.38, 192.0.2.0/24, 2001:DB8::1.
        permissions: Permissions on the object: dictionary with
            databases names as keys and `FULL`, `READONLY` or `NONE` as
            values.
    """
    id: int
    href: str = '/v1/database/user/'
    name: str
    password: str
    type: str
    require_ssl: bool
    host: str
    permissions: Dict[str, str]


class Datacenter(Resource):
    """Data center.
    https://api.alwaysdata.com/v1/datacenter/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        name: Name.
        country: Country.
    """
    id: int
    href: str = '/v1/datacenter/'
    name: str
    country: str


class Domain(Resource):
    """Domain.
    https://api.alwaysdata.com/v1/domain/doc/

    To query the WHOIS for this domain, use `api.whois(domain)`.

    Attributes:
        id: Resource ID.
        href: Resource location.
        name: Domain name.
        is_internal: External domain names are those registered at
            another registrar.
        auto_renew: Auto renew.
        date_expiration: Expiration date.
        default_ip_addresses: Subdomains created automatically use this
            IP address. However, you can change the details in the
            settings of the subdomain.
        default_ssl_certificate: Created subdomains will automatically
            use this SSL certificate. However, you can change the
            settings in the subdomain details.
        alias_mail_of: This domain will be an alias for the specified
            domain for incoming mails.
        dkim_selector: DKIM selector.
        dkim_public_key: The public key in PEM format and RSA
            encryption.
        dkim_private_key: The private key in PEM format and RSA
            encrypted.
    """
    id: int
    href: str = '/v1/domain/'
    name: str
    is_internal: bool
    auto_renew: bool
    date_expiration: str
    default_ip_addresses: Sequence[int]
    default_ssl_certificate: int
    alias_mail_of: int
    dkim_selector: str
    dkim_public_key: str
    dkim_private_key: str

    def whois(self, auth: AuthBase = DEFAULT_AUTH) -> str:
        """Returns the WHOIS information for the domain.

        Args:
            auth: Optional authentication, when the default
                authentication is not available or different credentials
                should be used.

        Returns:
            A string with the WHOIS response.

        Raises:
            `requests.HTTPError` upon failure.
        """
        endpoint = self.href + 'whois/'
        return self.request('POST', endpoint, auth=auth).text


class Record(Resource):
    """Domain record (DNS).
    https://api.alwaysdata.com/v1/record/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        domain: Domain.
        type: Type of DNS record (A, CNAME, MX, TXT, etc.)
        name: Only consists of letters, numbers, dash, underscore, or
            leave blank to designate the domain itself.
        value: Value.
        priority: For MX and SRV records, please specify a priority.
        ttl: In seconds.
        is_active: True if the DNS record is active.
        is_user_defined: True if the record was created by the user.
    """
    id: int
    href: str = '/v1/record/'
    domain: int
    type: str
    name: str
    value: str
    priority: int
    ttl: int
    is_active: bool
    is_user_defined: bool

    def __init__(self, *args: Union[int, str, bool],
                 domain: Union[int, Dict[str, str]] = None,
                 **kwargs: Union[int, str, bool]) -> None:
        # Fix when API returns {'domain': {'href': '/v1/domain/1234/'}}
        if domain is not None:
            if type(domain) != int:
                domain = int(domain['href'].split('/')[-2])
            kwargs.update(domain=domain)
        super().__init__(*args, **kwargs)


class Firewall(Resource):
    """Firewall rule.
    https://api.alwaysdata.com/v1/firewall/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        protocol: Protocol. Possible choices: `TCP`, `UDP`, `ANY`.
        action: Type. Possible choices: `ACCEPT`, `DROP`, `REJECT`.
        direction: Direction. Possible choices: `IN`, `OUT`.
        hosts: Please specify one or several hosts, separated by spaces.
            Hosts examples: 192.0.2.38, 192.0.2.0/24 or 2001:DB8::1.
        ports: Please specigy one or several port numbers, separated
            by spaces. You can also indicate consecutive ports, e.g.
            10000:10010.
        ip_version: IP version. Possible choices: `4`: IPv4, `6`: IPv6,
            `ANY`: IPv4/IPv6.
    """
    id: int
    href: str = '/v1/firewall/'
    protocol: str
    action: str
    direction: str
    hosts: str
    ports: str
    ip_version: str

    def __init__(self, *args, protocol: str, action: str,
                 direction: str, ip_version: str, **kwargs):
        assert protocol in (None, 'TCP', 'UDP', 'ANY')
        assert action in (None, 'ACCEPT', 'DROP', 'REJECT')
        assert direction in (None, 'IN', 'OUT')
        assert ip_version in (None, '4', '6', 'ANY')
        super().__init__(*args, protocol=protocol, action=action,
                         direction=direction, ip_version=ip_version, **kwargs)


class FTPUser(Resource):
    """FTP user.
    https://api.alwaysdata.com/v1/ftp/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        name: The name must begin by the account name followed by an
            underscore.
        password: Password.
        path: This directory is relative to the root directory of your
            account. Parent directories in the root directory will not
            be accessible or visible.
    """
    id: int
    href: str = '/v1/ftp/'
    name: str
    password: str
    path: str


class IPAddress(Resource):
    """IP address.
    https://api.alwaysdata.com/v1/ip/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        ip: IP.
        version: Version.
        reverse_dns: Reverse DNS. For example: www.example.org. Leave
            empty for a reverse DNS by default.
        use_smtp_for_ratings: Sending emails will be made with this IP
            for the checked spam scores. Possible choices: 0..4.
        role: Protocols using the IP address. Possible choices: `http`,
            `smtpout`.
    """
    id: int
    href: str = '/v1/ip/'
    ip: str
    version: int
    reverse_dns: str
    use_smtp_for_ratings: Sequence[int]
    role: str


class Mailbox(Resource):
    """Mailbox.
    https://api.alwaysdata.com/v1/mailbox/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        domain: Domain.
        name: Enter the part of the email address before the @ sign. For
            instance: john.smith. If you want to create a catch-all
            address, enter * (star).
        password: Password.
        antispam_enabled: Enable anti-spam.
        antispam_score: The anti-spam computes a score for each message
            based on the probability of being a spam. Messages over this
            score will be stored in the folder below. Unless you know
            what you are doing, don't change the default value (5).
        antispam_folder: Spams will be moved to this folder.
        antispam_score_delete: Messages exceeding this score will be
            directly deleted, without even being stored in the spam
            folder.
        antivirus_enabled: Enable antivirus.
        antivirus_folder: Viruses will be moved to this folder.
        purge_enabled: Enable purge.
        purge_days: Messages will be deleted after that period.
        purge_folders: List of folders to purge. To indicate multiple
            folders, separate them by spaces.
        redirect_enabled: Enable redirect.
        redirect_to: Enter addresses where emails will be redirected.
            Separate each address by a space.
        redirect_local_copy: If you check that box, all redirected
            messages will also be copied in that mailbox. Otherwise,
            messages will not be stored in your account, only
            redirected.
        autoresponder_enabled: Enable autoresponder.
        autoresponder_days: Only one automatic message per address will
            be sent for the selected period of time (in days).
        autoresponder_subject: Subject.
        autoresponder_message: Message.
        quota_enabled: Enable quota.
        quota_storage: Maximum size (in MB).
        sieve_enabled: If the Sieve script is enabled, it will be
            executed after the operations above (antispam, redirect,
            etc.)
        sieve_filter: Sieve format script executed at the e-mails
            reception.
    """
    id: int
    href: str = '/v1/mailbox/'
    domain: int
    name: str
    password: str
    antispam_enabled: bool
    antispam_score: int
    antispam_folder: str
    antispam_score_delete: int
    antivirus_enabled: bool
    antivirus_folder: str
    purge_enabled: bool
    purge_days: int
    purge_folders: str
    redirect_enabled: bool
    redirect_to: str
    redirect_local_copy: bool
    autoresponder_enabled: bool
    autoresponder_days: int
    autoresponder_subject: str
    autoresponder_message: str
    quota_enabled: bool
    quota_storage: int
    sieve_enabled: bool
    sieve_filter: str


class MailboxRule(Resource):
    """Mailbox rule.
    https://api.alwaysdata.com/v1/mailbox/rule/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        mailbox: Email address.
        target: The condition will apply on this field. Possible
            choices: `SUBJECT`, `FROM`, `TO`, `CC`, `BCC`, `REPLY_TO`,
            `BODY`, `SIZE`.
        condition: Some conditions apply only to certain fields. For
            example, OVER and UNDER apply only to the size.
            Possible values: `CONTAINS`, `CONTAINS_NOT`, `IS`, `IS_NOT`,
                `MATCHES` (matches the regular expression),
                `MATCHES_NOT`, `OVER` (greater than), `UNDER`.
        condition_value: Condition value.
        action: If the condition matches, this action will be executed
            on the message. Possible choices: `FILEINTO` (move in the
            folder), `REDIRECT` (redirect to address), `DISCARD`
            (delete), `REJECT` (reject with a message).
        action_value: Action value.
    """
    id: int
    href: str = '/v1/mailbox/rule/'
    mailbox: int
    target: str
    condition: str
    condition_value: str
    action: str
    action_value: str

    def __init__(self, *args, target: str, condition: str,
                 action: str, **kwargs) -> None:
        assert target in (None, 'SUBJECT', 'FROM', 'TO', 'CC', 'BCC',
                          'REPLY_TO', 'BODY', 'SIZE')
        assert condition in (None, 'CONTAINS', 'CONTAINS_NOT', 'IS', 'IS_NOT',
                             'MATCHES', 'MATCHES_NOT', 'OVER', 'UNDER')
        assert action in (None, 'FILEINTO', 'REDIRECT', 'DISCARD', 'REJECT')
        super().__init__(*args, target=target, condition=condition,
                         action=action, **kwargs)


class ObjectTransfer(Resource):
    """Object transfer.
    https://api.alwaysdata.com/v1/object_transfer/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        type: Transfer an `account`, `domain` or `site`.
    """
    id: int
    href: str = '/v1/object_transfer/'
    type: str

    def __init__(self, *args, type: str, **kwargs) -> None:
        assert type in (None, 'account', 'domain', 'site')
        super().__init__(*args, type=type, **kwargs)


class PHPEnvironment(Resource):
    """PHP environment.
    https://api.alwaysdata.com/v1/environment/php/doc/

    Attributes:
        href: Resource location.
        php_version: PHP version.
        php_ini: Custom php.ini.
    """
    href: str = '/v1/environment/php/'
    php_version: str
    php_ini: str


class Product(Resource):
    """Product.
    https://api.alwaysdata.com/v1/product/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        name: Name.
        verbose_name: Name displayed.
    """
    id: int
    href: str = '/v1/product/'
    name: str
    verbose_name: str


class PythonEnvironment(Resource):
    """Python environment.
    https://api.alwaysdata.com/v1/environment/python/doc/

    Attributes:
        href: Resource location.
        python_version: Python version.
    """
    href: str = '/v1/environment/python/'
    python_version: str


class RubyEnvironment(Resource):
    """Ruby environment.
    https://api.alwaysdata.com/v1/environment/ruby/doc/

    Attributes:
        href: Resource location.
        ruby_version: Ruby version.
    """
    href: str = '/v1/environment/ruby/'
    ruby_version: str


class Server(Resource):
    """Server.
    https://api.alwaysdata.com/v1/server/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        name: Name.
        datacenter: Datacenter.
    """
    id: int
    href: str = '/v1/server/'
    name: str
    datacenter: int


class Site(Resource):
    """Site.
    https://api.alwaysdata.com/v1/site/doc/

    `elixir_version`, `nodejs_version`, etc. have been replaced for the
    constant literal `language_version`. To know which language the
    version refers to, find it in `site.type`.

    Attributes:
        id: Resource ID.
        href: Resource location.
        name: The name is only for information purposes and is only used
            for display.
        type: Select the type of your application. Possible values:
            `apache_custom`, `elixir`, `nodejs`, `php`, `redirect`,
            `ruby_on_rails`, `ruby_rack`, `static`, `user_program`,
            `wsgi`.
        ssl_force: All HTTP requests will be automatically redirected to
            HTTPS.
        max_idle_time: Idle time before your application is stopped (in
            seconds).
        path_trim: If you have addresses containing a path, it will be
            trimmed from the request forwarded to your application.
        addresses: List of addresses for the website.

        global_directives: Directives that will be inserted at the
            global level of the Apache configuration.
        vhost_directives: Directives that will be included in the
            virtual host configuration.

        language_version: Elixir / Nodejs / PHP / ... version.
        command: Program command, you can specify arguments. This
            command should start a HTTP server listening on 0.0.0.0 and
            the port 8100 (available on the environment variable POST).
            For example: `node ~/myapp/index.js`
        path: The path is relative to the root of your account and must
            begin with "/". For example `/www/`.
        working_directory: Work directory path. If the path does not
            start with "/", it is relative to the root of your account.
        environment: Environment variables, format: FOO=bar LOREM=ipsum.

        url: Destination URL.
        redirect_type: Forwarding type. Possible values: `PERMANENT`
            (301), `TEMPORARY` (302), `TRANSPARENT` (reverse proxy).
        append_path: Check this box if you want the HTTP request path to
            be appended to the destination URL.

        bundler: Starts the application in the Gemfile defined
            environment.
        static_paths: Path to static files in the format:
            `url_path=file_path [...]`.

    Methods:
        restart: Restarts the website.
    """
    id: int
    href: str = '/v1/site/'
    name: str
    type: str
    ssl_force: bool
    max_idle_time: int
    path_trim: bool
    addresses: Sequence[str]
    # Apache custom.
    global_directives: str
    vhost_directives: str
    # Elixir, Nodejs, PHP, Ruby on Rails, Ruby Rack, User program, WSGI.
    language_version: str
    command: str
    path: str    # Also for static site.
    working_directory: str
    environment: str
    # PHP.
    php_ini: str
    # Redirect.
    url: str
    redirect_type: str
    append_path: bool
    # Ruby on Rails / Ruby Rack.
    bundler: bool
    static_paths: str    # Also for WSGI.
    # WSGI.
    virtualenv_directory: str

    def __init__(self, *args, language_version: str = None,
                 elixir_version: str = None, nodejs_version: str = None,
                 php_version: str = None, ruby_version: str = None,
                 python_version: str = None, redirect_type: str = None,
                 **kwargs: Union[str, bool, int, Sequence[str]]) -> None:
        assert redirect_type in (None, 'PERMANENT', 'TEMPORARY', 'TRANSPARENT')
        language_version = (language_version or elixir_version or
                            nodejs_version or php_version or ruby_version or
                            python_version)
        super().__init__(*args, language_version=language_version,
                         redirect_type=redirect_type, **kwargs)

    def restart(self, auth: AuthBase = DEFAULT_AUTH) -> None:
        """Restarts the website.

        Args:
            auth: Optional authentication, when the default
                authentication is not available or different credentials
                should be used.

        Raises:
            `requests.HTTPError` upon failure.
            When no exception is raised we may assume the request was
            successful.
        """
        endpoint = self.href + 'restart/'
        self.request('POST', endpoint, auth=auth)


class SSHUser(Resource):
    """SSH user.
    https://api.alwaysdata.com/v1/ssh/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        name: The name must begin by the account name followed by an
            underscore.
        password: Password.
        home_directory: This directory is relative to your root
            directory. It has to start with "/". Warning: the user is
            not chrooted in that directory, he can move anywhere.
        shell: Shell. Possible values: `BASH`, `ZSH`, `KSH`, `CSH`,
            `TCSH`, `FISH`, `SFTP`.
        can_use_password: Enable password login.
    """
    id: int
    href: str = '/v1/ssh/'
    name: str
    password: str
    home_directory: str
    shell: str
    can_use_password: bool

    def __init__(self, *args, shell: str, **kwargs) -> None:
        """Creates a SSHUser instance.
        """
        assert shell in (None, 'BASH', 'ZSH', 'KSH', 'CSH', 'TCSH', 'FISH',
                         'SFTP')
        super().__init__(*args, shell=shell, **kwargs)


class SSLCertificate(Resource):
    """SSL certificate.
    https://api.alwaysdata.com/v1/ssl/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        certificate: Certificate.
        intermediate_certificates: Intermediate certificates.
        key: Key.
        date_expiration: Expiration date/
        name: Name.
    """
    id: int
    href: str = '/v1/ssl/'
    certificate: str
    intermediate_certificates: str
    key: str
    date_expiration: str
    name: str


class Subdomain(Resource):
    """Subdomain.
    https://api.alwaysdata.com/v1/subdomain/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        ip_addresses: IP addresses.
        ssl_certificate: If no certificate is explicitly defined
    the
            most appropriate certificate will automatically be used.
        hostname: Complete address.
    """
    id: int
    href: str = '/v1/subdomain/'
    ip_addresses: Sequence[int]
    ssl_certificate: int
    hostname: str


class Subscription(Resource):
    """Subscription.
    https://api.alwaysdata.com/v1/subscription/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        date_expiry: The account is paid up to that date. If the field
            is empty, it means that the client has not forwarded payment
            yet.
        product: The subscription applies to this product.
        period: Example: `1mo`, `3mo`, `6mo`, `1y`, etc.
        price: The subscription price.
        object: The subscription resulted from the creation of this
            object.
    """
    id: int
    href: str = '/v1/subscription/'
    date_expiry: str
    product: int
    period: str
    price: float
    object: int


class WebdavUser(Resource):
    """Webdav user.
    https://api.alwaysdata.com/v1/webdav/doc/

    Attributes:
        id: Resource ID.
        href: Resource location.
        name: The name must begin by the account name followed by an
            underscore.
        password: Password.
        path: Parent directories of the root directory will be neither
            accessible nor visible.
    """
    id: int
    href: str = '/v1/webdav/'
    name: str
    password: str
    path: str
