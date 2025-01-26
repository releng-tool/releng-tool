# SPDX-License-Identifier: BSD-2-Clause OR 0BSD
# Copyright releng-tool

# Implementation in this file is considered "API safe". There is a strong
# attempt to prevent the changing of the following classes, methods, etc. to
# prevent compatibility issues as both this tool and extensions (if any) evolve.

class RelengRegistryInterface:
    """
    interface of the registry passed into an extension's setup stage

    This is the public interface of the releng-tool's registry which outlines
    methods which can be invoked by an extension during the setup stage. When an
    extension defines "def releng_setup(app):" the ``app`` value will be an
    instance of this interface (``RelengRegistryInterface``). During the setup
    call, an extension may call any of the defined methods using their ``app``
    context.
    """

    def add_extract_type(self, name, handler):
        """
        register extraction support with a given name for this extension

        An extension will invoke this method when attempting to support a custom
        extraction method for a release engineering process. The extraction
        type is identified by the provided ``name`` value. Packages being
        processed with VCS type paired with a extension-defined fetch type or a
        package extraction override will be processed through the provided
        ``handler``.

        An extension must define a proper ``name`` for the extract-type:

         - The name is a string value.
         - The name must be prefixed with ``ext-``.
         - The name should be all lowercase.
         - The dash character ``-`` is the recommended separator.

        The ``handler`` must be compatible with the implementation defined in
        ``RelengExtractExtensionInterface``. There is no requirement that the
        handler needs to inherit this interface.

        Additional notes:

         - The releng-tool process may instantiation one or more of the provided
            handler types.
         - The first extension loaded with a custom extract-type will take
            precedence over other extensions.

        Args:
            name: the name of this extract type
            handler: the extract-type class handler

        Raises:
            RelengInvalidSetupException: raised when the provided ``name`` or
                ``handler`` values are not supported by the releng-tool process
        """

    def add_fetch_type(self, name, handler):
        """
        register fetch support with a given name for this extension

        An extension will invoke this method when attempting to support a custom
        fetch method for a release engineering process. The fetch type is
        identified by the provided ``name`` value. Packages being processed with
        a matching VCS type will be processed through the provided ``handler``.

        An extension must define a proper ``name`` for the fetch-type:

         - The name is a string value.
         - The name must be prefixed with ``ext-``.
         - The name should be all lowercase.
         - The dash character ``-`` is the recommended separator.

        The ``handler`` must be compatible with the implementation defined in
        ``RelengFetchExtensionInterface``. There is no requirement that the
        handler needs to inherit this interface.

        Additional notes:

         - The releng-tool process may instantiation one or more of the provided
            handler types.
         - The first extension loaded with a custom fetch-type will take
            precedence over other extensions.

        Args:
            name: the name of this fetch type
            handler: the fetch-type class handler

        Raises:
            RelengInvalidSetupException: raised when the provided ``name`` or
                ``handler`` values are not supported by the releng-tool process
        """

    def add_package_type(self, name, handler):
        """
        register package support with a given name for this extension

        An extension will invoke this method when attempting to support a custom
        package methods for a release engineering process. The package type is
        identified by the provided ``name`` value. Packages being processed with
        a matching type will be processed through the provided ``handler`` for
        each package stage (configuration, building, etc.).

        An extension must define a proper ``name`` for the package-type:

         - The name is a string value.
         - The name must be prefixed with ``ext-``.
         - The name should be all lowercase.
         - The dash character ``-`` is the recommended separator.

        The ``handler`` must be compatible with the implementation defined in
        ``RelengPackageExtensionInterface``. There is no requirement that the
        handler needs to inherit this interface.

        Additional notes:

         - The releng-tool process may instantiation one or more of the provided
            handler types.
         - The first extension loaded with a custom package-type will take
            precedence over other extensions.

        Args:
            name: the name of this package type
            handler: the package-type class handler

        Raises:
            RelengInvalidSetupException: raised when the provided ``name`` or
                ``handler`` values are not supported by the releng-tool process
        """

    def connect(self, name, handler, priority=100):
        """
        register a handler for a specific releng-tool event

        For the lifecycle of a releng-tool run, a series of events may be
        triggered. An extension will invoke this method when attempting to
        have a callback triggered when a given event occurs.

        An extension must provide a supported ``name`` for an event type:

         - ``config-loaded``: trigger after a configuration is processed
         - ``post-build-started``: triggered before a post-build event starts
         - ``post-build-finished``: triggered after a post-build event ends

        The ``handler`` shall be able to accept an ``env`` keyword argument,
        representing the active script environment for the given stage of a
        releng-tool process. An extension may attempt to override or inject
        changes to this environment. A priority value can be set to order when
        an extension is notified for a given even (over other extensions).

        Args:
            name: the name of the event to listen for
            handler: the event handler
            priority (optional): the priority of the event handler

        Returns:
            the identifier for this connect request

        Raises:
            RelengInvalidSetupException: raised when the provided ``name``,
                ``handler`` or ``priority`` values are not supported by
                the releng-tool process
        """

    def disconnect(self, listener_id):
        """
        unregister an event handler previously configured in releng-tool

        An extension may use ``connect`` to register for specific events that
        can be triggered in releng-tool. This call can be used to unregister
        a previously made registration request.

        Args:
            listener_id: the listener identifier to unregister
        """

    def require_version(self, version):
        """
        perform a required-version check

        Enables an extension to explicitly check for a required releng-tool
        version before being loaded. Invoking this method with a
        dotted-separated ``version`` string, the string will be parsed and
        compared with the running releng-tool version. If the required version
        is met, this method will have no effect. In the event that the required
        version is not met, the exception ``RelengVersionNotSupportedException``
        will be raised. The extension implementation does not need to explicitly
        handle this exception (as it is caught by the registry loading process).

        Args:
            version: dotted-separated version string

        Raises:
            RelengVersionNotSupportedException: raised when the required version
                for this extension is not met
        """


# ##############################################################################


class RelengPackageOptions:
    """
    releng package-type options

    Provides a series of options from the releng process into a package-type
    handler. A handler's ``configure``, ``build``, and ``install`` methods will
    be passed options to react on.

    Attributes:
        def_dir: the directory holder the package definition
        env: package's environment variables
        ext: extension (pass-through) options
        name: the name of the package being processed
        version: the version of the package
    """
    def __init__(self):
        self.def_dir = None
        self.env = None
        self.ext = {}
        self.name = None
        self.version = None


class RelengAssembledOptions(RelengPackageOptions):
    """
    releng assembled options

    Options that are common between the configuration, building and
    installation stages.

    Attributes:
        build_base_dir: directory container for all build content
        build_dir: directory for a package's buildable content
        build_output_dir: build output directory for the package process
        host_dir: directory container for host tools
        prefix: prefix for system root (if applicable)
        staging_dir: directory container for staged content
        symbols_dir: directory container for symbols content
        target_dir: directory container for target content
    """
    def __init__(self):
        super().__init__()
        self.build_base_dir = None
        self.build_dir = None
        self.build_output_dir = None
        self.host_dir = None
        self.prefix = None
        self.staging_dir = None
        self.symbols_dir = None
        self.target_dir = None


class RelengConfigureOptions(RelengAssembledOptions):
    """
    releng configure-type options

    Provides a series of options from the releng process into a configure-type
    handler. A handler's ``configuration`` method will be passed options to
    react on.

    Attributes:
        conf_defs: command line definitions to apply
        conf_env: environment variables to use
        conf_opts: command line options to apply
        install_type: installation type (host, staging, target or images)
        jobs: number of calculated jobs to allow at a given time
        jobsconf: number of jobs to allow at a given time (0: auto)
    """
    def __init__(self):
        super().__init__()
        self.conf_defs = None
        self.conf_env = None
        self.conf_opts = None
        self.install_type = None
        self.jobs = 1
        self.jobsconf = 0


class RelengBuildOptions(RelengAssembledOptions):
    """
    releng build-type options

    Provides a series of options from the releng process into a build-type
    handler. A handler's ``build`` method will be passed options to react on.

    Attributes:
        build_base_dir: directory container for all build content
        build_defs: command line definitions to apply
        build_opts: command line options to apply
        jobs: number of calculated jobs to allow at a given time
        jobsconf: number of jobs to allow at a given time (0: auto)
    """
    def __init__(self):
        super().__init__()
        self.build_base_dir = None
        self.build_defs = None
        self.build_opts = None
        self.jobs = 1
        self.jobsconf = 0


class RelengExtractOptions(RelengPackageOptions):
    """
    releng extract-type options

    Provides a series of options from the releng process into a extract-type
    handler. A handler's ``extract`` method will be passed options to react on.

    Attributes:
        cache_dir: directory to store cached content (if applicable)
        cache_file: file to store cached content (if applicable)
        revision: revision to use to fetch from source control
        strip_count: strip-count for package extraction (if applicable)
        work_dir: the working directory
    """
    def __init__(self):
        super().__init__()
        self.cache_dir = None
        self.cache_file = None
        self.revision = None
        self.strip_count = 1
        self.work_dir = None


class RelengFetchOptions(RelengPackageOptions):
    """
    releng fetch-type options

    Provides a series of options from the releng process into a fetch-type
    handler. A handler's ``fetch`` method will be passed options to react on.

    Attributes:
        cache_dir: directory to store cached content (if applicable)
        cache_file: file to store cached content (if applicable)
        fetch_opts: command line options to apply (if applicable)
        ignore_cache: whether or not there is a hint to ignore cache information
        revision: revision to use to fetch from source control
        site: the site (uri) to acquire a package's resources
    """
    def __init__(self):
        super().__init__()
        self.cache_dir = None
        self.cache_file = None
        self.fetch_opts = None
        self.ignore_cache = None
        self.revision = None
        self.site = None


class RelengInstallOptions(RelengAssembledOptions):
    """
    releng install-type options

    Provides a series of options from the releng process into a install-type
    handler. A handler's ``installation`` method will be passed options to react
    on.

    Attributes:
        cache_file: location to cache file (if applicable)
        dest_dirs: list of directories to install to
        images_dir: directory container for (final) images
        install_defs: command line definitions to apply
        install_env: environment variables to use
        install_opts: command line options to apply
        install_type: installation type
    """
    def __init__(self):
        super().__init__()
        self.cache_file = None
        self.dest_dirs = None
        self.images_dir = None
        self.install_defs = None
        self.install_env = None
        self.install_opts = None
        self.install_type = None


# ##############################################################################


class RelengExtensionInterface:
    """
    base interface type

    This is a base class for all releng-tool extension implementations.
    """


class RelengExtractExtensionInterface(RelengExtensionInterface):
    """
    interface to implement a custom extract-type

    Extensions wishing to define a custom extract type can implement this
    interface and register it (see ``add_extract_type``) during the extension's
    setup stage. This will allow an project support custom DVCS-types defined in
    package definitions (for example "<PKG>_VCS_TYPE='ext-myawesometype'").
    """

    def extract(self, name, opts):
        """
        handle a custom extract operation

        When a package attempts to be "extracted" and VCS-type is defined to the
        custom extraction name, this method will be invoked. Package information
        to perform the extraction is provided by the ``opts`` argument. The main
        goal of this operation is to populate the provided work or "build"
        directory (same as the working directory) based off the package's cache
        directory or file (which varies base don the package type). On
        completion, this method should return ``True`` to indicate a successful
        extraction. If an error occurs, this method should return ``False``. A
        failed extraction operation is not required to clean the work directory.

        The ``extract`` method may be called multiple times throughout the
        lifetime of a releng-tool process (i.e. once per project being
        extracted).

        Args:
            name: the name of this extraction type
            opts: the extract options (see ``RelengExtractOptions``)

        Returns:
            ``True`` on successful extraction; otherwise ``False``
        """
        return False


class RelengFetchExtensionInterface(RelengExtensionInterface):
    """
    interface to implement a custom fetch-type

    Extensions wishing to define a custom fetch type can implement this
    interface and register it (see ``add_fetch_type``) during the extension's
    setup stage. This will allow an project support custom VCS-types defined in
    package definitions (for example "<PKG>_VCS_TYPE='ext-myawesomefetchtype'").
    """

    def fetch(self, name, opts):
        """
        handle a custom fetch operation

        When a package attempts to be "fetched" and VCS-type is defined to the
        custom fetch name, this method will be invoked. Package information to
        perform the fetch on is provided by the ``opts`` argument. The main goal
        of this operation is to fetch content from a provided site into either
        a cache file or a cache directory. On completion, this method should
        return either the cache file or cache directory depending on which has
        been populated from the fetch operation. The returned catch value should
        match the same value provided in the fetch options: ``opts.cache_file``
        if the fetch operation populates a cached file or ``opts.cache_dir`` if
        the fetch operation populates a cache directory. If the fetch operation
        returns a ``None`, this is an indication that the fetch operation has
        failed. A failed fetch operation is not required to clean the work
        directory; however, it is the responsibility of the custom fetch type to
        manage the state of the ``cache_dir`` (if applicable) and other external
        resources it may managed.

        The ``fetch`` method may be called multiple times throughout the
        lifetime of a releng-tool process (i.e. once per project being fetched).

        Args:
            name: the name of this fetch type
            opts: the fetch options (see ``RelengFetchOptions``)

        Returns:
            ``True`` on successful fetch; otherwise ``False``
        """
        return False


class RelengPackageExtensionInterface(RelengExtensionInterface):
    """
    interface to implement a custom package-type

    Extensions wishing to define a custom package type can implement this
    interface and register it (see ``add_package_type``) during the extension's
    setup stage. This will allow an project support custom package types which
    have custom steps to perform for configuring, building and installation.
    """

    def build(self, name, opts):
        """
        handle a custom build operation

        When a package reaches the building stage and package-type is defined
        to the custom package-type name, this method will be invoked. Package
        information to perform the build on is provided by the ``opts``
        argument. The main goal of this operation is to complete the build stage
        of a specific package in the provided work directory (same as the
        working directory). On completion, this method should return ``True`` to
        indicate a successful build. If an error occurs, this method should
        return ``False``. A failed build operation is not required to clean the
        work directory; however, the implementation should (attempt) to support
        a build request on a package which may have previously failed (i.e.
        build options or sources may have been changed to result in a successful
        build).

        The ``build`` method may be called multiple times throughout the
        lifetime of a releng-tool process (i.e. once per project being built).

        Args:
            name: the name of this package type
            opts: the build options (see ``RelengPackageOptions``)

        Returns:
            ``True`` on a successful build; otherwise ``False``
        """
        return False

    def configure(self, name, opts):
        """
        handle a custom configure operation

        When a package reaches the configuration stage and package-type is
        defined to the custom package-type name, this method will be invoked.
        Package information to perform the configuration on is provided by the
        ``opts`` argument. The main goal of this operation is to complete the
        configuration stage of a specific package in the provided work directory
        (same as the working directory). On completion, this method should
        return ``True`` to indicate a successful configuration. If an error
        occurs, this method should return ``False``. A failed configuration
        operation is not required to clean the work directory; however, the
        implementation should (attempt) to support a configuration request on a
        package which may have previously failed (i.e. configuration options or
        sources may have been changed to result in a successful configuration).

        The ``configure`` method may be called multiple times throughout the
        lifetime of a releng-tool process (i.e. once per project being
        configured).

        Args:
            name: the name of this package type
            opts: the configuration options (see ``RelengPackageOptions``)

        Returns:
            ``True`` on a successful configuration; otherwise ``False``
        """
        return False

    def install(self, name, opts):
        """
        handle a custom install operation

        When a package reaches the installation stage and package-type is
        defined to the custom package-type name, this method will be invoked.
        Package information to perform the installation on is provided by the
        ``opts`` argument. The main goal of this operation is to complete the
        install stage of a specific package in the provided work directory
        (same as the working directory). On completion, this method should
        return ``True`` to indicate a successful installation. If an error
        occurs, this method should return ``False``. A failed install operation
        is not required to clean the work directory; however, the implementation
        should (attempt) to support an install request on a package which may
        have previously failed (i.e. install options or sources may have been
        changed to result in a successful installation).

        The ``install`` method may be called multiple times throughout the
        lifetime of a releng-tool process (i.e. once per project being
        installed).

        Args:
            name: the name of this package type
            opts: the install options (see ``RelengPackageOptions``)

        Returns:
            `True`` on a successful installation; otherwise ``False``
        """
        return False


# ##############################################################################


class RelengInvalidSetupException(Exception):
    """
    exception raised when a loading extension has a setup issue
    """


class RelengVersionNotSupportedException(Exception):
    """
    exception raised when an extension does not support the releng-tool version
    """
